import fitz

from ragcore.pdf_parser import extract_pages


def _make_pdf(path, page_texts: list[str]):
    doc = fitz.open()
    for text in page_texts:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


def test_extract_pages_returns_text(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    _make_pdf(pdf_path, ["Hello grounding world"])

    pages = extract_pages(str(pdf_path))
    assert len(pages) == 1
    assert "Hello grounding world" in pages[0].text
    assert pages[0].number == 1


def test_extract_pages_skips_blank_pages(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    doc.new_page()  # blank
    page2 = doc.new_page()
    page2.insert_text((72, 72), "second page has text")
    doc.save(str(pdf_path))
    doc.close()

    pages = extract_pages(str(pdf_path))
    assert len(pages) == 1
    assert pages[0].number == 2
