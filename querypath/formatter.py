import json
import csv
import io
from typing import List, Dict, Any


SUPPORTED_FORMATS = ("table", "json", "csv")


def format_table(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "(no results)"

    headers = list(rows[0].keys())
    col_widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))

    sep = "+" + "+".join("-" * (col_widths[h] + 2) for h in headers) + "+"
    header_row = "|" + "|".join(f" {h:<{col_widths[h]}} " for h in headers) + "|"

    lines = [sep, header_row, sep]
    for row in rows:
        line = "|" + "|".join(f" {str(row.get(h, '')):<{col_widths[h]}} " for h in headers) + "|"
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


def format_json(rows: List[Dict[str, Any]]) -> str:
    return json.dumps(rows, indent=2, default=str)


def format_csv(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return ""
    output = io.StringIO()
    headers = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().rstrip()


def format_output(rows: List[Dict[str, Any]], fmt: str = "table") -> str:
    if fmt == "json":
        return format_json(rows)
    elif fmt == "csv":
        return format_csv(rows)
    elif fmt == "table":
        return format_table(rows)
    else:
        raise ValueError(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}")
