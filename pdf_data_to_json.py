import pdfplumber
import json

PDF_PATH = r"C:\pdf_data_to_json\input\sample.pdf.pdf"


OUTPUT_FILE = "output/output.json"

rows = []

with pdfplumber.open(PDF_PATH) as pdf:
    for page_no, page in enumerate(pdf.pages, start=1):

        tables = page.extract_tables()
        if not tables:
            continue

        for table_no, table in enumerate(tables, start=1):

            headers = table[0]

            for row in table[1:]:
                if not any(row):
                    continue

                record = {
                    "page_no": page_no,
                    "table_no": table_no
                }

                for i, header in enumerate(headers):
                    if header and i < len(row):
                        record[header.strip()] = (
                            row[i].strip() if row[i] else None
                        )

                rows.append(record)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)

print("DONE – JSON file created")
