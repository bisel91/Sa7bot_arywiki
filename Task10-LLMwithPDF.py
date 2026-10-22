import json
from pathlib import Path
from typing import Optional

import ollama
from pdf2image import convert_from_path
from pydantic import BaseModel, Field
from pypdf import PdfReader
import pytesseract


# ---------------------------------------------------------
# 1. Person-Centric Target Schema
# ---------------------------------------------------------
class PersonProfile(BaseModel):
    full_name: Optional[str] = Field(
        default=None, description="Full name of the person"
    )
    gender: Optional[str] = Field(
        default=None, description="Gender (e.g., Male, Female)"
    )
    country_of_citizenship: Optional[str] = Field(
        default=None, description="Country or nationality"
    )
    birth_date: Optional[str] = Field(
        default=None, description="Date of birth (e.g., YYYY-MM-DD or Year)"
    )
    death_date: Optional[str] = Field(
        default=None, description="Date of death if deceased, otherwise null"
    )
    is_deceased: Optional[bool] = Field(
        default=None, description="True if deceased, False if living"
    )
    birth_place: Optional[str] = Field(
        default=None, description="City, region, or country of birth"
    )
    number_of_children: Optional[int] = Field(
        default=None, description="Number of sons/daughters/children"
    )
    native_language: Optional[str] = Field(
        default=None, description="Native language or mother tongue"
    )
    profession: list[str] = Field(
        default_factory=list, description="Professions, occupations, or roles"
    )
    key_achievements: list[str] = Field(
        default_factory=list, description="Key achievements, works, or milestones"
    )
    summary: Optional[str] = Field(
        default=None, description="A 2-3 sentence overview of the biography"
    )


# ---------------------------------------------------------
# 2. Text Extraction: PyPDF with OCR Fallback
# ---------------------------------------------------------
def extract_pdf_content(pdf_path: Path) -> str:
    # Attempt 1: Standard PyPDF text extraction
    try:
        reader = PdfReader(str(pdf_path))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        if text.strip():
            print("  -> Extracted text using standard PDF reader.")
            return text
    except Exception:
        pass

    # Attempt 2: Tesseract OCR fallback
    print("  -> Scanned PDF detected. Running Tesseract OCR on pages...")
    images = convert_from_path(str(pdf_path), first_page=1, last_page=10)

    ocr_text = ""
    for idx, img in enumerate(images, start=1):
        # OCR supporting English, French, and Arabic
        page_text = pytesseract.image_to_string(img, lang="eng+fra+ara")
        ocr_text += f"\n--- Page {idx} ---\n" + page_text

    return ocr_text


# ---------------------------------------------------------
# 3. Main Processing Pipeline
# ---------------------------------------------------------
def main():
    script_dir = Path(__file__).parent.resolve()
    list_file = script_dir / "pdf" / "list.txt"
    output_file = script_dir / "extracted_pdf_data.json"
    model_name = "llama3.2"

    if not list_file.exists():
        print(f"Error: Target list file '{list_file}' does not exist.")
        return

    with open(list_file, "r", encoding="utf-8") as f:
        path_entries = [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

    print(f"Found {len(path_entries)} file path(s) in '{list_file}'.\n")
    results = []

    for idx, path_str in enumerate(path_entries, start=1):
        print(f"[{idx}/{len(path_entries)}] Processing: {path_str}")

        try:
            pdf_path = Path(path_str).expanduser().resolve()

            if not pdf_path.exists():
                print(f"  -> File not found: '{pdf_path}'\n")
                continue

            # Extract raw text or perform OCR
            text_data = extract_pdf_content(pdf_path)

            if not text_data.strip():
                print(f"  -> Failed to extract text from '{pdf_path.name}'.\n")
                continue

            # Prompt Ollama with person-focused extraction instructions
            prompt = (
                f"Extract personal and biographical details strictly according to the target JSON schema. "
                f"If a field is not mentioned in the text, leave it as null:\n\n"
                f"{text_data[:8000]}"
            )

            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                format=PersonProfile.model_json_schema(),
            )

            # Parse and validate response
            parsed = PersonProfile.model_validate_json(
                response.message.content
            ).model_dump()

            parsed["file_name"] = pdf_path.name
            parsed["absolute_path"] = str(pdf_path)
            results.append(parsed)

            print(f"  -> Successfully extracted profile for '{pdf_path.name}'\n")

        except Exception as e:
            print(f"  -> Error: {e}\n")

    if results:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"Done! Saved biographical profiles to '{output_file}'.")


if __name__ == "__main__":
    main()