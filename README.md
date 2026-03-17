---
title: TextExtractor
sdk: docker
app_port: 7860
---

## TextExtractor – UPSC PDF Hindi/English Question OCR

Extract **Hindi + English UPSC-style MCQ questions** from a *scanned* PDF and save them as clean text files:

- `output/hindi_questions.txt`
- `output/english_questions.txt`

Under the hood it:
- Converts PDF pages to images (Poppler)
- Runs OCR (PaddleOCR recommended, Tesseract optional/legacy)
- Parses each column independently and classifies questions as Hindi/English automatically
- Keeps only the **stem + options (a)–(d)** and drops common noise (rough work, booklet codes, etc.)

---

### Quick start (Windows / PowerShell)

1) Create venv + install dependencies:

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

CMD:

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
```

2) Install **Poppler** and set `POPPLER_PATH` (required for PDF → images):

```powershell
# Example (change to your actual poppler "Library\bin" path)
$env:POPPLER_PATH="C:\path\to\poppler\Library\bin"
```

3) (Recommended) Install **Tesseract** and set `TESSERACT_CMD` (used for legacy OCR and as a fallback):

```powershell
# Example (default install path)
$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
```

4) Run the UI (recommended):

```bash
streamlit run streamlit_app.py
```

Then upload a PDF → click **Upload & Extract** → download both text files from the page.

---

### Prerequisites

- **Python**: 3.10+ recommended (works with newer Python versions too, as long as dependencies install).
- **Poppler (required)**: needed by `pdf2image` to convert PDFs to images.
  - On Windows, download a Poppler build and locate the `Library\bin` directory.
  - You can provide it at runtime via `POPPLER_PATH` (see above) or by editing the default in `app.py`.
- **OCR engine**
  - **PaddleOCR (recommended)**: best results on mixed Hindi+English scans.
  - **Tesseract (optional/legacy)**: also supported; on Windows install the `.exe` and make sure language data `hin` + `eng` is present.

---

### Configuration (environment variables)

These are already supported by the code, so new users don’t need to edit files:

- **`POPPLER_PATH`**: path to Poppler `bin` directory (Windows: `...\Library\bin`)
- **`TESSERACT_CMD`**: path to `tesseract.exe` (Windows default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- **`PDF_PATH`** (CLI only): path to the PDF to process. If not set, the CLI will auto-pick the first `.pdf` found in `uploads/`.

Example (PowerShell):

```powershell
$env:POPPLER_PATH="C:\path\to\poppler\Library\bin"
$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
$env:PDF_PATH="E:\TextExtractor\uploads\my.pdf"
```

---

### Run options

#### Option A: Streamlit UI (recommended)

```bash
streamlit run streamlit_app.py
```

- **OCR engine**: choose **PaddleOCR (recommended)** for best accuracy.
- **Poppler/Tesseract paths**: can be edited in the UI if needed.
- Outputs are written to `output/` and also available as download buttons.

#### Option B: CLI

Put a PDF into `uploads/` (or set `PDF_PATH`), then run:

```bash
python app.py
```

Outputs:
- `output/hindi_questions.txt`
- `output/english_questions.txt`

Format example:

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

---

### Project structure (key files)

- `streamlit_app.py`: Streamlit UI (upload → extract → preview/download)
- `app.py`: core pipeline + CLI entry (PDF → images → OCR → parse → save)
- `extractor/ai_ocr.py`: OCR backends (PaddleOCR + Tesseract)
- `extractor/question_parser.py`: UPSC-style MCQ parsing + Hindi/English classification
- `utils/csv_writer.py`: writes final text files into `output/`
- `uploads/`: input PDFs (CLI will auto-pick the first PDF here if `PDF_PATH` not set)
- `output/`: generated text files

---

### Troubleshooting (common issues)

- **PDF conversion fails (`pdf2image` / Poppler errors)**:
  - Symptoms: `PDFInfoNotInstalledError`, “Unable to get page count”, or Poppler not found.
  - Fix: set `POPPLER_PATH` to the Poppler `Library\bin` folder (see Quick start).

- **Tesseract not found / wrong path**:
  - Symptoms: `TesseractNotFoundError` or OCR returns empty output when using Tesseract.
  - Fix: set `TESSERACT_CMD` to the real `tesseract.exe` path.

- **PaddleOCR install is slow / fails**:
  - `paddlepaddle` can be large on Windows and may take time to install.
  - If PaddleOCR isn’t available, the app will try to fall back to Tesseract automatically.

- **Permission error running `Activate.ps1`** (PowerShell):
  - Run PowerShell as your normal user and execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

### Notes and limitations

- This tool is tuned for **UPSC Prelims-style MCQs** (stem + options (a)–(d), statement questions, mixed Hindi/English).
- OCR quality depends heavily on scan quality (resolution, skew, blur). If results look poor, try higher DPI in the UI (e.g. 350–450).

---

### Free hosting (Hugging Face Spaces - Docker)

This is the **most reliable free** way to host this OCR app because it includes Poppler + Tesseract + PaddleOCR.

1. Push this repo to GitHub (public).
2. On Hugging Face → Spaces → **Create new Space**
3. Select **Docker** as the Space SDK.
4. Connect your GitHub repo (or upload files).
5. The Space will build from `Dockerfile` and run the Streamlit app on port **7860** automatically.

Notes:
- Free CPU can be slow for large PDFs.
- The Docker image installs `poppler-utils` + `tesseract-ocr` (+ Hindi/English language packs) automatically.

