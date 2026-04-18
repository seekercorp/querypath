import pytest
from querypath.nulls import (
    coalesce, nullif,
    apply_coalesce, apply_nullif,
    filter_is_null, filter_is_not_null,
    parse_null_spec, apply_null_spec,
)


def test_coalesce_returns_first_non_none():
    assert coalesce(None, None, 3, 4) == 3


def test_coalesce_all_none_returns_none():
    assert coalesce(None, None) is None


def test_coalesce_first_value():
    assert coalesce(1, 2) == 1


def test_nullif_equal_returns_none():
    assert nullif("N/A", "N/A") is None


def test_nullif_not_equal_returns_value():
    assert nullif("hello", "N/A") == "hello"


ROWS = [
    {"a": None, "b": 10, "c": 99},
    {"a": 5,    "b": None, "c": 99},
    {"a": None, "b": None, "c": 7},
]


def test_apply_coalesce_picks_first_non_none():
    result = apply_coalesce(ROWS, "a", ["b", "c"], "val")
    assert result[0]["val"] == 10
    assert result[1]["val"] == 5
    assert result[2]["val"] == 7


def test_apply_coalesce_does_not_mutate():
    original = [{"a": None, "b": 1}]
    apply_coalesce(original, "a", ["b"], "out")
    assert "out" not in original[0]


def test_apply_nullif_replaces_matching():
    rows = [{"score": -1}, {"score": 5}]
    result = apply_nullif(rows, "score", -1, "score")
    assert result[0]["score"] is None
    assert result[1]["score"] == 5


def test_filter_is_null_keeps_none():
    rows = [{"x": None}, {"x": 1}, {"x": None}]
    assert len(filter_is_null(rows, "x")) == 2


def test_filter_is_not_null_excludes_none():
    rows = [{"x": None}, {"x": 1}, {"x": 2}]
    assert len(filter_is_not_null(rows, "x")) == 2


def test_filter_is_null_missing_field_treated_as_null():
    rows = [{"y": 1}, {"x": None}]
    assert len(filter_is_null(rows, "x")) == 2


def test_parse_null_spec_coalesce():
    spec = parse_null_spec({"coalesce": {"field": "a", "fallbacks": ["b"], "dest": "v"}})
    assert spec["op"] == "coalesce"


def test_parse_null_spec_is_null():
    spec = parse_null_spec({"is_null": "name"})
    assert spec == {"op": "is_null", "field": "name"}


def test_parse_null_spec_none():
    assert parse_null_spec({}) is None


def test_apply_null_spec_is_not_null():
    rows = [{"v": 1}, {"v": None}]
    result = apply_null_spec(rows, {"op": "is_not_null", "field": "v"})
    assert result == [{"v": 1}]
