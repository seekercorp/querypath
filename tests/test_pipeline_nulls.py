import pytest
from querypath.nulls import apply_null_spec, parse_null_spec


DATA = [
    {"name": "Alice", "city": "NYC",  "backup": "BOS"},
    {"name": "Bob",   "city": None,   "backup": "LA"},
    {"name": "Carol", "city": None,   "backup": None},
]


def _run(rows, options):
    spec = parse_null_spec(options)
    if spec:
        return apply_null_spec(rows, spec)
    return rows


def test_coalesce_fills_missing_city():
    result = _run(DATA, {"coalesce": {"field": "city", "fallbacks": ["backup"], "dest": "location"}})
    assert result[0]["location"] == "NYC"
    assert result[1]["location"] == "LA"
    assert result[2]["location"] is None


def test_is_null_filters_to_missing_city():
    result = _run(DATA, {"is_null": "city"})
    assert len(result) == 2
    assert all(r["city"] is None for r in result)


def test_is_not_null_filters_to_present_city():
    result = _run(DATA, {"is_not_null": "city"})
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_nullif_blanks_sentinel():
    rows = [{"score": 0}, {"score": 5}, {"score": 0}]
    result = _run(rows, {"nullif": {"field": "score", "null_value": 0, "dest": "score"}})
    assert result[0]["score"] is None
    assert result[1]["score"] == 5
    assert result[2]["score"] is None


def test_no_spec_returns_rows_unchanged():
    result = _run(DATA, {})
    assert result is DATA
