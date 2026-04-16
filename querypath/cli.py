import argparse
import json
import sys
from pathlib import Path

from querypath.readers import get_reader
from querypath.query_engine import QueryEngine


def format_output(results, fmt="table"):
    if not results:
        print("No results.")
        return

    if fmt == "json":
        print(json.dumps(results, indent=2))
        return

    # Table format
    keys = list(results[0].keys())
    col_widths = {k: max(len(k), max(len(str(row.get(k, ""))) for row in results)) for k in keys}

    header = "  ".join(k.ljust(col_widths[k]) for k in keys)
    separator = "  ".join("-" * col_widths[k] for k in keys)
    print(header)
    print(separator)
    for row in results:
        print("  ".join(str(row.get(k, "")).ljust(col_widths[k]) for k in keys))


def main():
    parser = argparse.ArgumentParser(
        description="Run SQL-like queries against JSON, CSV, or YAML files."
    )
    parser.add_argument("file", help="Path to the data file (json, csv, yaml/yml)")
    parser.add_argument("query", help="SQL-like query string, e.g. \"SELECT * FROM data\"")
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    args = parser.parse_args()
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"Error: file '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        reader = get_reader(str(file_path))
        records = reader.read()
        engine = QueryEngine(records)
        results = engine.execute(args.query)
        format_output(results, fmt=args.format)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
