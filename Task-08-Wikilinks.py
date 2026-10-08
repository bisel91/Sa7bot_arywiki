#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
unify_wikilinks_ary.py

Script for ary.wikipedia.org (Moroccan Arabic / Darija Wikipedia).

Goals
-----
1. Unify wikilinks: when the same target page is linked multiple times in
   an article using different display text (e.g. [[مهرجان كان|كان]] and
   [[مهرجان كان|مهرجان كان]]), normalize all occurrences to a single,
   chosen display form (the most frequent one, or the bare target if no
   piping is needed).

2. Fix "position held / profession" bracket mistakes using WIKIDATA as the
   source of truth. The script loads the article's Wikidata item and reads
   P106 (occupation) and P39 (position held), fetching the Arabic (ar) or
   Moroccan Arabic (ary) labels for each. It then:
     - repairs malformed bracket/pipe syntax around profession/position
       links (stray spaces, colon-instead-of-pipe, empty pipe, doubled
       brackets), and
     - if the bracketed text inside is a profession/position term that
       does not match what Wikidata records for the subject, corrects it
       to the Wikidata label (target page + display text), e.g.:
         [[ كاتب]]              -> kept if "كاتب" is in Wikidata P106
         [[صحفي]] (typo/wrong)  -> [[صحافي]]   if Wikidata says صحافي
         [[كاتب :  روائي]]      -> [[كاتب|روائي]] (syntax fix, pipe form kept
                                    if both sides are valid Wikidata values)
         [[كاتب|]]              -> [[كاتب]]
         [[كاتب|كاتب]]          -> [[كاتب]]   (redundant pipe removed)

Requires a working pywikibot install with API access to wikidata.org.

Run with:
    python unify_wikilinks_ary.py -page:"PAGE_TITLE"
    python unify_wikilinks_ary.py -cat:"CATEGORY_NAME"
    python unify_wikilinks_ary.py -file:list.txt

