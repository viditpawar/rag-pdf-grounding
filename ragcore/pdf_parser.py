"""Extracts text from PDF files, page by page."""
from dataclasses import dataclass

import fitz  # PyMuPDF


@dataclass
class Page:
    number: int
    text: str


def extract_pages(pdf_path: str) -> list[Page]:
    """Return one Page per non-empty page in the PDF, 1-indexed."""
    pages = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if text:
                pages.append(Page(number=i + 1, text=text))
    return pages
