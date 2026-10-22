import json
import os
from typing import Optional
from pydantic import BaseModel, Field
import ollama

# 1. تحديث هيكل البيانات ليتطابق مع طلبك (مع الرموز المقابلة)
class PersonInfo(BaseModel):
    name: Optional[str] = Field(None, description="First name (P735)")
    lastname: Optional[str] = Field(None, description="Last name (P734)")
    sex: Optional[str] = Field(None, description="Sex or gender (P21)")
    country_of_citizenship: Optional[str] = Field(None, description="Country of citizenship (P27)")
    birth_date: Optional[str] = Field(None, description="Date of birth (P569)")
    birth_place: Optional[str] = Field(None, description="Place of birth (P19)")

class BirthdaysList(BaseModel):
    people: list[PersonInfo]

# 2. دالة الاستعلام عبر Ollama
def get_person_details_for_name(name_query: str, model_name: str = "qwen2.5:7b") -> dict:
    prompt = f"""
    For the historical or public figure '{name_query}', extract the following details precisely:
    - name (First name / P735)
    - lastname (Last name / P734)
    - sex (P21, e.g., Male/Female)
    - country_of_citizenship (P27, Country name)
    - birth_date (P569, YYYY-MM-DD format if possible)
    - birth_place (P19, City/Country)
    
    If ANY of these specific details are completely unknown or missing for this person, leave them as null.
    """
    
    response = ollama.chat(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a precise biographical data extraction assistant. Output strictly valid JSON adhering to the schema."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=BirthdaysList.model_json_schema(),
        options={
            "temperature": 0.0,
        }
    )
    return json.loads(response["message"]["content"])

# 3. المعالجة الرئيسية مع شرط تخطي البيانات التي تحتوي على null
def process_names_file(file_path = 'names.txt', output_file: str = "birthdays_results.json", model_name: str = "qwen2.5:7b"):
    if not os.path.exists(file_path):
        print(f"[!] File '{file_path}' not found. Please create it and add names.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[*] Found {len(names)} names to process.\n")
    all_results = []
    skipped_count = 0

    for index, name_query in enumerate(names, 1):
        print(f"[{index}/{len(names)}] Processing: {name_query}")
        try:
            response_data = get_person_details_for_name(name_query, model_name=model_name)
            
            # استخراج الكائن الشخصي من الاستجابة
            people_list = response_data.get("people", [])
            if not people_list:
                print(f"  └─ Skipped: No data returned.")
                skipped_count += 1
                continue
                
            person = people_list[0]
            
            # --- شرط التحقق: التأكد من عدم وجود أي قيمة فارغة (null) في الحقول الستة ---
            fields_to_check = [
                person.get("name"),
                person.get("lastname"),
                person.get("sex"),
                person.get("country_of_citizenship"),
                person.get("birth_date"),
                person.get("birth_place")
            ]
            
            # إذا كان أي حقل منها فارغاً أو None، نقوم بتخطي الشخص تماماً
            if any(field is None or str(field).strip() == "" for field in fields_to_check):
                print(f"  └─ ⚠️ Skipped: Some required fields are missing (null found).")
                skipped_count += 1
                continue

            # إذا كانت جميع البيانات متوفرة، نضيفها للقائمة النهائية
            all_results.append({
                "query_name": name_query,
                "status": "success",
                "data": person
            })
            print(f"  └─ ✔️ Successfully extracted complete data!")

        except Exception as e:
            print(f"  └─ Error for {name_query}: {e}")
            skipped_count += 1

    # حفظ النتائج النظيفة (التي ليس فيها null)
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(all_results, out, indent=2, ensure_ascii=False)

    print(f"\n[✓] Done! Saved {len(all_results)} complete records. Skipped {skipped_count} incomplete records.")

if __name__ == "__main__":
    process_names_file("names.txt", output_file="birthdays_results.json", model_name="qwen2.5:7b")