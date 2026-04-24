"""Tests for querypath.type_inspector."""
import pytest
from querypath.type_inspector import (
    _infer_scalar,
    _merge_types,
    infer_column_types,
    summarise_columns,
)


# ---------------------------------------------------------------------------
# _infer_scalar
# ---------------------------------------------------------------------------

def test_infer_none():
    assert _infer_scalar(None) == "null"

def test_infer_bool():
    assert _infer_scalar(True) == "bool"
    assert _infer_scalar(False) == "bool"

def test_infer_int():
    assert _infer_scalar(42) == "int"

def test_infer_float():
    assert _infer_scalar(3.14) == "float"

def test_infer_str():
    assert _infer_scalar("hello") == "str"


# ---------------------------------------------------------------------------
# _merge_types
# ---------------------------------------------------------------------------

def test_merge_same_type():
    assert _merge_types("int", "int") == "int"

def test_merge_int_float_widens_to_float():
    assert _merge_types("int", "float") == "float"

def test_merge_null_with_int_widens_to_int():
    assert _merge_types("null", "int") == "int"

def test_merge_bool_with_str_widens_to_str():
    assert _merge_types("bool", "str") == "str"


# ---------------------------------------------------------------------------
# infer_column_types
# ---------------------------------------------------------------------------

def test_infer_empty_rows_returns_empty():
    assert infer_column_types([]) == {}

def test_infer_all_ints():
    rows = [{"age": 10}, {"age": 20}, {"age": 30}]
    assert infer_column_types(rows) == {"age": "int"}

def test_infer_mixed_int_float():
    rows = [{"val": 1}, {"val": 2.5}]
    assert infer_column_types(rows) == {"val": "float"}

def test_infer_null_widens_to_real_type():
    rows = [{"x": None}, {"x": "hello"}]
    assert infer_column_types(rows) == {"x": "str"}

def test_infer_all_null_stays_null():
    rows = [{"x": None}, {"x": None}]
    assert infer_column_types(rows) == {"x": "null"}

def test_infer_multiple_columns():
    rows = [
        {"name": "Alice", "score": 95, "active": True},
        {"name": "Bob",   "score": 87, "active": False},
    ]
    result = infer_column_types(rows)
    assert result["name"] == "str"
    assert result["score"] == "int"
    assert result["active"] == "bool"


# ---------------------------------------------------------------------------
# summarise_columns
# ---------------------------------------------------------------------------

def test_summarise_empty_returns_empty():
    assert summarise_columns([]) == []

def test_summarise_counts_nulls():
    rows = [{"city": "NYC"}, {"city": None}, {"city": "LA"}]
    summaries = {s["column"]: s for s in summarise_columns(rows)}
    assert summaries["city"]["null_count"] == 1
    assert summaries["city"]["non_null_count"] == 2

def test_summarise_sample_is_first_non_null():
    rows = [{"val": None}, {"val": 42}, {"val": 7}]
    summaries = {s["column"]: s for s in summarise_columns(rows)}
    assert summaries["val"]["sample"] == 42

def test_summarise_all_null_sample_is_none():
    rows = [{"x": None}, {"x": None}]
    summaries = {s["column"]: s for s in summarise_columns(rows)}
    assert summaries["x"]["sample"] is None

def test_summarise_type_reported():
    rows = [{"n": 1.1}, {"n": 2.2}]
    summaries = {s["column"]: s for s in summarise_columns(rows)}
    assert summaries["n"]["type"] == "float"
