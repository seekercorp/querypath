"""Date and time functions for computed columns and filters."""

from datetime import datetime, date
from typing import Any, List, Dict, Optional

_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d/%m/%Y",
    "%m/%d/%Y",
]


def _parse_date(value: Any) -> Optional[datetime]:
    """Try to parse a string value into a datetime object."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if not isinstance(value, str):
        return None
    for fmt in _FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def fn_year(value: Any) -> Optional[int]:
    dt = _parse_date(value)
    return dt.year if dt else None


def fn_month(value: Any) -> Optional[int]:
    dt = _parse_date(value)
    return dt.month if dt else None


def fn_day(value: Any) -> Optional[int]:
    dt = _parse_date(value)
    return dt.day if dt else None


def fn_date_diff(value: Any, other: Any, unit: str = "days") -> Optional[int]:
    """Return the difference between two dates in the given unit."""
    dt1 = _parse_date(value)
    dt2 = _parse_date(other)
    if dt1 is None or dt2 is None:
        return None
    delta = dt1 - dt2
    if unit == "days":
        return delta.days
    if unit == "seconds":
        return int(delta.total_seconds())
    if unit == "hours":
        return int(delta.total_seconds() // 3600)
    return delta.days


def fn_format_date(value: Any, fmt: str = "%Y-%m-%d") -> Optional[str]:
    dt = _parse_date(value)
    return dt.strftime(fmt) if dt else None


DATE_FUNCTIONS = {
    "year": fn_year,
    "month": fn_month,
    "day": fn_day,
    "format_date": fn_format_date,
}


def extract_date_func_specs(options: dict) -> List[Dict]:
    """Parse date function specs from CLI options.

    Expected format: [{"func": "year", "column": "dob", "alias": "birth_year"}, ...]
    """
    return options.get("date_funcs", []) or []


def run_pipeline_with_date_funcs(rows: List[Dict], options: dict) -> List[Dict]:
    specs = extract_date_func_specs(options)
    if not specs:
        return rows
    result = []
    for row in rows:
        new_row = dict(row)
        for spec in specs:
            func_name = spec.get("func", "")
            col = spec.get("column", "")
            alias = spec.get("alias") or f"{func_name}_{col}"
            fn = DATE_FUNCTIONS.get(func_name)
            if fn and col in new_row:
                new_row[alias] = fn(new_row[col])
        result.append(new_row)
    return result
