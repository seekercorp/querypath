"""Tests for querypath.column_rename_map."""

import pytest
from querypath.column_rename_map import (
    apply_rename_map,
    parse_rename_map_spec,
    run_pipeline_with_rename_map,
)


ROWS = [
    {"first_name": "Alice", "last_name": "Smith", "age": 30},
    {"first_name": "Bob", "last_name": "Jones", "age": 25},
]


# ---------------------------------------------------------------------------
# apply_rename_map
# ---------------------------------------------------------------------------

def test_rename_single_column():
    result = apply_rename_map(ROWS, {"first_name": "name"})
    assert all("name" in r for r in result)
    assert all("first_name" not in r for r in result)


def test_rename_multiple_columns():
    result = apply_rename_map(ROWS, {"first_name": "fname", "last_name": "lname"})
    assert result[0] == {"fname": "Alice", "lname": "Smith", "age": 30}


def test_rename_preserves_unmapped_columns():
    result = apply_rename_map(ROWS, {"first_name": "fname"})
    assert all("last_name" in r for r in result)
    assert all("age" in r for r in result)


def test_rename_empty_map_returns_rows_unchanged():
    result = apply_rename_map(ROWS, {})
    assert result == ROWS


def test_rename_missing_key_in_row_is_skipped():
    rows = [{"a": 1}, {"a": 2, "b": 3}]
    result = apply_rename_map(rows, {"b": "beta"})
    assert result[0] == {"a": 1}
    assert result[1] == {"a": 2, "beta": 3}


def test_rename_does_not_mutate_original():
    original = [{"x": 1}]
    apply_rename_map(original, {"x": "y"})
    assert original[0] == {"x": 1}


# ---------------------------------------------------------------------------
# parse_rename_map_spec
# ---------------------------------------------------------------------------

def test_parse_dict_spec():
    opts = {"rename": {"a": "alpha", "b": "beta"}}
    result = parse_rename_map_spec(opts)
    assert result == {"a": "alpha", "b": "beta"}


def test_parse_list_of_pairs_spec():
    opts = {"rename": [["a", "alpha"], ["b", "beta"]]}
    result = parse_rename_map_spec(opts)
    assert result == {"a": "alpha", "b": "beta"}


def test_parse_none_opts_returns_none():
    assert parse_rename_map_spec(None) is None


def test_parse_missing_key_returns_none():
    assert parse_rename_map_spec({"other": "value"}) is None


def test_parse_empty_dict_returns_none():
    assert parse_rename_map_spec({"rename": {}}) is None


def test_parse_invalid_pairs_skipped():
    opts = {"rename": [["a", "alpha"], ["bad"], "ignored"]}
    result = parse_rename_map_spec(opts)
    assert result == {"a": "alpha"}


# ---------------------------------------------------------------------------
# run_pipeline_with_rename_map
# ---------------------------------------------------------------------------

def test_pipeline_renames_via_dict():
    opts = {"rename": {"first_name": "fname", "last_name": "lname"}}
    result = run_pipeline_with_rename_map(ROWS, opts)
    assert result[0]["fname"] == "Alice"
    assert result[0]["lname"] == "Smith"


def test_pipeline_no_spec_returns_rows_unchanged():
    result = run_pipeline_with_rename_map(ROWS, {})
    assert result == ROWS


def test_pipeline_none_opts_returns_rows_unchanged():
    result = run_pipeline_with_rename_map(ROWS, None)
    assert result == ROWS
