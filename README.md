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

This is being built in stages. Current stage: **core pipeline, no Docker yet.**

- [x] Week 1 — PDF parsing, chunking, embedding, vector store, CLI scripts
- [ ] Week 2 — Folder watcher (separate service) + FastAPI wrapper
- [ ] Week 3 — Dockerized: Ollama, Chroma, API, watcher as networked services
- [ ] Week 4 — Streamlit UI showing answers with cited source chunks
- [ ] Week 5 — GitHub Actions CI (lint, tests, image build) + Prometheus/Grafana
- [ ] Week 6 — Docs, demo GIF, polish

## Tech stack

| Layer | Choice |
|---|---|
| LLM + embeddings | Ollama (`llama3.2:3b` + `nomic-embed-text`) |
| Vector store | ChromaDB (persistent, local) |
| PDF parsing | PyMuPDF |
| Folder watcher | `watchdog` (week 2) |
| API | FastAPI (week 2) |
| UI | Streamlit (week 4) |
| Orchestration | Docker Compose (week 3) |

## Setup (current stage)

Requires Python 3.11+ and [Ollama](https://ollama.com) installed and running
locally.

```bash
# 1. Pull the models Ollama will serve
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure (defaults in .env.example already match the models above)
cp .env.example .env
```

## Usage

```bash
# Ingest one or more PDFs into the grounding store
python ingest_cli.py data/pdfs/your-file.pdf

# Ask a question grounded in what's been ingested
python ask_cli.py "What does the document say about X?"
```

## Tests

```bash
python -m pytest -v
```

Tests cover chunking logic, PDF parsing, and the vector store — the parts
that don't require Ollama to be running. LLM calls are exercised manually
via the CLI scripts above.

## Project layout

```
ragcore/
  pdf_parser.py      # PDF -> text, page by page
  chunking.py         # text -> overlapping word chunks
  ollama_client.py     # HTTP client for Ollama (embed + generate)
  vectorstore.py       # Chroma wrapper (the grounding store)
  ingest.py            # ingestion pipeline
  qa.py                 # retrieval + generation pipeline
ingest_cli.py           # CLI: ingest PDFs
ask_cli.py               # CLI: ask questions
tests/
```
