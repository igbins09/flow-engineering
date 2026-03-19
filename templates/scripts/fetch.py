#!/usr/bin/env python3
"""
Flow Engineering — Generic Fetch Template (Deterministic Layer)

This script retrieves and structures all input data needed for the LLM step.
It must be fully deterministic — no LLM calls allowed here.

Usage:
  python fetch.py                     # Default: read from configured source
  python fetch.py --source api        # Specify source type
  python fetch.py --source file --path data.json

Output:
  Structured JSON to stdout. Errors to stderr with exit code 1.

Customize:
  1. Add your data sources to the SOURCES dict
  2. Implement each source's fetch function
  3. Add any CLI arguments you need
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def fetch_from_file(path: str) -> list[dict]:
    """Read items from a JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both array and object with "items" key
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "items" in data:
        return data["items"]
    else:
        return [data]


def fetch_from_api(endpoint: str = "") -> list[dict]:
    """Fetch items from an API endpoint."""
    # TODO: Implement your API call
    # Example:
    #   import requests
    #   response = requests.get(endpoint, headers={"Authorization": f"Bearer {API_KEY}"})
    #   response.raise_for_status()
    #   return response.json()["results"]
    raise NotImplementedError("Implement fetch_from_api() with your API endpoint")


def fetch_from_database(query: str = "") -> list[dict]:
    """Fetch items from a SQLite database."""
    # TODO: Implement your database query
    # Example:
    #   import sqlite3
    #   conn = sqlite3.connect("your.db")
    #   conn.row_factory = sqlite3.Row
    #   rows = conn.execute(query).fetchall()
    #   return [dict(row) for row in rows]
    raise NotImplementedError("Implement fetch_from_database() with your DB path and query")


# Register your data sources here
SOURCES = {
    "file": fetch_from_file,
    "api": fetch_from_api,
    "database": fetch_from_database,
}


def fetch(source: str = "file", **kwargs) -> dict:
    """Main fetch function. Returns structured JSON."""
    start_time = time.time()

    if source not in SOURCES:
        raise ValueError(f"Unknown source: {source}. Available: {list(SOURCES.keys())}")

    fetch_fn = SOURCES[source]
    items = fetch_fn(**kwargs)

    duration_ms = int((time.time() - start_time) * 1000)

    return {
        "items": items,
        "metadata": {
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(items),
            "duration_ms": duration_ms,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch input data (D layer)")
    parser.add_argument("--source", default="file", choices=SOURCES.keys(), help="Data source type")
    parser.add_argument("--path", default="", help="File path (for file source)")
    parser.add_argument("--endpoint", default="", help="API endpoint (for api source)")
    parser.add_argument("--query", default="", help="SQL query (for database source)")
    args = parser.parse_args()

    kwargs = {}
    if args.source == "file":
        kwargs["path"] = args.path
    elif args.source == "api":
        kwargs["endpoint"] = args.endpoint
    elif args.source == "database":
        kwargs["query"] = args.query

    try:
        result = fetch(args.source, **kwargs)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e), "step": "fetch"}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
