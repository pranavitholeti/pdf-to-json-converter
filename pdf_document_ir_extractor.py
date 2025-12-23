import pdfplumber
import json
import os
import re

PDF_PATH = "input/sample.pdf"
OUTPUT_FILE = "output/document_ir.json"

os.makedirs("output", exist_ok=True)

def detect_section(text):
    match = re.search(r"(section|block)\s+\d+(\.\d+)?", text.lower())
    return match.group(0) if match else None

def is_instruction_line(text):
    keywords = [
        "go to", "skip to", "if yes", "if no",
        "instruction", "note", "to be filled",
        "applicable", "only for", "otherwise"
    ]
    return any(k in text.lower() for k in keywords)

def extract_units(text):
    units = []
    for u in ["kg", "gm", "litre", "₹", "rupees", "days", "months", "number"]:
        if u in text.lower():
            units.append(u)
    return units

document_ir = {
    "document_type": "LCES Questionnaire",
    "representation": "document-aware intermediate representation",
    "pages": []
}

with pdfplumber.open(PDF_PATH) as pdf:
    current_section = None

    for page_no, page in enumerate(pdf.pages, start=1):
        page_text = page.extract_text() or ""

        detected_section = detect_section(page_text)
        if detected_section:
            current_section = detected_section

        page_obj = {
            "page_number": page_no,
            "section": current_section,
            "content": []
        }

        for line in page_text.split("\n"):
            if is_instruction_line(line):
                page_obj["content"].append({
                    "type": "instruction",
                    "text": line.strip(),
                    "units": extract_units(line),
                    "provenance": {
                        "page": page_no,
                        "source": "page_text"
                    }
                })

        tables = page.extract_tables()

        for table_index, table in enumerate(tables, start=1):
            if not table or len(table) < 2:
                continue

            header_rows = table[:2]
            columns = []

            for h1, h2 in zip(header_rows[0], header_rows[1]):
                columns.append({
                    "parent_header": h1.strip() if h1 else None,
                    "child_header": h2.strip() if h2 else None,
                    "units": extract_units((h1 or "") + " " + (h2 or ""))
                })

            table_obj = {
                "type": "table",
                "table_id": f"{current_section or 'unknown'}_P{page_no}_T{table_index}",
                "columns": columns,
                "rows": []
            }

            for row in table[2:]:
                row_obj = {
                    "cells": [],
                    "warnings": []
                }

                for cell in row:
                    if cell is None:
                        row_obj["cells"].append(None)
                        row_obj["warnings"].append("merged_or_missing_cell")
                    else:
                        row_obj["cells"].append(cell.strip())

                table_obj["rows"].append(row_obj)

            page_obj["content"].append(table_obj)

        document_ir["pages"].append(page_obj)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(document_ir, f, indent=2, ensure_ascii=False)

print("DONE – document-aware IR created")
print(f"Total pages processed: {len(document_ir['pages'])}")
