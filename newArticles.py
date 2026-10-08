
#!/usr/bin/env python3
"""
List newly created Wikipedia articles that are linked to a Wikidata item
whose instance of (P31) includes Q5 (human).

Improvements:
- Proper identifiable User-Agent (mandatory for Wikimedia APIs).
- Persistent Session with headers.
- Exponential backoff for transient errors (429/5xx).
- Better diagnostics for 403.
- Option to use the Wikimedia API gateway instead of per-wiki endpoints.

Usage examples:
  python new_human_articles.py --lang en --hours 24 --limit 100
  python new_human_articles.py --lang fr --since 2025-12-12T00:00:00Z --until 2025-12-13T00:00:00Z
  python new_human_articles.py --lang en --hours 6 --csv out.csv --json out.json
  python new_human_articles.py --lang en --use-gateway
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests

# ⚠️ IMPORTANT: Set a meaningful User-Agent with contact info.
USER_AGENT = "YourToolName/1.0 (https://your-site-or-github; your-email@example.com)"

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
DEFAULT_LIMIT = 200
MAX_RCLIMIT = 500
PAGEPROP_BATCH = 50
WD_ENTITY_BATCH = 50
HUMAN_QID = "Q5"

# Backoff settings
MAX_RETRIES = 5
INITIAL_WAIT = 0.5
BACKOFF_FACTOR = 2.0


def build_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    return s


def wiki_api_base(lang: str, use_gateway: bool) -> str:
    """
    Return MediaWiki API endpoint.
    - Per-wiki: https://{lang}.wikipedia.org/w/api.php
    - Wikimedia API gateway (supports many projects): https://api.wikimedia.org/core/v1/wikipedia/{lang}/...
      Note: The gateway has different paths for some features, so we keep action API default unless needed.
    """
    if use_gateway:
        # Use gateway for recentchanges via action API proxy:
        # Gateway supports action API at: https://api.wikimedia.org/w/api.php?project={lang}wiki
        # This keeps parameters compatible with action=query.
        return "https://api.wikimedia.org/w/api.php"
    return f"https://{lang}.wikipedia.org/w/api.php"


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def chunked(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]


def safe_get(session: requests.Session, url: str, params: Dict, desc: str) -> Dict:
    """
    GET with retries and backoff for 429/5xx; raise for others.
    """
    wait = INITIAL_WAIT
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=30)
            # Handle rate limiting or server errors with retry
            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt < MAX_RETRIES:
                    time.sleep(wait)
                    wait *= BACKOFF_FACTOR
                    continue
            # For 403, surface a helpful hint
            if resp.status_code == 403:
                msg = (
                    f"403 Forbidden while {desc}. Tip: set a meaningful User-Agent; "
                    f"check corporate proxies/VPN, and ensure parameters are valid. "
                    f"URL: {resp.url}"
                )
                resp.raise_for_status()  # will raise HTTPError
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            # Non-retriable or final attempt
            raise
        except requests.RequestException as e:
            # Network issue; retry if possible
            if attempt < MAX_RETRIES:
                time.sleep(wait)
                wait *= BACKOFF_FACTOR
                continue
            raise
    # Should not reach here
    raise RuntimeError(f"Failed {desc} after retries")


def fetch_recent_new_pages(
    session: requests.Session,
    lang: str,
    start_iso: str,
    end_iso: str,
    max_pages: int,
    use_gateway: bool
) -> List[Dict]:
    """
    Fetch recent 'new' articles in main namespace (0), excluding redirects.
    """
    api = wiki_api_base(lang, use_gateway)
    results = []
    rccontinue = None

    while True:
        remaining = max_pages - len(results)
        if remaining <= 0:
            break
        rclimit = min(MAX_RCLIMIT, remaining)

        params = {
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|ids|timestamp|redirect",
            "rcnamespace": 0,
            "rctype": "new",
            "rcshow": "!redirect",
            "rcstart": start_iso,  # older start
            "rcend": end_iso,      # newer end
            "rcdir": "newer",      # move forward in time
            "rclimit": rclimit,
            "format": "json",
            "formatversion": 2,
        }
        # For gateway, you must pass project param to route to the right wiki.
        if use_gateway:
            params["project"] = f"{lang}wiki"

        if rccontinue:
            params["rccontinue"] = rccontinue

        data = safe_get(session, api, params, desc="fetching recentchanges")
        rc = data.get("query", {}).get("recentchanges", [])
        if not rc:
            break

        for entry in rc:
            if entry.get("type") == "new" and entry.get("ns") == 0 and not entry.get("redirect"):
                results.append({
                    "pageid": entry.get("pageid"),
                    "title": entry.get("title"),
                    "timestamp": entry.get("timestamp"),
                    "revid": entry.get("revid"),
                })

        cont = data.get("continue", {})
        rccontinue = cont.get("rccontinue")
        if not rccontinue:
            break

        time.sleep(0.1)

    return results


def fetch_wikibase_items_for_pages(
    session: requests.Session,
    lang: str,
    pageids: List[int],
    use_gateway: bool
) -> Dict[int, Optional[str]]:
    """
    Get wikibase_item (Wikidata QID) via pageprops for given page IDs.
    """
    api = wiki_api_base(lang, use_gateway)
    mapping = {}
    for batch in chunked(pageids, PAGEPROP_BATCH):
        params = {
            "action": "query",
            "prop": "pageprops",
            "pageids": "|".join(str(pid) for pid in batch),
            "format": "json",
            "formatversion": 2,
        }
        if use_gateway:
            params["project"] = f"{lang}wiki"

        data = safe_get(session, api, params, desc="fetching pageprops")
        pages = data.get("query", {}).get("pages", [])
        for page in pages:
            pid = page.get("pageid")
            pp = page.get("pageprops", {}) or {}
            qid = pp.get("wikibase_item")
            mapping[pid] = qid if isinstance(qid, str) else None

        time.sleep(0.05)

    return mapping


def fetch_wikidata_entities(session: requests.Session, qids: List[str], label_lang: str = "ary") -> Dict[str, Dict]:
    """
    Batch fetch Wikidata entities (claims + labels).
    """
    results = {}
    for batch in chunked(qids, WD_ENTITY_BATCH):
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "claims|labels",
            "languages": label_lang,
            "format": "json",
        }
        data = safe_get(session, WIKIDATA_API, params, desc="fetching Wikidata entities")
        entities = data.get("entities", {})
        for qid, ent in entities.items():
            results[qid] = ent
        time.sleep(0.05)
    return results


def is_human_entity(entity: Dict) -> bool:
    claims = entity.get("claims", {})
    p31 = claims.get("P31", [])
    for claim in p31:
        mainsnak = claim.get("mainsnak", {})
        datavalue = mainsnak.get("datavalue", {})
        value = datavalue.get("value", {})
        if isinstance(value, dict) and value.get("id") == HUMAN_QID:
            return True
    return False


def label_for_entity(entity: Dict, lang: str) -> Optional[str]:
    labels = entity.get("labels", {})
    if lang in labels:
        return labels[lang].get("value")
    if labels:
        return next(iter(labels.values())).get("value")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Show newly created Wikipedia articles linked to Wikidata humans (P31=Q5)."
    )
    parser.add_argument("--lang", default="ary", help="Wikipedia language code (e.g., en, fr, de). Default: ary")
    parser.add_argument("--hours", type=int, default=24,
                        help="Look back this many hours from now (UTC). Ignored if --since is provided. Default: 24")
    parser.add_argument("--since", help="ISO8601 UTC start (e.g., 2021-12-12T00:00:00Z). Overrides --hours.")
    parser.add_argument("--until", help="ISO8601 UTC end (default: now UTC).")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                        help=f"Max pages to inspect (paginated via rccontinue). Default: {DEFAULT_LIMIT}")
    parser.add_argument("--label-lang", default="ary", help="Preferred label language for Wikidata. Default: en")
    parser.add_argument("--csv", help="Optional: path to write CSV output.")
    parser.add_argument("--json", help="Optional: path to write JSON output.")
    parser.add_argument("--use-gateway", action="store_true",
                        help="Use https://api.wikimedia.org/w/api.php with ?project={lang}wiki")
    args = parser.parse_args()
    now_utc = datetime.now(timezone.utc)
    if args.since:
        start = args.since
    else:
        start_dt = now_utc - timedelta(hours=args.hours)
        start = iso_utc(start_dt)
    end = args.until if args.until else iso_utc(now_utc)

    session = build_session()

    # 1) Get new pages
    try:
        new_pages = fetch_recent_new_pages(session, args.lang, start, end, args.limit, args.use_gateway)
    except requests.HTTPError as e:
        print(f"Error fetching recent changes: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error while fetching recent changes: {e}", file=sys.stderr)
        sys.exit(1)

    if not new_pages:
        print(f"No new articles found between {start} and {end} on {args.lang}.wikipedia.org.")
        return

    # 2) Map to Wikidata items via pageprops
    pageids = [p["pageid"] for p in new_pages if p.get("pageid")]
    item_map = fetch_wikibase_items_for_pages(session, args.lang, pageids, args.use_gateway)

    # 3) Fetch Wikidata entities
    qids = sorted({qid for qid in item_map.values() if qid})
    if qids:
        entities = fetch_wikidata_entities(session, qids, label_lang=args.label_lang)
    else:
        entities = {}

    # 4) Filter to humans
    human_qids = {qid for qid, ent in entities.items() if is_human_entity(ent)}
    human_pages = []
    for p in new_pages:
        qid = item_map.get(p["pageid"])
        if qid and qid in human_qids:
            ent = entities.get(qid, {})
            label = label_for_entity(ent, args.label_lang)
            human_pages.append({
                "lang": args.lang,
                "title": p["title"],
                "pageid": p["pageid"],
                "timestamp": p["timestamp"],
                "wikidata_qid": qid,
                "wikidata_label": label,
            })

    # 5) Output
    if not human_pages:
        print(f"No newly created articles linked to human items (P31=Q5) found for {args.lang} between {start} and {end}.")
        return

    print(f"Found {len(human_pages)} newly created articles linked to humans (P31=Q5) on {args.lang}.wikipedia.org")
    for row in human_pages:
        print(
            f"- {row['title']} (pageid={row['pageid']}, "
            f"time={row['timestamp']}, QID={row['wikidata_qid']}, label={row['wikidata_label']})"
        )

    # Optional CSV
    if args.csv:
        fieldnames = ["lang", "title", "pageid", "timestamp", "wikidata_qid", "wikidata_label"]
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(human_pages)
        print(f"CSV written to: {args.csv}")

    # Optional JSON
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(human_pages, f, ensure_ascii=False, indent=2)
        print(f"JSON written to: {args.json}")


if __name__ == "__main__":
    main()
