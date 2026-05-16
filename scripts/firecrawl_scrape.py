#!/usr/bin/env python3
"""Fetch page content as Markdown using Firecrawl scrape API.

Usage:
  python scripts/firecrawl_scrape.py --url https://example.com
  python scripts/firecrawl_scrape.py --url https://example.com --output output/example.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from firecrawl import Firecrawl


def scrape_markdown(url: str, api_key: str | None = None) -> str:
    """Return markdown for the given URL using Firecrawl scrape."""
    if not url:
        raise ValueError("url is required")

    if api_key is None:
        load_dotenv()
        api_key = os.getenv("FIRECRAWL_API_KEY")

    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY is missing. Put it in .env or pass api_key.")

    firecrawl = Firecrawl(api_key=api_key)
    doc = firecrawl.scrape(url, formats=["markdown"])

    markdown = getattr(doc, "markdown", None)
    if not markdown:
        raise RuntimeError(f"Firecrawl returned no markdown. Raw response: {doc}")

    return markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape a URL and return markdown via Firecrawl")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--output", help="Optional output file path for markdown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        md = scrape_markdown(args.url)
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(str(out))
        else:
            print(md)
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