Add -simulate to preview diffs without saving.
"""

import re
import collections
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import SingleSiteBot, ExistingPageBot

LINK_RE = re.compile(r'\[\[\s*([^\[\]\|#]+?)\s*(?:\|\s*([^\[\]]*?)\s*)?\]\]')

# Wikidata properties that describe a person's profession / position held.
PROFESSION_PROPS = ["P106"]   # occupation
POSITION_PROPS = ["P39"]      # position held

# Preferred label languages, in priority order, for the ary wiki.
LABEL_LANGS = ["ary", "ar"]

# Fallback static term list, used only if Wikidata lookup is unavailable
# (no Wikidata item, network error, property missing, etc.). This keeps
# basic bracket-syntax repair working even without Wikidata access.
PROFESSION_TERMS_FALLBACK = {
    "كاتب", "كاتبة", "روائي", "روائية", "شاعر", "شاعرة", "ممثل", "ممثلة",
    "مخرج", "مخرجة", "صحافي", "صحافية", "سياسي", "سياسية", "وزير", "وزيرة",
    "رئيس", "رئيسة", "لاعب", "لاعبة", "مغني", "مغنية", "فنان", "فنانة",
    "أستاذ", "أستاذة", "طبيب", "طبيبة", "محامي", "محامية", "مهندس",
    "مهندسة", "رسام", "رسامة", "موسيقي", "موسيقية", "منتج", "منتجة",
    "كاتب سيناريو", "ملحن", "ملحنة", "باحث", "باحثة", "أكاديمي", "أكاديمية",
}


def get_wikidata_profession_terms(page):
    """
    Given a pywikibot Page, fetch its associated Wikidata item and return
    the set of valid profession/position display labels (occupation P106
    + position held P39), preferring 'ary' labels then 'ar', falling back
    to the item's own labels in any language, then to sitelink page titles
    for the target wiki (useful when no label is set in ary/ar).

    Returns (terms_set, target_titles_map) where target_titles_map maps a
    display label -> the wiki page title it should link to (so [[target]]
    can be reconstructed correctly even if the label differs from the
    page title).
    """
    terms = set()
    target_for_label = {}

    try:
        item = page.data_item()
        item.get()
    except (pywikibot.exceptions.NoPageError,
            pywikibot.exceptions.NoWikibaseEntityError,
            AttributeError):
        return terms, target_for_label
    except Exception as e:
        pywikibot.warning(f"تعذر جلب عنصر ويكي‌ديتا لـ {page.title()}: {e}")
        return terms, target_for_label

    claims = item.claims or {}
    site = page.site

    for prop in PROFESSION_PROPS + POSITION_PROPS:
        for claim in claims.get(prop, []):
            target_item = claim.getTarget()
            if target_item is None:
                continue
            try:
                target_item.get()
            except Exception:
                continue

            label = None
            for lang in LABEL_LANGS:
                if lang in target_item.labels:
                    label = target_item.labels[lang]
                    break
            if label is None and target_item.labels:
                label = next(iter(target_item.labels.values()))
            if not label:
                continue

            terms.add(label)

            # Prefer the actual ary-wiki sitelink title as the link target,
            # if one exists; otherwise use the label itself as the target.
            page_title = label
            sitelinks = getattr(target_item, "sitelinks", {})
            dbname = site.dbName() if hasattr(site, "dbName") else None
            for key in (dbname, f"{site.lang}wiki"):
                if key and key in sitelinks:
                    page_title = sitelinks[key].title
                    break

            target_for_label[label] = page_title

    return terms, target_for_label


def clean_bracket_artifacts(text):
    """Repair malformed bracket/pipe patterns before structural link parsing."""
    # Collapse stray spaced brackets: "[ [" -> "[[", "] ]" -> "]]"
    text = re.sub(r'\[\s+\[', '[[', text)
    text = re.sub(r'\]\s+\]', ']]', text)

    # Normalize a lone "[" + "[" already adjacent but with internal junk
    text = re.sub(r'\[\[\s+', '[[', text)
    text = re.sub(r'\s+\]\]', ']]', text)

    # Replace a colon used instead of a pipe inside double brackets:
    # [[target : display]] -> [[target|display]]
    text = re.sub(
        r'\[\[\s*([^\[\]\|#:]+?)\s*:\s*([^\[\]]+?)\s*\]\]',
        r'[[\1|\2]]',
        text,
    )

    # Remove empty pipe: [[target|]] -> [[target]]
    text = re.sub(r'\[\[\s*([^\[\]\|#]+?)\s*\|\s*\]\]', r'[[\1]]', text)

    # Remove redundant pipe where target == display: [[X|X]] -> [[X]]
    def _dedupe(m):
        target, display = m.group(1).strip(), m.group(2).strip()
        if target == display:
            return f'[[{target}]]'
        return m.group(0)

    text = re.sub(
        r'\[\[\s*([^\[\]\|#]+?)\s*\|\s*([^\[\]]+?)\s*\]\]',
        _dedupe,
        text,
    )

    return text


def _closest_term(word, terms, max_distance=2):
    """Return the closest matching term from `terms` for `word` (simple
    Levenshtein), or None if nothing is within max_distance. Used to catch
    typos like 'صحفي' vs the Wikidata-correct 'صحافي'."""
    if not terms:
        return None
    if word in terms:
        return word

    def lev(a, b):
        if a == b:
            return 0
        prev = list(range(len(b) + 1))
        for i, ca in enumerate(a, 1):
            cur = [i] + [0] * len(b)
            for j, cb in enumerate(b, 1):
                cur[j] = min(
                    prev[j] + 1,
                    cur[j - 1] + 1,
                    prev[j - 1] + (ca != cb),
                )
            prev = cur
        return prev[-1]

    best, best_dist = None, max_distance + 1
    for term in terms:
        d = lev(word, term)
        if d < best_dist:
            best, best_dist = term, d
    return best if best_dist <= max_distance else None


def fix_profession_brackets(text, wikidata_terms=None, target_for_label=None):
    """
    Fix the common 'position held / profession' bracket mistake where the
    profession/position term inside a wikilink is malformed or wrong,
    correcting it against `wikidata_terms` (display labels pulled from the
    article's Wikidata item, P106 occupation / P39 position held) when
    available. Falls back to the static PROFESSION_TERMS_FALLBACK set
    otherwise (syntax repair only, no correction of wrong terms).

    Handles:
      - stray spaces / doubled brackets / colon-as-pipe (done upstream by
        clean_bracket_artifacts, but also normalized here defensively)
      - a profession word that is a near-miss typo of the correct
        Wikidata label -> corrected to the Wikidata label
      - two profession terms jammed in one target, e.g. [[كاتب وروائي]]
        -> split into two separate links if both sides are valid terms
    """
    terms = wikidata_terms if wikidata_terms else PROFESSION_TERMS_FALLBACK
    target_for_label = target_for_label or {}
    using_wikidata = bool(wikidata_terms)

    def _link_for(label):
        page_title = target_for_label.get(label, label)
        if page_title == label:
            return f'[[{label}]]'
        return f'[[{page_title}|{label}]]'

    def _fix(m):
        target = m.group(1).strip()
        display = m.group(2)
        display = display.strip() if display else None

        # Two profession terms jammed into a single target, e.g.
        # "[[كاتب وروائي]]" -> two separate correct links.
        if display is None and ' و' in target:
            parts = re.split(r'\s+و', target, maxsplit=1)
            if len(parts) == 2:
                left, right = parts[0].strip(), parts[1].strip()
                left_match = _closest_term(left, terms)
                right_match = _closest_term(right, terms)
                if left_match and right_match:
                    return f'{_link_for(left_match)} و{_link_for(right_match)}'

        target = re.sub(r'\s+', ' ', target)
        if display:
            display = re.sub(r'\s+', ' ', display)

        if display:
            # Piped link: validate target and display independently.
            # Don't collapse a deliberate [[target|display]] pair just
            # because display matches a Wikidata term — only correct
            # actual typos on each side.
            target_match = _closest_term(target, terms)
            display_match = _closest_term(display, terms)

            new_target = target_match if target_match else target
            new_display = display_match if display_match else display

            correct_page = target_for_label.get(new_target, new_target)
            if correct_page != new_display:
                return f'[[{correct_page}|{new_display}]]'
            return f'[[{new_display}]]'

        # Unpiped link: the shown text is the target itself.
        shown = target
        match = _closest_term(shown, terms)
        if match and match != shown:
            # Wrong/typo'd profession term -> correct it using Wikidata.
            return _link_for(match)

        if match and using_wikidata:
            # Correct term already; just make sure target page is right.
            correct_target = target_for_label.get(match, target)
            if correct_target != target:
                return f'[[{correct_target}|{match}]]' if correct_target != match else f'[[{match}]]'

        return f'[[{target}]]'

    return LINK_RE.sub(_fix, text)


def collect_link_targets(text):
    """Return Counter: target -> Counter of display forms used."""
    targets = collections.defaultdict(collections.Counter)
    for m in LINK_RE.finditer(text):
        target = m.group(1).strip()
        display = m.group(2).strip() if m.group(2) else target
        targets[target][display] += 1
    return targets


def unify_links(text):
    """
    For every distinct link target appearing more than once with varying
    display text, rewrite all occurrences to use the single most common
    display form for that target. If the most common display equals the
    target itself, emit a bare [[target]] (no pipe).
    """
    targets = collect_link_targets(text)

    canonical_display = {}
    for target, displays in targets.items():
        if len(displays) <= 1:
            continue  # already consistent
        best_display, _ = displays.most_common(1)[0]
        canonical_display[target] = best_display

    if not canonical_display:
        return text, {}

    def _replace(m):
        target = m.group(1).strip()
        display = m.group(2).strip() if m.group(2) else target
        if target in canonical_display:
            new_display = canonical_display[target]
            if new_display == target:
                return f'[[{target}]]'
            return f'[[{target}|{new_display}]]'
        return m.group(0)

    new_text = LINK_RE.sub(_replace, text)
    return new_text, canonical_display


def process_text(text, wikidata_terms=None, target_for_label=None):
    original = text
    text = clean_bracket_artifacts(text)
    text = fix_profession_brackets(text, wikidata_terms, target_for_label)
    text, unified = unify_links(text)
    changed = text != original
    return text, changed, unified


class UnifyWikilinksBot(ExistingPageBot, SingleSiteBot):
    use_redirects = False

    def __init__(self, summary=None, **kwargs):
        self.summary = summary or (
            "بوت: توحيد الروابط الداخلية وتصحيح الأقواس فـ المهنة/المنصب"
        )
        super().__init__(**kwargs)

    def treat_page(self):
        page = self.current_page
        old_text = page.text

        wikidata_terms, target_for_label = get_wikidata_profession_terms(page)
        if wikidata_terms:
            pywikibot.info(
                f"مهن/مناصب جايين من ويكي‌ديتا لـ {page.title()}: "
                f"{', '.join(sorted(wikidata_terms))}"
            )
        else:
            pywikibot.info(
                f"- ماكاينة شي مهنة/منصب فـ ويكي‌ديتا لـ {page.title()}، "
                f"غادي نستعمل غير تصحيح الصياغة."
            )

        new_text, changed, unified = process_text(
            old_text, wikidata_terms, target_for_label
        )

        if not changed:
            pywikibot.info(f"- ماشي بحال: {page.title()} (والو ما تبدل)")
            return

        pywikibot.info(f"تبدلو الروابط فـ: {page.title()}")
        for target, display in unified.items():
            pywikibot.info(f"  • [[{target}]] -> العرض الموحد: '{display}'")

        pywikibot.showDiff(old_text, new_text)
        page.text = new_text
        page.save(summary=self.summary, minor=True)


def main(*args):
    local_args = pywikibot.handle_args(args)
    gen_factory = pagegenerators.GeneratorFactory()

    summary = None
    for arg in gen_factory.handle_args(local_args):
        if arg.startswith('-summary:'):
            summary = arg.split(':', 1)[1]

    gen = gen_factory.getCombinedGenerator(preload=True)
    if not gen:
        pywikibot.bot.suggest_help(missing_generator=True)
        return

    bot = UnifyWikilinksBot(generator=gen, summary=summary)
    bot.run()


if __name__ == '__main__':
    main()