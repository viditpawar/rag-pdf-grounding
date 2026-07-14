"""Splits page text into overlapping word-based chunks.

Word-based chunking (rather than token-based) keeps this dependency-free
and is good enough for a portfolio-grade RAG pipeline. Swap in a tokenizer
(e.g. tiktoken) later if you want token-precise chunk sizing.
"""
from dataclasses import dataclass

from .pdf_parser import Page


@dataclass
class Chunk:
    text: str
    page: int
    chunk_index: int


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks of `chunk_size` words."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def chunk_pages(pages: list[Page], chunk_size: int, overlap: int) -> list[Chunk]:
    """Chunk every page independently, preserving page numbers for citations."""
    all_chunks = []
    for page in pages:
        for idx, text in enumerate(chunk_text(page.text, chunk_size, overlap)):
            all_chunks.append(Chunk(text=text, page=page.number, chunk_index=idx))
    return all_chunks
