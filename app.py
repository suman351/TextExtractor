import os

from pdf2image import convert_from_path
import pytesseract

from extractor.question_parser import parse_questions
from utils.csv_writer import save_extracted_questions

# Configuration
PDF_PATH = "uploads/2022 = PT = CSE.pdf"
POPPLER_PATH = r"C:\Users\suman\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def process_document():
    if not os.path.exists(PDF_PATH):
        print("PDF file not found!")
        return

    print("Converting PDF to images...")
    images = convert_from_path(PDF_PATH, dpi=300, poppler_path=POPPLER_PATH)

    all_text = ""

    print("Extracting text from both columns...")
    for img in images[1:]:  # Skipping instructions page
        width, height = img.size

        # Left column (typically Hindi)
        left_col = img.crop((0, 0, width // 2, height))
        all_text += pytesseract.image_to_string(left_col, lang="hin+eng") + "\n"

        # Right column (typically English)
        right_col = img.crop((width // 2, 0, width, height))
        all_text += pytesseract.image_to_string(right_col, lang="hin+eng") + "\n"

    # Parse questions into Hindi and English lists
    hindi_list, english_list = parse_questions(all_text)

    # Save all extracted questions as plain-text files in output/
    save_extracted_questions(hindi_list, english_list)


if __name__ == "__main__":
    process_document()