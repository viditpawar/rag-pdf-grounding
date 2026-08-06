import io

from fastapi.testclient import TestClient

import api


def test_health():
    client = TestClient(api.app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ingest_rejects_non_pdf():
    client = TestClient(api.app)
    resp = client.post(
        "/ingest", files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    )
    assert resp.status_code == 400


def test_ingest_stores_pdf(monkeypatch):
    monkeypatch.setattr(api, "ingest_pdf", lambda path: 3)

    client = TestClient(api.app)
    resp = client.post(
        "/ingest", files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")}
    )

    assert resp.status_code == 200
    assert resp.json() == {"filename": "doc.pdf", "chunks_stored": 3}


def test_ask_returns_answer(monkeypatch):
    stub_result = {
        "answer": "The document says X.",
        "sources": [{"source": "doc.pdf", "page": 1, "excerpt": "..."}],
    }
    monkeypatch.setattr(api, "answer_question", lambda question, top_k=None: stub_result)

    client = TestClient(api.app)
    resp = client.post("/ask", json={"question": "What does it say?"})

    assert resp.status_code == 200
    assert resp.json() == stub_result
