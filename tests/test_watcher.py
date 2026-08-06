from ragcore import watcher


def test_wait_until_stable_returns_true_for_unchanging_file(tmp_path, monkeypatch):
    path = tmp_path / "file.pdf"
    path.write_bytes(b"stable content")

    monkeypatch.setattr(watcher, "_STABILITY_POLL_SECONDS", 0)
    assert watcher.wait_until_stable(str(path)) is True


def test_wait_until_stable_returns_false_when_missing(tmp_path):
    missing = tmp_path / "does-not-exist.pdf"
    assert watcher.wait_until_stable(str(missing)) is False


def test_handler_ignores_non_pdf(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(watcher, "ingest_pdf", lambda path, client=None: calls.append(path))

    handler = watcher.PDFHandler(client=object())
    handler._maybe_ingest(str(tmp_path / "notes.txt"))

    assert calls == []


def test_handler_ingests_stable_pdf(tmp_path, monkeypatch):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    calls = []
    monkeypatch.setattr(watcher, "ingest_pdf", lambda path, client=None: calls.append(path))
    monkeypatch.setattr(watcher, "wait_until_stable", lambda path: True)

    handler = watcher.PDFHandler(client=object())
    handler._maybe_ingest(str(pdf_path))

    assert calls == [str(pdf_path)]


def test_handler_skips_ingest_when_file_never_stabilizes(tmp_path, monkeypatch):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    calls = []
    monkeypatch.setattr(watcher, "ingest_pdf", lambda path, client=None: calls.append(path))
    monkeypatch.setattr(watcher, "wait_until_stable", lambda path: False)

    handler = watcher.PDFHandler(client=object())
    handler._maybe_ingest(str(pdf_path))

    assert calls == []


def test_handler_logs_and_continues_on_ingest_failure(tmp_path, monkeypatch):
    pdf_path = tmp_path / "doc.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")

    def _boom(path, client=None):
        raise RuntimeError("parsing exploded")

    monkeypatch.setattr(watcher, "ingest_pdf", _boom)
    monkeypatch.setattr(watcher, "wait_until_stable", lambda path: True)

    handler = watcher.PDFHandler(client=object())
    handler._maybe_ingest(str(pdf_path))  # should not raise
