import json

path = "data/schemes.json"
with open(path, encoding="utf-8-sig") as f:
    schemes = json.load(f)

new = [
  {
    "id": "ap-post-matric-jnanabhumi",
    "name": "AP Post Matric Scholarship (Jnanabhumi)",
    "state": "AP",
    "category": "scholarship",
    "benefit": "Tuition fee reimbursement and maintenance support for polytechnic, ITI, degree and above courses",
    "eligibility": {"min_age": None, "max_age": None, "max_income": None,
                    "castes": ["SC", "ST", "BC", "OBC"], "occupations": ["student"], "gender": None},
    "documents": [
      {"name": "Aadhaar card", "where_to_get": "UIDAI / Aadhaar centre"},
      {"name": "Caste certificate", "where_to_get": "MeeSeva / Sachivalayam"},
      {"name": "Income certificate", "where_to_get": "MeeSeva / Sachivalayam"},
      {"name": "Previous class marksheet", "where_to_get": "Your school / college"},
      {"name": "Admission or bonafide certificate", "where_to_get": "Your college"},
      {"name": "Aadhaar-linked bank passbook", "where_to_get": "Your bank branch"}
    ],
    "deadline": None,
    "official_link": "https://jnanabhumi.ap.gov.in",
    "note": "For Andhra Pradesh residents. Income limits differ by category and change often. Check Jnanabhumi before applying."
  },
  {
    "id": "ts-post-matric-epass",
    "name": "Telangana Post Matric Scholarship (ePASS)",
    "state": "TS",
    "category": "scholarship",
    "benefit": "Tuition fee reimbursement and maintenance support for post-matric courses",
    "eligibility": {"min_age": None, "max_age": None, "max_income": None,
                    "castes": ["SC", "ST", "BC", "OBC"], "occupations": ["student"], "gender": None},
    "documents": [
      {"name": "Aadhaar card", "where_to_get": "UIDAI / Aadhaar centre"},
      {"name": "Caste certificate", "where_to_get": "MeeSeva"},
      {"name": "Income certificate", "where_to_get": "MeeSeva"},
      {"name": "SSC (10th) hall ticket", "where_to_get": "Your school / board"},
      {"name": "Bonafide certificate", "where_to_get": "Your college"},
      {"name": "Bank passbook", "where_to_get": "Your bank branch"}
    ],
    "deadline": None,
    "official_link": "https://telanganaepass.cgg.gov.in",
    "note": "For Telangana residents. Income limits differ by category and change often. Check ePASS before applying."
  }
]

ids = {s["id"] for s in schemes}
for s in new:
    if s["id"] not in ids:
        schemes.append(s)

with open(path, "w", encoding="utf-8") as f:
    json.dump(schemes, f, indent=2, ensure_ascii=False)
print(len(schemes), "schemes saved")
