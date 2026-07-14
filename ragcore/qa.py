"""Query pipeline: question -> retrieval -> augmented prompt -> LLM answer.

This is the "RAG" half of the system - retrieval happens first, and its
output shapes the prompt the LLM actually sees. Grounding and RAG are the
same mechanism, not two separate stages.
"""
import logging

from . import config
from .ollama_client import OllamaClient
from .vectorstore import get_collection, query

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using only the "
    "provided context from the user's documents. If the answer is not "
    "contained in the context, say you don't know rather than guessing."
)


def build_prompt(question: str, context_chunks: list[str]) -> str:
    context = "\n\n".join(f"[{i + 1}] {c}" for i, c in enumerate(context_chunks))
    return (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above. Cite sources like [1], [2] where relevant."
    )


def answer_question(question: str, top_k: int | None = None, client: OllamaClient | None = None) -> dict:
    client = client or OllamaClient()
    top_k = top_k or config.TOP_K

    query_embedding = client.embed(question)
    collection = get_collection()
    results = query(collection, query_embedding, top_k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {"answer": "No documents have been ingested yet.", "sources": []}

    prompt = build_prompt(question, documents)
    answer = client.generate(prompt, system=SYSTEM_PROMPT)

    sources = [
        {"source": m["source"], "page": m["page"], "excerpt": d[:200]}
        for m, d in zip(metadatas, documents)
    ]
    return {"answer": answer, "sources": sources}
