"""Column transformation: rename and computed columns."""

import operator
import re

_OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}

_EXPR_RE = re.compile(
    r'^([\w.]+)\s*([+\-*/])\s*([\w.]+)$'
)


def _resolve(row: dict, token: str):
    """Return numeric value of a token (field name or literal)."""
    try:
        return float(token)
    except ValueError:
        val = row.get(token)
        if val is None:
            raise KeyError(f"Field {token!r} not found in row")
        return float(val)


def apply_rename(rows: list[dict], old: str, new: str) -> list[dict]:
    """Rename a column in every row."""
    out = []
    for row in rows:
        row = dict(row)
        if old in row:
            row[new] = row.pop(old)
        out.append(row)
    return out


def apply_computed_column(rows: list[dict], expr: str, alias: str) -> list[dict]:
    """Add a computed column from a simple arithmetic expression."""
    m = _EXPR_RE.match(expr.strip())
    if not m:
        raise ValueError(f"Cannot parse expression: {expr!r}")
    left_tok, op_sym, right_tok = m.group(1), m.group(2), m.group(3)
    op_fn = _OPS[op_sym]
    out = []
    for row in rows:
        row = dict(row)
        try:
            row[alias] = op_fn(_resolve(row, left_tok), _resolve(row, right_tok))
        except (KeyError, TypeError, ZeroDivisionError):
            row[alias] = None
        out.append(row)
    return out


def parse_alias(expr: str):
    """Parse 'expr AS alias' → (expr, alias). Returns (expr, None) if no alias."""
    m = re.match(r'^(.+?)\s+[Aa][Ss]\s+(\w+)$', expr.strip())
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return expr.strip(), None
