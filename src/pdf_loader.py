from typing import List
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar


def extract_pdf_text(pdf_path: str) -> List[dict]:
    pages = []
    for page_no, page_layout in enumerate(extract_pages(pdf_path), start=1):
        lines = []
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                text = element.get_text()
                if text:
                    lines.append(text)
        page_text = "\n".join(lines)
        pages.append({"page": page_no, "text": page_text})
    return pages
