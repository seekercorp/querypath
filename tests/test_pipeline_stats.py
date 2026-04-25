"""Integration tests for querypath/pipeline_stats.py"""
import pytest
from querypath.pipeline_stats import extract_stats_spec, run_pipeline_with_stats

ROWS = [
    {"dept": "Eng",  "salary": 90000, "age": 32},
    {"dept": "Eng",  "salary": 85000, "age": 28},
    {"dept": "HR",   "salary": 70000, "age": 45},
    {"dept": "HR",   "salary": 72000, "age": None},
]


# ── extract_stats_spec ────────────────────────────────────────────────────────

def test_extract_stats_spec_none_opts():
    assert extract_stats_spec(None) is None


def test_extract_stats_spec_missing_key():
    assert extract_stats_spec({"limit": 10}) is None


def test_extract_stats_spec_list():
    result = extract_stats_spec({"stats": ["salary", "age"]})
    assert result == ["salary", "age"]


def test_extract_stats_spec_string():
    result = extract_stats_spec({"stats": "salary, age"})
    assert result == ["salary", "age"]


def test_extract_stats_spec_strips_whitespace():
    result = extract_stats_spec({"stats": "  salary  ,  age  "})
    assert result == ["salary", "age"]


# ── run_pipeline_with_stats ───────────────────────────────────────────────────

def test_no_spec_returns_rows_unchanged():
    result = run_pipeline_with_stats(ROWS, {})
    assert result is ROWS


def test_none_opts_returns_rows_unchanged():
    result = run_pipeline_with_stats(ROWS, None)
    assert result is ROWS


def test_stats_returns_one_row_per_field():
    result = run_pipeline_with_stats(ROWS, {"stats": ["salary", "age"]})
    assert len(result) == 2
    assert result[0]["field"] == "salary"
    assert result[1]["field"] == "age"


def test_stats_salary_values():
    result = run_pipeline_with_stats(ROWS, {"stats": ["salary"]})
    row = result[0]
    assert row["count"] == 4
    assert row["min"] == 70000.0
    assert row["max"] == 90000.0
    assert row["mean"] == (90000 + 85000 + 70000 + 72000) / 4


def test_stats_age_skips_none():
    result = run_pipeline_with_stats(ROWS, {"stats": "age"})
    row = result[0]
    assert row["count"] == 3   # one None
    assert row["numeric_count"] == 3


def test_stats_empty_rows():
    result = run_pipeline_with_stats([], {"stats": ["salary"]})
    assert result[0]["count"] == 0
    assert result[0]["min"] is None
