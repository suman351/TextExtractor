import os
from dataclasses import dataclass
from typing import Optional

from pdf2image import convert_from_path
import pytesseract

from extractor.ai_ocr import ocr_paddle, ocr_tesseract
from extractor.question_parser import parse_questions
from utils.csv_writer import save_extracted_questions

# Configuration
def _pick_default_pdf() -> str | None:
    uploads_dir = "uploads"
    if not os.path.isdir(uploads_dir):
        return None
    pdfs = [
        os.path.join(uploads_dir, f)
        for f in os.listdir(uploads_dir)
        if f.lower().endswith(".pdf")
    ]
    return sorted(pdfs)[0] if pdfs else None


# You can override this by setting the PDF_PATH environment variable.
PDF_PATH = os.environ.get("PDF_PATH") or _pick_default_pdf()
POPPLER_PATH = os.environ.get(
    "POPPLER_PATH",
    r"C:\Users\suman\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin",
)
TESSERACT_CMD = os.environ.get(
    "TESSERACT_CMD",
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
)
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


@dataclass(frozen=True)
class ExtractionResult:
    hindi_questions: list[str]
    english_questions: list[str]
    hindi_txt: str
    english_txt: str


def _format_questions_txt(prefix: str, questions: list[str]) -> str:
    parts: list[str] = []
    for i, q in enumerate(questions, 1):
        parts.append(f"--- {prefix} Question {i} ---\n{q}\n")
    return "\n".join(parts).strip() + "\n"


def extract_from_pdf(
    pdf_path: str,
    *,
    poppler_path: Optional[str] = POPPLER_PATH,
    tesseract_cmd: Optional[str] = TESSERACT_CMD,
    dpi: int = 300,
    skip_first_page: bool = True,
    ocr_engine: str = "paddle",
) -> ExtractionResult:
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    images = convert_from_path(pdf_path, dpi=dpi, poppler_path=poppler_path)
    if skip_first_page and len(images) > 1:
        images = images[1:]

    # Keep columns separate to avoid left-column artifacts leaking into the
    # right-column question blocks (and vice-versa).
    #
    # Also do NOT assume a fixed layout (left=Hindi/right=English). Some PDFs
    # have English on both columns or Hindi on both columns. So we parse each
    # column independently and let the parser classify each question by
    # language (via is_hindi()).
    column_texts: list[str] = []

    for img in images:
        width, height = img.size

        # Left column
        left_col = img.crop((0, 0, width // 2, height))
        column_texts.append(_ocr_image(left_col, ocr_engine=ocr_engine, tesseract_cmd=tesseract_cmd))

        # Right column
        right_col = img.crop((width // 2, 0, width, height))
        column_texts.append(_ocr_image(right_col, ocr_engine=ocr_engine, tesseract_cmd=tesseract_cmd))

    hindi_list: list[str] = []
    english_list: list[str] = []

    for col_text in column_texts:
        h, e = parse_questions(col_text)
        hindi_list.extend(h)
        english_list.extend(e)

    return ExtractionResult(
        hindi_questions=hindi_list,
        english_questions=english_list,
        hindi_txt=_format_questions_txt("Hindi", hindi_list),
        english_txt=_format_questions_txt("English", english_list),
    )


def _ocr_image(pil_image, *, ocr_engine: str, tesseract_cmd: Optional[str]) -> str:
    engine = (ocr_engine or "paddle").strip().lower()
    if engine == "tesseract":
        return ocr_tesseract(pil_image, tesseract_cmd=tesseract_cmd, lang="hin+eng")

    # Default: PaddleOCR (with automatic fallback to tesseract if not installed)
    try:
        return ocr_paddle(pil_image, langs=("hi", "en"))
    except Exception:
        return ocr_tesseract(pil_image, tesseract_cmd=tesseract_cmd, lang="hin+eng")


def process_document():
    if not PDF_PATH or not os.path.exists(PDF_PATH):
        print("PDF file not found!")
        print("Put a .pdf into the 'uploads/' folder or set PDF_PATH to a full file path.")
        return

    print("Extracting questions...")
    result = extract_from_pdf(PDF_PATH)

    # Save all extracted questions as plain-text files in output/
    save_extracted_questions(result.hindi_questions, result.english_questions)


if __name__ == "__main__":
    process_document()