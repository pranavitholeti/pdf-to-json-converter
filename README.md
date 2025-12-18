# PDF to JSON Converter using Python

## 📌 Objective
The objective of this project is to extract tabular data from a PDF document and convert it into structured JSON format using Python.

---

## 🛠️ Technologies Used
- Python 3
- pdfplumber
- JSON

---

## 📁 Project Structure

```text
pdf-to-json-converter/
├── input/
│   └── sample.pdf
├── output/
│   ├── output.json
│   └── clean_output.json
├── pdf_data_to_json.py
├── clean_json.py
├── requirements.txt
└── README.md

## ▶️ How to Run
# Install required dependencies
pip install -r requirements.txt

# Convert PDF tables to raw JSON
python pdf_data_to_json.py

# (Optional) Clean the JSON output
python clean_json.py


