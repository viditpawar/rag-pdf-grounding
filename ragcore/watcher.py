"""Folder watcher: notices new PDFs dropped in WATCH_FOLDER and ingests them.

Runs as a separate long-lived process (see watcher_cli.py at the repo root).
Only reacts to files added while it's running - it does not scan for
pre-existing files on startup, so anything dropped while the watcher was
down needs a manual `ingest_cli.py` run.
"""
import logging
import os
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from . import config
from .ingest import ingest_pdf
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)

# How long to wait for a file's size to stop changing before treating it as
# fully written (guards against ingesting a PDF that's still being copied).
_STABILITY_POLL_SECONDS = 0.5
_STABILITY_TIMEOUT_SECONDS = 10


def wait_until_stable(path: str) -> bool:
    """Poll a file's size until it stops changing. Returns False on timeout."""
    deadline = time.monotonic() + _STABILITY_TIMEOUT_SECONDS
    last_size = -1
    while time.monotonic() < deadline:
        try:
            size = os.path.getsize(path)
        except OSError:
            return False
        if size == last_size:
            return True
        last_size = size
        time.sleep(_STABILITY_POLL_SECONDS)
    return False


class PDFHandler(FileSystemEventHandler):
    def __init__(self, client: OllamaClient | None = None):
        self.client = client or OllamaClient()

    def on_created(self, event):
        if not event.is_directory:
            self._maybe_ingest(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._maybe_ingest(event.dest_path)

    def _maybe_ingest(self, path: str) -> None:
        if not path.lower().endswith(".pdf"):
            return

        logger.info("Detected new PDF: %s", path)
        if not wait_until_stable(path):
            logger.warning("Gave up waiting for %s to finish writing", path)
            return

        try:
            ingest_pdf(path, client=self.client)
        except Exception:
            logger.exception("Failed to ingest %s", path)


def watch_folder(folder: str | None = None) -> None:
    folder = folder or config.WATCH_FOLDER
    Path(folder).mkdir(parents=True, exist_ok=True)

    handler = PDFHandler()
    # PollingObserver (not the default inotify-based Observer): bind-mounted
    # volumes under Docker Desktop don't reliably propagate inotify events
    # for changes made from the host, so we poll the directory instead.
    observer = PollingObserver()
    observer.schedule(handler, folder, recursive=False)
    observer.start()
    logger.info("Watching %s for new PDFs (Ctrl+C to stop)", folder)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher")
        observer.stop()
    observer.join()
