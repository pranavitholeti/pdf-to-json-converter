# 📄 PDF to JSON Converter using Python

This project focuses on extracting information from a  PDF and converting it into a structured JSON format.
While working with the PDF, it was observed that directly converting tables into rows causes several issues such as data loss, incorrect column mapping, and missing instructions. To avoid these problems, this project generates a document-aware intermediate JSON representation that preserves the structure and logic of the original PDF.

---

## ➥ OBJECTIVE

The objective of this project is to:

1. Extract tabular and non-tabular data from a PDF file

2. Preserve section context and question numbers

3. Capture instructions

4. Avoid silent data corruption caused by merged or missing cells

The final JSON output is designed to be reliable and suitable for further processing or validation.

---

## 🛠️ Technologies Used

### 1. Python 3

### 2. pdfplumber

### 3. JSON

---

## 📁 Project Structure

```text
pdf-to-json-converter/
├── input/
│   └── sample.pdf
├── output/
│   ├── output.json
├── pdf_document_ir_extractor.py
├── requirements.txt
└── README.md

```
## ⚙️ HOW DOES IT WORK ?

1.The PDF is scanned page by page to identify sections and preserve questionnaire context.

2. Instructional text such as skip rules and conditions is extracted separately as metadata.

3. Tables are processed conservatively to handle multi-row headers and merged cells without data loss.

4. Checkbox-based tables are converted into clear boolean values (true / false).

5. Known relationships between sections are explicitly recorded.

6. Diagnostic details like page numbers and merged cell counts are stored for validation.

---

## ▶️ HOW TO RUN THE PROJECT ?

### 1️⃣ Install required dependencies

pip install -r requirements.txt

### 2️⃣ Add the PDF File
Place the PDF file in the same directory as the script and name it:
sample.pdf

### 3️⃣ Run the script
python  pdf_document_ir_extractor.py

---

## 📄OUTPUT

### output/output.json

The output JSON contains:

1. Document metadata

2. Section-wise grouped content

3. Instruction blocks

4. Table data with preserved headers

5. Explicit relationships between sections

6. Diagnostic information

This structure makes it easier to understand the original questionnaire without referring back to the PDF.

---

## 🛠 Handling Common PDF Extraction Issues

1. This project handles several common PDF extraction challenges:

2. Repeated headers across pages

3. Multi-row and merged table headers

4. Checkbox-based questions

5. Instructions mixed with tabular data

The approach avoids silently incorrect mappings

---

## ⚠ Limitations

1. Vision-based layout models are not used

2. Section detection is heuristic

3. Full automatic questionnaire reconstruction is not attempted

These limitations are documented to keep the extraction safe and transparent.

---

## 📝 Conclusion

This project demonstrates a practical approach to extracting structured data from complex PDFs. The focus is on correctness and clarity rather than full automation. The generated JSON can be used as a reliable intermediate format for further analysis or processing.



