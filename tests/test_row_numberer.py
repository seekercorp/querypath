"""Tests for querypath/row_numberer.py"""
import pytest
from querypath.row_numberer import (
    apply_row_index,
    apply_grouped_index,
    parse_row_index_spec,
    run_pipeline_with_row_index,
)

ROWS = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "eng"},
    {"name": "Carol", "dept": "hr"},
    {"name": "Dan", "dept": "hr"},
    {"name": "Eve", "dept": "eng"},
]


def test_apply_row_index_default_column():
    result = apply_row_index(ROWS)
    assert [r["_row_index"] for r in result] == [1, 2, 3, 4, 5]


def test_apply_row_index_custom_column():
    result = apply_row_index(ROWS, column="idx")
    assert all("idx" in r for r in result)
    assert result[0]["idx"] == 1


def test_apply_row_index_custom_start():
    result = apply_row_index(ROWS, start=0)
    assert result[0]["_row_index"] == 0
    assert result[-1]["_row_index"] == 4


def test_apply_row_index_does_not_mutate():
    original = [{"a": 1}]
    apply_row_index(original)
    assert "_row_index" not in original[0]


def test_apply_row_index_empty():
    assert apply_row_index([]) == []


def test_apply_grouped_index_resets_per_partition():
    result = apply_grouped_index(ROWS, partition_by="dept")
    # eng: Alice=1, Bob=2, Eve=3  |  hr: Carol=1, Dan=2
    assert result[0]["_group_index"] == 1  # Alice / eng
    assert result[1]["_group_index"] == 2  # Bob / eng
    assert result[2]["_group_index"] == 1  # Carol / hr
    assert result[3]["_group_index"] == 2  # Dan / hr
    assert result[4]["_group_index"] == 3  # Eve / eng


def test_apply_grouped_index_custom_column():
    result = apply_grouped_index(ROWS, partition_by="dept", column="grp")
    assert "grp" in result[0]


def test_apply_grouped_index_does_not_mutate():
    original = [{"dept": "x"}]
    apply_grouped_index(original, partition_by="dept")
    assert "_group_index" not in original[0]


def test_parse_row_index_spec_none_opts():
    assert parse_row_index_spec(None) is None


def test_parse_row_index_spec_missing_key():
    assert parse_row_index_spec({"other": "value"}) is None


def test_parse_row_index_spec_bool_true_uses_default_name():
    spec = parse_row_index_spec({"row_index": True})
    assert spec["column"] == "_row_index"


def test_parse_row_index_spec_string_name():
    spec = parse_row_index_spec({"row_index": "idx"})
    assert spec["column"] == "idx"


def test_parse_row_index_spec_defaults():
    spec = parse_row_index_spec({"row_index": True})
    assert spec["start"] == 1
    assert spec["partition_by"] is None


def test_parse_row_index_spec_custom_start():
    spec = parse_row_index_spec({"row_index": True, "row_index_start": "0"})
    assert spec["start"] == 0


def test_run_pipeline_no_opts_returns_unchanged():
    result = run_pipeline_with_row_index(ROWS)
    assert result == ROWS


def test_run_pipeline_adds_index():
    opts = {"row_index": "n"}
    result = run_pipeline_with_row_index(ROWS, opts)
    assert result[2]["n"] == 3


def test_run_pipeline_with_partition():
    opts = {"row_index": "gi", "row_index_partition": "dept"}
    result = run_pipeline_with_row_index(ROWS, opts)
    assert result[2]["gi"] == 1  # Carol – first in hr
