# RAG PDF Grounding Pipeline

A retrieval-augmented generation (RAG) system that answers questions grounded
in your own PDFs, running entirely on local, self-hosted infrastructure —
no API keys, no external calls.

Drop a PDF in a watched folder, ask a question, get an answer with cited
sources — powered by a local LLM served through Ollama, running in Docker.

## Why this exists

This project is a cloud/DevOps-flavored take on RAG: the interesting parts
are containerization, orchestration, observability, and CI — not model
training. The LLM and embedding model are treated as infrastructure to
deploy reliably, not as something to build from scratch.

## Architecture

**Ingestion (grounding), runs whenever a PDF is added:**

```
watched folder → parse & chunk PDF → embed each chunk → store in vector DB
```

**Query (retrieval-augmented generation), runs per question:**

```
question → embed question → retrieve top-k chunks → build augmented prompt
         → LLM call (Ollama, in Docker) → grounded answer + sources
```

Retrieval happens *before* generation — the retrieved chunks are what
"ground" the LLM's answer in the actual document instead of letting it
hallucinate.

## Status

This is being built in stages. Current stage: **fully Dockerized — Ollama, Chroma, API, and watcher run as networked services via Docker Compose.**

- [x] Week 1 — PDF parsing, chunking, embedding, vector store, CLI scripts
- [x] Week 2 — Folder watcher (separate service) + FastAPI wrapper
- [x] Week 3 — Dockerized: Ollama, Chroma, API, watcher as networked services
- [ ] Week 4 — Streamlit UI showing answers with cited source chunks
- [ ] Week 5 — GitHub Actions CI (lint, tests, image build) + Prometheus/Grafana
- [ ] Week 6 — Docs, demo GIF, polish

## Tech stack

| Layer | Choice |
|---|---|
| LLM + embeddings | Ollama (`llama3.2:3b` + `nomic-embed-text`) |
| Vector store | ChromaDB (server, networked via Docker Compose) |
| PDF parsing | PyMuPDF |
| Folder watcher | `watchdog` (polling observer) |
| API | FastAPI |
| UI | Streamlit (week 4) |
| Orchestration | Docker Compose |

## Running with Docker Compose (recommended)

Requires Docker with Compose v2. This brings up all four services -
`ollama`, `chroma`, `api`, and `watcher` - networked together, plus a
one-shot `ollama-pull` job that pulls the configured models before
`api`/`watcher` start.

```bash
docker compose up -d --build

# Wait for everything to report healthy (first run pulls ~2.3GB of models)
docker compose ps
```

```bash
# Drop a PDF in the watched folder - the watcher container auto-ingests it
cp your-file.pdf data/pdfs/

# ...or ingest directly through the API
curl -F file=@data/pdfs/your-file.pdf http://localhost:8000/ingest

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about X?"}'

docker compose down
```

Service ports on the host: API on `8000`, Chroma on `8001` (its container
port `8000` is remapped to avoid colliding with the API), Ollama on
`11434`. Model weights and Chroma's data persist in named volumes
(`ollama_data`, `chroma_data`) across restarts; the watched folder is a
bind mount at `./data/pdfs`, so files dropped there from the host are
visible to the `watcher` container.

## Local setup (without Docker)

For development and running the test suite without containers. Requires
Python 3.11+ and [Ollama](https://ollama.com) installed and running
locally.

```bash
# 1. Pull the models Ollama will serve
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure (defaults in .env.example already match the models above,
#    and leave CHROMA_HOST unset so Chroma runs embedded rather than
#    expecting a networked server)
cp .env.example .env
```

## Usage

```bash
# Ingest one or more PDFs into the grounding store
python ingest_cli.py data/pdfs/your-file.pdf

# Ask a question grounded in what's been ingested
python ask_cli.py "What does the document say about X?"
```

### Folder watcher

Watches `WATCH_FOLDER` (default `./data/pdfs`) and ingests any PDF dropped
into it while the watcher is running.

```bash
python watcher_cli.py
```

### API

```bash
uvicorn api:app --reload

# Ingest a PDF
curl -F file=@data/pdfs/your-file.pdf http://localhost:8000/ingest

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does the document say about X?"}'
```

## Tests

```bash
python -m pytest -v
```

Tests cover chunking logic, PDF parsing, the vector store, the folder
watcher, and the API — all with Ollama calls stubbed out, so the suite
doesn't need Ollama running. LLM calls themselves are exercised manually via
the CLI scripts and API above.

## Project layout

```
ragcore/
  pdf_parser.py      # PDF -> text, page by page
  chunking.py         # text -> overlapping word chunks
  ollama_client.py     # HTTP client for Ollama (embed + generate)
  vectorstore.py       # Chroma wrapper (the grounding store)
  ingest.py            # ingestion pipeline
  qa.py                 # retrieval + generation pipeline
  watcher.py            # folder watcher (auto-ingest on file drop)
ingest_cli.py           # CLI: ingest PDFs
ask_cli.py               # CLI: ask questions
watcher_cli.py            # entrypoint: run the folder watcher
api.py                     # FastAPI app: /ingest, /ask
tests/
Dockerfile                  # shared image for the api and watcher services
docker-compose.yml           # ollama, chroma, api, watcher as networked services
```
