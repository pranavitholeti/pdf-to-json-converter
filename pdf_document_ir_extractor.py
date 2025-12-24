import pdfplumber
import json
import os
import re

PDF_PATH = "sample.pdf"
OUTPUT_FILE = "hces_canonical_output.json"

def normalize_checkboxes(rows, section_id):
    if section_id not in ["4.1.2", "4.1.3"]:
        return None

    items = []
    for row in rows:
        if len(row) >= 3 and row[1]:
            status = any(mark in str(row[2]) for mark in ["X", "1", "✔"])
            items.append({
                "item": row[1].strip(),
                "selected": status
            })
    return items


def extract_semantic_metadata(text):
    return {
        "question_no": re.search(r"Q?\d+\.\d+", text).group(0)
        if re.search(r"Q?\d+\.\d+", text) else None,
        "reference_period_days": (
            30 if "30 days" in text.lower()
            else 7 if "7 days" in text.lower()
            else None
        ),
        "units": re.findall(r"(kg|gm|litre|rupees|number)", text.lower()),
        "logic_indicators": [
            k for k in ["skip", "go to", "if yes", "applicable"]
            if k in text.lower()
        ]
    }


def resolve_header_hierarchy(table_rows):
    header_rows = []
    data_start_idx = 0

    for i, row in enumerate(table_rows):
        if any(
            cell and re.search(r"(Q?\d+(\.\d+)?|item\s*no)", str(cell), re.I)
            for cell in row
        ):
            data_start_idx = i
            break
        header_rows.append(row)

    if not header_rows:
        return [], 0

    col_count = max(len(r) for r in header_rows)
    paths = [[] for _ in range(col_count)]

    for row in header_rows:
        last_val = None
        for i in range(col_count):
            cell = row[i].strip() if (i < len(row) and row[i]) else None
            if cell:
                last_val = cell
            if last_val:
                paths[i].append(last_val)

    columns = []
    for p in paths:
        clean = []
        for x in p:
            if not clean or clean[-1] != x:
                clean.append(x)
        columns.append({
            "id": ".".join(clean).lower().replace(" ", "_"),
            "hierarchy": clean
        })

    return columns, data_start_idx


def build_cross_table_links(document_ir):
    links = []
    if "3" in document_ir["sections"] and "2" in document_ir["sections"]:
        links.append({
            "source": "Section 3 (Members)",
            "target": "Section 2 (Household Size)",
            "rule": "Number of member rows should match household size"
        })
    return links


def process_hces_pdf(path):
    document_ir = {
        "metadata": {
            "document_type": "LCES / HCQ / FDQ Survey",
            "year": "2023–24",
            "representation": "canonical_multi_layer_model",
            "limitations": [
                "No vision-based layout models",
                "Heuristic section detection",
                "No automatic questionnaire reconstruction"
            ]
        },
        "sections": {},
        "relationships": [],
        "diagnostics": {
            "merged_cells_detected": 0
        }
    }

    with pdfplumber.open(path) as pdf:
        current_section_id = "0"

        for page_index, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""

            section_match = re.search(
                r"SECTION\s*\[?(\d+(\.\d+)?)\]?",
                page_text,
                re.I
            )
            if section_match:
                current_section_id = section_match.group(1)

            if current_section_id not in document_ir["sections"]:
                document_ir["sections"][current_section_id] = {
                    "page": page_index,
                    "blocks": []
                }

            for line in page_text.split("\n"):
                semantics = extract_semantic_metadata(line)
                if semantics["logic_indicators"] or semantics["question_no"]:
                    document_ir["sections"][current_section_id]["blocks"].append({
                        "type": "instruction_or_metadata",
                        "text": line.strip(),
                        "semantics": semantics,
                        "provenance": {
                            "page": page_index,
                            "method": "pdfplumber.extract_text"
                        }
                    })

            for table in page.find_tables():
                raw = table.extract()
                if not raw:
                    continue

                columns, data_idx = resolve_header_hierarchy(raw)
                checkbox_group = normalize_checkboxes(
                    raw[data_idx:], current_section_id
                )

                block = {
                    "type": "checkbox_group" if checkbox_group else "data_table",
                    "bbox": table.bbox,
                    "columns": None if checkbox_group else columns,
                    "data": []
                }

                if checkbox_group:
                    block["data"] = checkbox_group
                else:
                    for row in raw[data_idx:]:
                        row_obj = {}
                        for i, cell in enumerate(row):
                            if cell is None:
                                document_ir["diagnostics"]["merged_cells_detected"] += 1
                                row_obj[columns[i]["id"]] = None
                            elif i < len(columns):
                                row_obj[columns[i]["id"]] = cell.strip()
                        block["data"].append(row_obj)

                document_ir["sections"][current_section_id]["blocks"].append(block)

    document_ir["relationships"] = build_cross_table_links(document_ir)
    return document_ir


if __name__ == "__main__":
    canonical_json = process_hces_pdf(PDF_PATH)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(canonical_json, f, indent=2, ensure_ascii=False)
    print("DONE — Canonical JSON generated successfully.")
