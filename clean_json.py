import json

with open("output/output.json", "r", encoding="utf-8") as f:
    data = json.load(f)

clean = []

for row in data:
    new_row = {}
    for k, v in row.items():
        if k not in ("page_no", "table_no") and v not in (None, "", " "):
            new_row[k] = v.replace("\n", " ").strip() if isinstance(v, str) else v
    if new_row:
        clean.append(new_row)

with open("output/clean_output.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, indent=2, ensure_ascii=False)

print("CLEAN JSON CREATED")
