# extract/pdf_extract.py

import pdfplumber


def extract_text_from_pdf(pdf_path: str):
    """
    Extracts text from PDF.
    Returns: List[str]  (one string per page)
    """

    pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
            else:
                pages.append("")

    return pages
