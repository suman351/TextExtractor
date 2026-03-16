## TextExtractor – UPSC PDF Hindi/English Question OCR

This project extracts **Hindi (and optionally English) MCQ questions** from a scanned UPSC‑style PDF and saves them as clean text files.

Currently the main flow is:
- Convert the input PDF in `uploads/` to images.
- Run OCR on each page (Hindi on the left column, English on the right).
- Group question stem + statements + options `(a)…(d)` into single blocks.
- Save **only the Hindi questions** to `output/hindi_questions.txt`.

---

### 1. Prerequisites

- **Python**: 3.8+ installed and available as `python` / `py` on PATH.
- **Tesseract OCR (Windows)**:
  - Install from the official installer (e.g. `tesseract-ocr-w64-setup-*.exe`).
  - Make sure Hindi and English language data (`hin`, `eng`) are installed.
  - The code currently expects:
    - `C:\Program Files\Tesseract-OCR\tesseract.exe`
  - If your path is different, update:
    - `pytesseract.pytesseract.tesseract_cmd` in `app.py` (and `extractor/pdf_reader.py` if you use it).
- **Poppler for Windows**:
  - Download a recent Poppler build for Windows.
  - Extract it somewhere (you already have something like):
    - `C:\Users\suman\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin`
  - Ensure `POPPLER_PATH` in `app.py` points to that `bin` directory.

---

### 2. Install Python dependencies

From the project root (`E:\TextExtractor`):

```bash
# (Optional but recommended) create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

If you prefer installing directly instead of using `requirements.txt`:

```bash
pip install pdf2image pytesseract
```

---

### 3. Project structure (key files)

- `app.py`  
  Main entry point. Converts the uploaded PDF to images, runs OCR on both columns, parses questions, and saves the output.

- `extractor/pdf_reader.py`  
  Helper to OCR an entire PDF into text (not used in the current `app.py` flow, but available).

- `extractor/question_parser.py`  
  Contains the logic to:
  - Detect Hindi vs English text.
  - Split OCR output into question blocks.
  - Merge statement‑style questions with their options.
  - Trim each question to only include stem + options `(a)…(d)` and drop noise.

- `utils/csv_writer.py`  
  At the moment, only used to save **Hindi** questions to `output/hindi_questions.txt`.

- `uploads/`  
  Input folder. Place your scanned UPSC‑style PDF here, e.g. `uploads/2022 = PT = CSE.pdf`.

- `output/`  
  Auto‑created. Contains the extracted Hindi questions as text.

---

### 4. Running the extractor

1. Copy your target PDF into `uploads/` and make sure the filename in `app.py` matches, e.g.:

```python
PDF_PATH = "uploads/2022 = PT = CSE.pdf"
```

2. From the project root, run:

```bash
python app.py
```

3. On success you will see a message similar to:

```text
✅ Extraction complete: 100 Hindi questions saved to 'output/hindi_questions.txt'.
```

4. Open `output/hindi_questions.txt` to see the results. Each question has the format:

```text
--- Hindi Question 2 ---
2. भारतीय अर्थव्यवस्था के सन्दर्भ में, निम्नलिखित कथनों
पर विचार कीजिए :
1. ...
2. ...
3. ...
(a) ...
(b) ...
(c) ...
(d) ...
```

Only the question stem + options are kept; booklet codes, rough‑work footers and other noise are removed.

---

### 5. Common installation issues

- **`ModuleNotFoundError: No module named 'pdf2image'`**  
  Run:

  ```bash
  pip install pdf2image
  ```

- **`ModuleNotFoundError: No module named 'pytesseract'`**  
  Run:

  ```bash
  pip install pytesseract
  ```

- **Tesseract not found / wrong path**  
  - Verify Tesseract is installed.
  - Confirm the path in `app.py` (and `extractor/pdf_reader.py` if used) is correct:

    ```python
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    ```

---

### 6. Notes and limitations

- The input PDF is a **scan**, so the text quality depends on Tesseract OCR and the scan resolution; 100% character‑perfect extraction is not guaranteed.
- The parser is tuned for **UPSC Prelims style MCQs** (statements + options a/b/c/d). Very different layouts may need additional parsing rules.

