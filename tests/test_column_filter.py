"""Tests for querypath/column_filter.py."""
import pytest
from querypath.column_filter import (
    apply_include,
    apply_exclude,
    apply_include_pattern,
    apply_exclude_pattern,
    parse_column_filter_spec,
    run_column_filter,
)

ROWS = [
    {"id": 1, "name": "Alice", "dept": "Eng", "salary": 90000},
    {"id": 2, "name": "Bob",   "dept": "HR",  "salary": 70000},
    {"id": 3, "name": "Carol", "dept": "Eng", "salary": 95000},
]


def test_include_keeps_only_listed_columns():
    result = apply_include(ROWS, ["id", "name"])
    assert all(set(r.keys()) == {"id", "name"} for r in result)


def test_include_preserves_order():
    result = apply_include(ROWS, ["name", "id"])
    assert list(result[0].keys()) == ["name", "id"]


def test_include_missing_column_is_ignored():
    result = apply_include(ROWS, ["id", "nonexistent"])
    assert all(set(r.keys()) == {"id"} for r in result)


def test_include_empty_list_returns_empty_dicts():
    result = apply_include(ROWS, [])
    assert result == [{}, {}, {}]


def test_exclude_drops_listed_columns():
    result = apply_exclude(ROWS, ["salary"])
    assert all("salary" not in r for r in result)
    assert all("id" in r for r in result)


def test_exclude_multiple_columns():
    result = apply_exclude(ROWS, ["dept", "salary"])
    assert all(set(r.keys()) == {"id", "name"} for r in result)


def test_exclude_nonexistent_column_is_noop():
    result = apply_exclude(ROWS, ["ghost"])
    assert result == ROWS


def test_include_pattern_wildcard():
    rows = [{"first_name": "A", "last_name": "B", "age": 30}]
    result = apply_include_pattern(rows, "*_name")
    assert all(set(r.keys()) == {"first_name", "last_name"} for r in result)


def test_include_pattern_no_match_returns_empty_dicts():
    result = apply_include_pattern(ROWS, "zzz*")
    assert result == [{}, {}, {}]


def test_exclude_pattern_drops_matching():
    rows = [{"tmp_a": 1, "tmp_b": 2, "keep": 3}]
    result = apply_exclude_pattern(rows, "tmp_*")
    assert result == [{"keep": 3}]


def test_exclude_pattern_empty_rows_returns_empty():
    assert apply_exclude_pattern([], "*") == []


def test_parse_column_filter_spec_none():
    assert parse_column_filter_spec(None) is None


def test_parse_column_filter_spec_extracts_keys():
    opts = {"include": ["id"], "other_key": True}
    spec = parse_column_filter_spec(opts)
    assert spec == {"include": ["id"]}


def test_parse_column_filter_spec_no_relevant_keys():
    assert parse_column_filter_spec({"limit": 10}) is None


def test_run_column_filter_no_spec():
    assert run_column_filter(ROWS, None) is ROWS


def test_run_column_filter_include_then_exclude():
    spec = {"include": ["id", "name", "dept"], "exclude": ["dept"]}
    result = run_column_filter(ROWS, spec)
    assert all(set(r.keys()) == {"id", "name"} for r in result)


def test_run_column_filter_exclude_pattern():
    spec = {"exclude_pattern": "s*"}
    result = run_column_filter(ROWS, spec)
    assert all("salary" not in r for r in result)
