"""FastAPI wrapper around the ingest + ask pipeline.

Run with: uvicorn api:app --reload

Thin wrapper, same spirit as ingest_cli.py / ask_cli.py - no business logic
here, just HTTP plumbing around ragcore.ingest.ingest_pdf and
ragcore.qa.answer_question.
"""
import logging
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile
from pydantic import BaseModel

from ragcore.ingest import ingest_pdf
from ragcore.qa import answer_question

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="RAG PDF Grounding API")


class AskRequest(BaseModel):
    question: str
    top_k: int | None = None


class AskResponse(BaseModel):
    answer: str
    sources: list[dict]


class IngestResponse(BaseModel):
    filename: str
    chunks_stored: int


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir) / file.filename
        with tmp_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        chunks_stored = ingest_pdf(str(tmp_path))

    return IngestResponse(filename=file.filename, chunks_stored=chunks_stored)


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    result = answer_question(request.question, top_k=request.top_k)
    return AskResponse(**result)
