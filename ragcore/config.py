"""Central configuration, loaded from environment variables (.env supported)."""
import os

from dotenv import load_dotenv

load_dotenv()

# Ollama (LLM + embeddings server)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "llama3.2:3b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Vector store (Chroma). If CHROMA_HOST is set, connect to a Chroma server
# over HTTP (week 3, Docker Compose); otherwise fall back to an embedded
# PersistentClient backed by CHROMA_PERSIST_DIR (local/dev, and tests).
CHROMA_HOST = os.getenv("CHROMA_HOST")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "pdf_grounding")

# Chunking (word-based, dependency free)
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "250"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval
TOP_K = int(os.getenv("TOP_K", "4"))

# Folder watcher (added in week 2)
WATCH_FOLDER = os.getenv("WATCH_FOLDER", "./data/pdfs")
