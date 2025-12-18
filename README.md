# 📄 PDF to JSON Converter using Python

A Python project to extract tabular data from PDF files and convert it into structured JSON format.

---

## 🧠 Documentation Flow
**WHAT → HOW → RUN → OUTPUT → RESULT**

---

## ✅ WHAT (What does this project do?)

This project reads a PDF file containing tables and converts the tabular data into JSON format.  
The generated JSON can be easily used for data analysis, storage, or further processing.

---

## ⚙️ HOW (How does it work?)

1. The PDF file is opened using the **pdfplumber** library.
2. Each page of the PDF is scanned to detect tables.
3. Table headers are mapped to their corresponding row values.
4. Extracted data is stored in structured **JSON** format.
5. An optional cleaning script removes null values and unwanted fields.

---

## ▶️ RUN (How to run the project?)

### 1️⃣ Install required dependencies
```bash
pip install -r requirements.txt
