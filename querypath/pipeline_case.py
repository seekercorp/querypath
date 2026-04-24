"""Pipeline integration for CASE expression computed columns."""
from typing import Any, Dict, List, Optional

from querypath.case_expr import apply_case_column, parse_case_spec


def extract_case_specs(opts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return a list of case specs from pipeline options.

    Supports a single spec under ``case`` or multiple under ``cases``.

    Args:
        opts: Pipeline options dict.

    Returns:
        List of case spec dicts (may be empty).
    """
    specs: List[Dict[str, Any]] = []

    single = parse_case_spec(opts)
    if single is not None:
        specs.append(single)

    for item in opts.get("cases", []):
        specs.append(item)

    return specs


def run_pipeline_with_case(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Apply zero or more CASE computed columns to *rows*.

    Args:
        rows: Input data rows.
        opts: Pipeline options dict.  Keys ``case`` or ``cases`` are consumed.

    Returns:
        Rows with any CASE-derived columns appended.
    """
    if not opts:
        return rows

    specs = extract_case_specs(opts)
    for spec in specs:
        alias = spec["alias"]
        when_thens = [
            ((wt["field"], wt["op"], wt["value"]), wt["result"])
            for wt in spec.get("when_thens", [])
        ]
        else_value = spec.get("else", None)
        rows = apply_case_column(rows, alias, when_thens, else_value)

    return rows
