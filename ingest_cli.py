#!/usr/bin/env python
"""CLI: python ingest_cli.py path/to/file.pdf [more.pdf ...]"""
import argparse
import logging
import sys

from ragcore.ingest import ingest_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Ingest one or more PDFs into the grounding store.")
    parser.add_argument("pdfs", nargs="+", help="Path(s) to PDF file(s)")
    args = parser.parse_args()

    total = 0
    for pdf_path in args.pdfs:
        total += ingest_pdf(pdf_path)
    print(f"Done. {total} chunks stored across {len(args.pdfs)} file(s).")


if __name__ == "__main__":
    sys.exit(main())
