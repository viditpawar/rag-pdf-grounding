#!/usr/bin/env python
"""CLI: python ask_cli.py "your question here" """
import argparse
import logging
import sys

from ragcore.qa import answer_question

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Ask a question grounded in the ingested PDFs.")
    parser.add_argument("question", help="Your question")
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    result = answer_question(args.question, top_k=args.top_k)

    print("\nAnswer:\n" + result["answer"])
    if result["sources"]:
        print("\nSources:")
        for s in result["sources"]:
            print(f"  - {s['source']} (page {s['page']}): {s['excerpt']}...")


if __name__ == "__main__":
    sys.exit(main())
