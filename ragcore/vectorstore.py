"""Wraps a persistent Chroma collection used as the grounding store.

`persist_dir` / `collection_name` are accepted as optional args (rather than
read from config internally) so tests can point this at a temp directory
without touching real data or env vars.
"""
import hashlib

import chromadb

from . import config


def get_collection(
    persist_dir: str | None = None,
    collection_name: str | None = None,
    host: str | None = None,
    port: int | None = None,
):
    """Get (or create) the grounding collection.

    Connects to a networked Chroma server when a host is given (explicitly,
    or via CHROMA_HOST in Docker Compose); otherwise falls back to an
    embedded PersistentClient on disk, which is what tests use.
    """
    host = host if host is not None else config.CHROMA_HOST
    collection_name = collection_name or config.CHROMA_COLLECTION_NAME

    if host:
        client = chromadb.HttpClient(host=host, port=port or config.CHROMA_PORT)
    else:
        persist_dir = persist_dir or config.CHROMA_PERSIST_DIR
        client = chromadb.PersistentClient(path=persist_dir)

    return client.get_or_create_collection(name=collection_name)


def chunk_id(source: str, page: int, chunk_index: int, text: str) -> str:
    """Deterministic ID so re-ingesting the same PDF upserts instead of duplicating."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
    return f"{source}:{page}:{chunk_index}:{digest}"


def add_chunks(collection, source: str, chunks, embeddings: list[list[float]]) -> int:
    if not chunks:
        return 0
    ids, docs, metas = [], [], []
    for chunk, embedding in zip(chunks, embeddings):
        ids.append(chunk_id(source, chunk.page, chunk.chunk_index, chunk.text))
        docs.append(chunk.text)
        metas.append({"source": source, "page": chunk.page, "chunk_index": chunk.chunk_index})
    collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    return len(ids)


def query(collection, query_embedding: list[float], top_k: int):
    return collection.query(query_embeddings=[query_embedding], n_results=top_k)
