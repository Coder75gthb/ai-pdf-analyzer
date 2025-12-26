import pytesseract
from pdf2image import convert_from_path
import tempfile
import os

# 🔒 HARD SET TESSERACT PATH (NO PATH DEPENDENCY)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ---- POPPLER PATH (MATCHES YOUR FOLDER) ----
POPPLER_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "poppler-25.12.0",
    "Library",
    "bin"
)


def ocr_pdf(pdf_path):
    text_pages = []

    with tempfile.TemporaryDirectory() as temp_dir:
        images = convert_from_path(
            pdf_path,
            dpi=300,
            output_folder=temp_dir,
            poppler_path=POPPLER_PATH
        )

        for img in images:
            text = pytesseract.image_to_string(img, lang="eng")
            if text.strip():
                text_pages.append(text)

    return "\n\n".join(text_pages).strip()

