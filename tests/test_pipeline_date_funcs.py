"""Integration-style tests for date_funcs running inside a pipeline."""

import pytest
from querypath.date_funcs import run_pipeline_with_date_funcs
from querypath.sorter import apply_order_by
from querypath.query_engine import QueryEngine


SAMPLE_ROWS = [
    {"id": 1, "name": "Alice", "hired": "2019-03-15"},
    {"id": 2, "name": "Bob",   "hired": "2021-11-01"},
    {"id": 3, "name": "Carol", "hired": "2020-07-22"},
    {"id": 4, "name": "Dave",  "hired": None},
]


def _run(rows, specs):
    return run_pipeline_with_date_funcs(rows, {"date_funcs": specs})


def test_pipeline_extracts_year_for_all_rows():
    result = _run(SAMPLE_ROWS, [{"func": "year", "column": "hired", "alias": "hire_year"}])
    assert result[0]["hire_year"] == 2019
    assert result[1]["hire_year"] == 2021
    assert result[2]["hire_year"] == 2020


def test_pipeline_none_value_yields_none_alias():
    result = _run(SAMPLE_ROWS, [{"func": "year", "column": "hired", "alias": "hire_year"}])
    assert result[3]["hire_year"] is None


def test_pipeline_multiple_date_funcs():
    specs = [
        {"func": "year",  "column": "hired", "alias": "yr"},
        {"func": "month", "column": "hired", "alias": "mo"},
    ]
    result = _run(SAMPLE_ROWS[:1], specs)
    assert result[0]["yr"] == 2019
    assert result[0]["mo"] == 3


def test_pipeline_original_columns_preserved():
    result = _run(SAMPLE_ROWS, [{"func": "day", "column": "hired", "alias": "hire_day"}])
    for orig, new in zip(SAMPLE_ROWS, result):
        assert new["id"] == orig["id"]
        assert new["name"] == orig["name"]
        assert new["hired"] == orig["hired"]


def test_pipeline_then_sort_by_derived_column():
    result = _run(SAMPLE_ROWS[:3], [{"func": "year", "column": "hired", "alias": "yr"}])
    sorted_rows = apply_order_by(result, "yr", "asc")
    years = [r["yr"] for r in sorted_rows]
    assert years == sorted(years)


def test_pipeline_date_diff_tenure():
    rows = [
        {"name": "Alice", "start": "2020-01-01", "end": "2020-01-11"},
    ]
    from querypath.date_funcs import fn_date_diff
    diff = fn_date_diff(rows[0]["end"], rows[0]["start"], "days")
    assert diff == 10
