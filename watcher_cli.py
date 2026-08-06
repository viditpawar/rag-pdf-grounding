#!/usr/bin/env python
"""Run: python watcher_cli.py

Watches WATCH_FOLDER and ingests any PDF dropped into it. Runs until Ctrl+C.
"""
import logging
import sys

from ragcore.watcher import watch_folder

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main():
    watch_folder()


if __name__ == "__main__":
    sys.exit(main())
