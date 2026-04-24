"""Numeric/math column functions: ROUND, ABS, CEIL, FLOOR, MOD."""

import math
from typing import Any, Dict, List, Optional


def fn_round(value: Any, decimals: int = 0) -> Optional[float]:
    """Round a numeric value to *decimals* decimal places."""
    if value is None:
        return None
    try:
        return round(float(value), decimals)
    except (TypeError, ValueError):
        return None


def fn_abs(value: Any) -> Optional[float]:
    """Return the absolute value."""
    if value is None:
        return None
    try:
        return abs(float(value))
    except (TypeError, ValueError):
        return None


def fn_ceil(value: Any) -> Optional[int]:
    """Return the ceiling (smallest integer >= value)."""
    if value is None:
        return None
    try:
        return math.ceil(float(value))
    except (TypeError, ValueError):
        return None


def fn_floor(value: Any) -> Optional[int]:
    """Return the floor (largest integer <= value)."""
    if value is None:
        return None
    try:
        return math.floor(float(value))
    except (TypeError, ValueError):
        return None


def fn_mod(value: Any, divisor: Any) -> Optional[float]:
    """Return value % divisor.  Returns None if either operand is None or divisor is 0."""
    if value is None or divisor is None:
        return None
    try:
        d = float(divisor)
        if d == 0:
            return None
        return float(value) % d
    except (TypeError, ValueError):
        return None


_FUNCTIONS = {
    "ROUND": fn_round,
    "ABS": fn_abs,
    "CEIL": fn_ceil,
    "FLOOR": fn_floor,
    "MOD": fn_mod,
}


def apply_math_func(
    rows: List[Dict[str, Any]],
    func_name: str,
    source_col: str,
    alias: str,
    extra_arg: Any = None,
) -> List[Dict[str, Any]]:
    """Apply a math function to *source_col* in every row, storing result in *alias*."""
    fn = _FUNCTIONS.get(func_name.upper())
    if fn is None:
        raise ValueError(f"Unknown math function: {func_name!r}")

    result = []
    for row in rows:
        new_row = dict(row)
        val = row.get(source_col)
        if extra_arg is not None:
            new_row[alias] = fn(val, extra_arg)
        else:
            new_row[alias] = fn(val)
        result.append(new_row)
    return result


def parse_math_func_specs(options: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract math-function specs from pipeline options.

    Expected format in *options*::

        "math_funcs": [
            {"func": "ROUND", "col": "price", "alias": "price_r", "arg": 2},
            {"func": "ABS",   "col": "delta", "alias": "abs_delta"}
        ]
    """
    return options.get("math_funcs") or []


def run_pipeline_with_math_funcs(
    rows: List[Dict[str, Any]], options: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Run all math-function transformations declared in *options*."""
    specs = parse_math_func_specs(options)
    for spec in specs:
        rows = apply_math_func(
            rows,
            func_name=spec["func"],
            source_col=spec["col"],
            alias=spec.get("alias", spec["col"]),
            extra_arg=spec.get("arg"),
        )
    return rows
