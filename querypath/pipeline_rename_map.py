"""Pipeline integration for bulk column renaming.

This module wires :mod:`querypath.column_rename_map` into the standard
pipeline options dict so that callers can supply a ``rename`` key and
have all matching columns renamed before downstream steps see the data.

Example opts::

    {
        "rename": {"first_name": "fname", "last_name": "lname"},
        # or as pairs:
        # "rename": [["first_name", "fname"], ["last_name", "lname"]],
    }
"""

from typing import Any, Dict, List, Optional

from querypath.column_rename_map import (
    apply_rename_map,
    parse_rename_map_spec,
)


def extract_rename_spec(
    opts: Optional[Dict[str, Any]]
) -> Optional[Dict[str, str]]:
    """Public alias so callers can inspect the parsed rename map."""
    return parse_rename_map_spec(opts)


def run_pipeline_rename_map(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Apply bulk column renaming if a ``rename`` spec is present in *opts*.

    Parameters
    ----------
    rows:
        The current row list flowing through the pipeline.
    opts:
        Pipeline options dict.  The ``rename`` key is consumed here;
        all other keys are ignored by this stage.

    Returns
    -------
    list
        Rows with columns renamed, or the original rows if no spec found.
    """
    rename_map = parse_rename_map_spec(opts)
    if not rename_map:
        return rows
    return apply_rename_map(rows, rename_map)


# ---------------------------------------------------------------------------
# Inline smoke test (not part of the pytest suite)
# ---------------------------------------------------------------------------

def _smoke_test() -> None:  # pragma: no cover
    sample = [
        {"first_name": "Alice", "last_name": "Smith", "dept": "Eng"},
        {"first_name": "Bob", "last_name": "Jones", "dept": "HR"},
    ]
    opts = {"rename": {"first_name": "fname", "last_name": "lname"}}
    out = run_pipeline_rename_map(sample, opts)
    for row in out:
        print(row)


if __name__ == "__main__":  # pragma: no cover
    _smoke_test()
