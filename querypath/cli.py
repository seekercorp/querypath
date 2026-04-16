"""CLI entry point for querypath."""
import argparse
import json
import sys
from pathlib import Path

from querypath.readers import get_reader
from querypath.query_engine import QueryEngine
from querypath.formatter import format_output


def _load_file(path: str):
    suffix = Path(path).suffix.lstrip(".")
    reader = get_reader(suffix)(path)
    return reader.read()


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="querypath",
        description="Run SQL-like queries against JSON, CSV, and YAML files.",
    )
    parser.add_argument("file", help="Path to the input file")
    parser.add_argument("--select", nargs="+", metavar="COL", help="Columns to select")
    parser.add_argument("--where", type=json.loads, metavar="JSON", help="Where conditions as JSON")
    parser.add_argument("--order-by", dest="order_by", metavar="COL")
    parser.add_argument("--order-dir", dest="order_dir", default="asc", choices=["asc", "desc"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--format", dest="fmt", default="table", choices=["table", "json", "csv"])
    parser.add_argument("--join", metavar="FILE", help="File to join with")
    parser.add_argument("--join-left-key", dest="join_left_key", metavar="COL")
    parser.add_argument("--join-right-key", dest="join_right_key", metavar="COL")
    parser.add_argument("--join-type", dest="join_type", default="inner", choices=["inner", "left"])
    parser.add_argument("--join-prefix", dest="join_prefix", metavar="PREFIX")

    args = parser.parse_args(argv)

    try:
        data = _load_file(args.file)
        join_data = _load_file(args.join) if args.join else None

        engine = QueryEngine(data)
        results = engine.execute(
            select=args.select,
            where=args.where,
            order_by=args.order_by,
            order_dir=args.order_dir,
            limit=args.limit,
            join_data=join_data,
            join_left_key=args.join_left_key,
            join_right_key=args.join_right_key,
            join_type=args.join_type,
            join_prefix=args.join_prefix,
        )
        print(format_output(results, fmt=args.fmt))
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
