"""Tests for querypath/date_funcs.py"""

import pytest
from querypath.date_funcs import (
    fn_year,
    fn_month,
    fn_day,
    fn_date_diff,
    fn_format_date,
    extract_date_func_specs,
    run_pipeline_with_date_funcs,
)


def test_year_from_iso_string():
    assert fn_year("2023-07-15") == 2023


def test_month_from_iso_string():
    assert fn_month("2023-07-15") == 7


def test_day_from_iso_string():
    assert fn_day("2023-07-15") == 15


def test_year_from_datetime_string():
    assert fn_year("2021-01-20T08:30:00") == 2021


def test_year_none_on_invalid():
    assert fn_year("not-a-date") is None


def test_year_none_on_none():
    assert fn_year(None) is None


def test_date_diff_days():
    assert fn_date_diff("2023-07-20", "2023-07-15", "days") == 5


def test_date_diff_negative():
    assert fn_date_diff("2023-07-10", "2023-07-15", "days") == -5


def test_date_diff_hours():
    result = fn_date_diff("2023-07-16", "2023-07-15", "hours")
    assert result == 24


def test_date_diff_invalid_returns_none():
    assert fn_date_diff("bad", "2023-07-15") is None


def test_format_date_custom_format():
    assert fn_format_date("2023-07-15", "%d/%m/%Y") == "15/07/2023"


def test_format_date_default_format():
    assert fn_format_date("2023-07-15") == "2023-07-15"


def test_format_date_none_on_invalid():
    assert fn_format_date("not-a-date") is None


def test_extract_date_func_specs_present():
    specs = [{"func": "year", "column": "dob", "alias": "birth_year"}]
    result = extract_date_func_specs({"date_funcs": specs})
    assert result == specs


def test_extract_date_func_specs_missing():
    assert extract_date_func_specs({}) == []


def test_run_pipeline_adds_year_column():
    rows = [{"name": "Alice", "dob": "1990-03-25"}]
    opts = {"date_funcs": [{"func": "year", "column": "dob", "alias": "birth_year"}]}
    result = run_pipeline_with_date_funcs(rows, opts)
    assert result[0]["birth_year"] == 1990


def test_run_pipeline_no_specs_returns_unchanged():
    rows = [{"name": "Alice", "dob": "1990-03-25"}]
    result = run_pipeline_with_date_funcs(rows, {})
    assert result == rows


def test_run_pipeline_auto_alias():
    rows = [{"joined": "2020-06-01"}]
    opts = {"date_funcs": [{"func": "month", "column": "joined"}]}
    result = run_pipeline_with_date_funcs(rows, opts)
    assert "month_joined" in result[0]
    assert result[0]["month_joined"] == 6


def test_run_pipeline_missing_column_skips():
    rows = [{"name": "Bob"}]
    opts = {"date_funcs": [{"func": "year", "column": "dob", "alias": "yr"}]}
    result = run_pipeline_with_date_funcs(rows, opts)
    assert "yr" not in result[0]
