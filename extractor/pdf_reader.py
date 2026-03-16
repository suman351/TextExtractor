import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_pdf(pdf_path):

    text = ""

    images = convert_from_path(
        pdf_path,
        dpi=400,
        poppler_path=r"C:\Users\suman\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
    )

    # Skip first page (instructions)
    images = images[1:]

    for img in images:
        extracted = pytesseract.image_to_string(img, lang="hin+eng")
        text += extracted + "\n"

    return text