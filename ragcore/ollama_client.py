"""Thin HTTP client for a local Ollama server (chat + embeddings).

Kept as a plain requests wrapper (no SDK dependency) so it is easy to see
exactly what's being sent to the LLM, which matters for debugging RAG
quality issues later.
"""
import requests

from . import config


class OllamaClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or config.OLLAMA_BASE_URL

    def embed(self, text: str, model: str | None = None) -> list[float]:
        model = model or config.OLLAMA_EMBED_MODEL
        resp = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]

    def embed_batch(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        return [self.embed(t, model) for t in texts]

    def generate(self, prompt: str, system: str | None = None, model: str | None = None) -> str:
        model = model or config.OLLAMA_CHAT_MODEL
        payload = {"model": model, "prompt": prompt, "stream": False}
        if system:
            payload["system"] = system
        resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json()["response"].strip()
