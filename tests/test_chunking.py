import pytest

from ragcore.chunking import chunk_pages, chunk_text
from ragcore.pdf_parser import Page


def test_chunk_text_basic():
    text = " ".join(f"word{i}" for i in range(100))
    chunks = chunk_text(text, chunk_size=30, overlap=5)
    assert len(chunks) > 1
    # consecutive chunks should overlap by exactly `overlap` words
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    assert first_words[-5:] == second_words[:5]


def test_chunk_text_empty():
    assert chunk_text("", chunk_size=30, overlap=5) == []


def test_chunk_text_short_text_single_chunk():
    chunks = chunk_text("just a few words here", chunk_size=30, overlap=5)
    assert chunks == ["just a few words here"]


def test_chunk_text_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("a b c", chunk_size=5, overlap=5)


def test_chunk_pages_preserves_page_numbers():
    pages = [
        Page(number=1, text="alpha beta gamma delta epsilon"),
        Page(number=2, text="zeta eta theta"),
    ]
    chunks = chunk_pages(pages, chunk_size=3, overlap=1)
    assert {c.page for c in chunks} == {1, 2}
    assert chunks[0].chunk_index == 0
