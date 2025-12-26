import pdfplumber

def extract_tables_from_pdf(pdf_path):
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_no, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            for table in page_tables:
                if table and len(table) > 1:
                    tables.append({
                        "page": page_no + 1,
                        "rows": table
                    })

    return tables
