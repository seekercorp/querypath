"""Tests for querypath.sorter module."""

import pytest
from querypath.sorter import apply_order_by, apply_limit

SAMPLE = [
    {"name": "Charlie", "age": 30, "score": 88.5},
    {"name": "Alice", "age": 25, "score": 95.0},
    {"name": "Bob", "age": 35, "score": 72.0},
    {"name": "Diana", "age": 28, "score": None},
]


def test_order_by_string_asc():
    result = apply_order_by(SAMPLE, "name", ascending=True)
    names = [r["name"] for r in result]
    assert names == ["Alice", "Bob", "Charlie", "Diana"]


def test_order_by_string_desc():
    result = apply_order_by(SAMPLE, "name", ascending=False)
    names = [r["name"] for r in result]
    assert names == ["Diana", "Charlie", "Bob", "Alice"]


def test_order_by_numeric_asc():
    result = apply_order_by(SAMPLE, "age", ascending=True)
    ages = [r["age"] for r in result]
    assert ages == [25, 28, 30, 35]


def test_order_by_numeric_desc():
    result = apply_order_by(SAMPLE, "score", ascending=False)
    # None should be last
    assert result[-1]["score"] is None
    assert result[0]["score"] == 95.0


def test_order_by_none_column_skips():
    result = apply_order_by(SAMPLE, None)
    assert result == SAMPLE


def test_order_by_invalid_column():
    with pytest.raises(ValueError, match="ORDER BY column"):
        apply_order_by(SAMPLE, "nonexistent")


def test_order_by_empty_records():
    assert apply_order_by([], "name") == []


def test_limit_basic():
    result = apply_limit(SAMPLE, limit=2)
    assert len(result) == 2
    assert result[0]["name"] == "Charlie"


def test_limit_with_offset():
    result = apply_limit(SAMPLE, limit=2, offset=1)
    assert len(result) == 2
    assert result[0]["name"] == "Alice"


def test_limit_none_returns_all():
    result = apply_limit(SAMPLE, limit=None)
    assert len(result) == len(SAMPLE)


def test_offset_only():
    result = apply_limit(SAMPLE, offset=3)
    assert len(result) == 1
    assert result[0]["name"] == "Diana"


def test_limit_exceeds_length():
    result = apply_limit(SAMPLE, limit=100)
    assert len(result) == len(SAMPLE)
