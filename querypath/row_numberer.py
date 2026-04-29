"""row_numberer.py – add sequential or grouped row-index columns to a result set.

Functions
---------
apply_row_index      – add a 1-based index column across all rows
apply_grouped_index  – reset the counter per unique value of a partition column
parse_row_index_spec – extract config from an opts dict
"""
from __future__ import annotations
from typing import Any


def apply_row_index(
    rows: list[dict],
    column: str = "_row_index",
    start: int = 1,
) -> list[dict]:
    """Return copies of *rows* with a sequential integer column added."""
    result = []
    for i, row in enumerate(rows, start=start):
        new_row = dict(row)
        new_row[column] = i
        result.append(new_row)
    return result


def apply_grouped_index(
    rows: list[dict],
    partition_by: str,
    column: str = "_group_index",
    start: int = 1,
) -> list[dict]:
    """Return copies of *rows* with a counter that resets for each partition value."""
    counters: dict[Any, int] = {}
    result = []
    for row in rows:
        key = row.get(partition_by)
        counters[key] = counters.get(key, start - 1) + 1
        new_row = dict(row)
        new_row[column] = counters[key]
        result.append(new_row)
    return result


def parse_row_index_spec(opts: dict | None) -> dict | None:
    """Extract row-index config from *opts*.

    Expected keys (all optional):
        row_index        – str column name, or True to use default name
        row_index_start  – int, default 1
        row_index_partition – str column to partition by
    Returns None when the feature is not requested.
    """
    if not opts:
        return None
    raw = opts.get("row_index")
    if not raw:
        return None
    column = raw if isinstance(raw, str) else "_row_index"
    return {
        "column": column,
        "start": int(opts.get("row_index_start", 1)),
        "partition_by": opts.get("row_index_partition"),
    }


def run_pipeline_with_row_index(
    rows: list[dict],
    opts: dict | None = None,
) -> list[dict]:
    """Apply row-index numbering when configured in *opts*."""
    spec = parse_row_index_spec(opts)
    if spec is None:
        return rows
    if spec["partition_by"]:
        return apply_grouped_index(
            rows,
            partition_by=spec["partition_by"],
            column=spec["column"],
            start=spec["start"],
        )
    return apply_row_index(rows, column=spec["column"], start=spec["start"])
