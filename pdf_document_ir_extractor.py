import pdfplumber
import json
import os
import re

PDF_PATH = "input/sample.pdf"
OUTPUT_FILE = "output/document_ir.json"
os.makedirs("output", exist_ok=True)

def detect_section(text):
    m = re.search(r"(section|block)\s+\d+(\.\d+)?", text.lower())
    return m.group(0) if m else None


def is_instruction(text):
    keywords = [
        "go to", "skip", "if yes", "if no",
        "only for", "applicable", "note",
        "to be filled", "otherwise"
    ]
    return any(k in text.lower() for k in keywords)


def extract_cross_refs(text):
    refs = re.findall(r"(section\s+\d+(\.\d+)?|item\s+\d+(\.\d+)?)", text.lower())
    return [r[0] for r in refs] if refs else None


def extract_units(text):
    units = []
    for u in ["kg", "gm", "litre", "rupees", "₹", "days", "months", "number"]:
        if u in text.lower():
            units.append(u)
    return units


def extract_question_number(text):
    m = re.search(r"\bQ?\d+\.\d+\b", text)
    return m.group(0) if m else None


def extract_reference_period(text):
    m = re.search(r"(\d+)\s*(day|days|month|months)", text.lower())
    if m:
        return {"value": int(m.group(1)), "unit": m.group(2)}
    return None


def extract_applicability(text):
    app = []
    if "rural only" in text.lower():
        app.append("rural")
    if "urban only" in text.lower():
        app.append("urban")
    return app if app else None


def interpret_checkbox(value):
    if value is None:
        return None
    v = value.strip().lower()
    if v in ["x", "✓", "✔", "yes"]:
        return True
    if v in ["", "no"]:
        return False
    return None


def extract_hierarchical_headers(table):
    header_rows = []
    for row in table:
        if any(cell and any(c.isdigit() for c in cell) for cell in row):
            break
        header_rows.append(row)

    if not header_rows:
        return [], 0

    cols = max(len(r) for r in header_rows)
    paths = [[] for _ in range(cols)]

    for row in header_rows:
        last = None
        for i in range(cols):
            cell = row[i] if i < len(row) else None
            if cell:
                last = cell.strip()
                paths[i].append(last)
            elif last:
                paths[i].append(last)

    clean = []
    for p in paths:
        out = []
        for x in p:
            if not out or out[-1] != x:
                out.append(x)
        clean.append(out)

    return clean, len(header_rows)


def build_provenance(page, bbox=None, method="pdfplumber"):
    return {
        "page": page,
        "bbox": bbox,
        "extraction_method": method,
        "confidence": None
    }

diagnostics = {
    "pages_with_no_tables": [],
    "tables_with_header_mismatch": []
}

document_ir = {
    "document_type": "LCES Questionnaire",
    "representation": "document-aware intermediate representation",
    "pages": [],
    "diagnostics": diagnostics
}

prev_header_signature = None


with pdfplumber.open(PDF_PATH) as pdf:

    current_section = None

    for page_no, page in enumerate(pdf.pages, start=1):

        page_text = page.extract_text() or ""

        sec = detect_section(page_text)
        if sec:
            current_section = sec

        page_obj = {
            "page_number": page_no,
            "section": current_section,
            "content": []
        }

       
        for line in page_text.split("\n"):
            if is_instruction(line):
                page_obj["content"].append({
                    "type": "instruction",
                    "text": line.strip(),
                    "units": extract_units(line),
                    "cross_references": extract_cross_refs(line),
                    "provenance": build_provenance(
                        page_no,
                        method="pdfplumber.extract_text"
                    )
                })


        tables = page.find_tables()
        if not tables:
            diagnostics["pages_with_no_tables"].append(page_no)

        for t_index, t in enumerate(tables, start=1):
            raw = t.extract()
            bbox = t.bbox

            headers, h_rows = extract_hierarchical_headers(raw)
            signature = tuple(tuple(h) for h in headers)

            is_continuation = signature == prev_header_signature
            prev_header_signature = signature

            columns = []
            for h in headers:
                columns.append({
                    "hierarchy": h,
                    "semantic_key": ".".join(
                        x.lower().replace(" ", "_") for x in h
                    ),
                    "units": extract_units(" ".join(h))
                })

            context_text = " ".join(" ".join(h) for h in headers)
            question_meta = {
                "question_number": extract_question_number(context_text),
                "reference_period": extract_reference_period(context_text),
                "applicability": extract_applicability(context_text)
            }

            table_obj = {
                "type": "table",
                "table_id": f"{current_section}_P{page_no}_T{t_index}",
                "is_continuation": is_continuation,
                "question_metadata": question_meta,
                "columns": columns,
                "rows": [],
                "provenance": build_provenance(
                    page_no,
                    bbox=bbox,
                    method="pdfplumber.find_tables"
                )
            }

            expected_cols = len(columns)

            for row in raw[h_rows:]:
                if len(row) != expected_cols:
                    diagnostics["tables_with_header_mismatch"].append({
                        "page": page_no,
                        "table": t_index,
                        "expected_cols": expected_cols,
                        "actual_cols": len(row)
                    })

                row_obj = {
                    "cells": [],
                    "warnings": []
                }

                for cell in row:
                    checkbox = interpret_checkbox(cell)
                    if cell is None:
                        row_obj["cells"].append(None)
                        row_obj["warnings"].append("merged_or_missing_cell")
                    elif checkbox is not None:
                        row_obj["cells"].append({
                            "raw": cell,
                            "checkbox": checkbox
                        })
                    else:
                        row_obj["cells"].append(cell.strip())

                table_obj["rows"].append(row_obj)

            page_obj["content"].append(table_obj)

        document_ir["pages"].append(page_obj)


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(document_ir, f, indent=2, ensure_ascii=False)

print("DONE — document-aware intermediate representation created")
