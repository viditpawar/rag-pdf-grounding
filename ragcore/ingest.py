"""Ingestion pipeline: PDF -> parsed pages -> chunks -> embeddings -> vector store.

This is the "grounding" half of the system - it runs once per document,
whenever a new PDF shows up (manually today, via a folder watcher from week 2).
"""
import logging
import os

from . import config
from .chunking import chunk_pages
from .ollama_client import OllamaClient
from .pdf_parser import extract_pages
from .vectorstore import add_chunks, get_collection

logger = logging.getLogger(__name__)


def ingest_pdf(pdf_path: str, client: OllamaClient | None = None) -> int:
    """Parse, chunk, embed, and store a single PDF. Returns chunks stored."""
    client = client or OllamaClient()
    source = os.path.basename(pdf_path)

    logger.info("Parsing %s", source)
    pages = extract_pages(pdf_path)
    if not pages:
        logger.warning("No extractable text found in %s (scanned PDF?)", source)
        return 0

    chunks = chunk_pages(pages, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    logger.info("Split %s (%d pages) into %d chunks", source, len(pages), len(chunks))

    embeddings = client.embed_batch([c.text for c in chunks])

    collection = get_collection()
    added = add_chunks(collection, source, chunks, embeddings)
    logger.info("Stored %d chunks from %s in the grounding store", added, source)
    return added
