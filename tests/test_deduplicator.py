import pytest
from querypath.deduplicator import (
    apply_distinct,
    apply_distinct_on,
    parse_distinct_spec,
)

ROWS = [
    {"city": "London", "dept": "Eng", "sal": 90},
    {"city": "London", "dept": "Eng", "sal": 90},
    {"city": "Paris", "dept": "Eng", "sal": 80},
    {"city": "London", "dept": "HR", "sal": 70},
    {"city": "Paris", "dept": "HR", "sal": 60},
]


def test_distinct_removes_exact_duplicates():
    result = apply_distinct(ROWS)
    assert len(result) == 4


def test_distinct_preserves_order():
    result = apply_distinct(ROWS)
    assert result[0] == {"city": "London", "dept": "Eng", "sal": 90}


def test_distinct_no_duplicates_unchanged():
    rows = [{"a": 1}, {"a": 2}]
    assert apply_distinct(rows) == rows


def test_distinct_on_single_column_keep_first():
    result = apply_distinct_on(ROWS, ["city"])
    cities = [r["city"] for r in result]
    assert cities == ["London", "Paris"]


def test_distinct_on_single_column_keep_last():
    result = apply_distinct_on(ROWS, ["city"], keep="last")
    cities = [r["city"] for r in result]
    assert cities == ["London", "Paris"]
    # last London row has sal=70
    london = next(r for r in result if r["city"] == "London")
    assert london["sal"] == 70


def test_distinct_on_multiple_columns():
    result = apply_distinct_on(ROWS, ["city", "dept"])
    assert len(result) == 4


def test_distinct_on_empty_columns_returns_all():
    result = apply_distinct_on(ROWS, [])
    assert result == ROWS


def test_parse_distinct_spec_none():
    assert parse_distinct_spec(None) is None


def test_parse_distinct_spec_string():
    assert parse_distinct_spec("city, dept") == ["city", "dept"]


def test_parse_distinct_spec_list():
    assert parse_distinct_spec(["city", "dept"]) == ["city", "dept"]


def test_parse_distinct_spec_unknown_type_returns_none():
    assert parse_distinct_spec(123) is None
