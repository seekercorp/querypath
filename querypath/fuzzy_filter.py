"""Fuzzy/pattern matching filter for string fields."""
import re
from typing import List, Dict, Any, Optional


def _like_to_regex(pattern: str) -> re.Pattern:
    """Convert SQL LIKE pattern to regex. % = any chars, _ = single char."""
    escaped = re.escape(pattern)
    escaped = escaped.replace(r"\%", ".*").replace(r"\_", ".")
    return re.compile(f"^{escaped}$", re.IGNORECASE)


def apply_like(rows: List[Dict[str, Any]], column: str, pattern: str) -> List[Dict[str, Any]]:
    """Filter rows where column matches SQL LIKE pattern."""
    regex = _like_to_regex(pattern)
    return [r for r in rows if regex.match(str(r.get(column, "")))]


def apply_not_like(rows: List[Dict[str, Any]], column: str, pattern: str) -> List[Dict[str, Any]]:
    """Filter rows where column does NOT match SQL LIKE pattern."""
    regex = _like_to_regex(pattern)
    return [r for r in rows if not regex.match(str(r.get(column, "")))]


def apply_regex_filter(rows: List[Dict[str, Any]], column: str, pattern: str) -> List[Dict[str, Any]]:
    """Filter rows where column matches a raw regex pattern."""
    regex = re.compile(pattern)
    return [r for r in rows if regex.search(str(r.get(column, "")))]


def parse_fuzzy_spec(spec: Optional[str]) -> Optional[Dict[str, Any]]:
    """Parse a fuzzy filter spec string like 'name LIKE %john%' or 'email REGEX ^a'."""
    if not spec:
        return None
    like_match = re.match(r"(\w+)\s+(NOT LIKE|LIKE|REGEX)\s+(.+)", spec, re.IGNORECASE)
    if not like_match:
        return None
    column, op, pattern = like_match.group(1), like_match.group(2).upper(), like_match.group(3).strip()
    return {"column": column, "op": op, "pattern": pattern}


def apply_fuzzy_spec(rows: List[Dict[str, Any]], spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    op = spec["op"]
    if op == "LIKE":
        return apply_like(rows, spec["column"], spec["pattern"])
    elif op == "NOT LIKE":
        return apply_not_like(rows, spec["column"], spec["pattern"])
    elif op == "REGEX":
        return apply_regex_filter(rows, spec["column"], spec["pattern"])
    return rows
