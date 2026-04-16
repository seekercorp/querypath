"""Integration tests: run_pipeline with window function specs."""
import pytest
from querypath.pipeline import run_pipeline

DATA = [
    {"dept": "eng", "name": "Alice", "salary": 90},
    {"dept": "eng", "name": "Bob",   "salary": 70},
    {"dept": "hr",  "name": "Carol", "salary": 80},
    {"dept": "hr",  "name": "Dave",  "salary": 60},
]


def test_pipeline_row_number_added():
    plan = {
        "window": [{"fn": "row_number", "col": "rn", "partition": ["dept"], "order": "salary"}]
    }
    result = run_pipeline(DATA, plan)
    assert all("rn" in r for r in result)
    eng = [r["rn"] for r in result if r["dept"] == "eng"]
    assert sorted(eng) == [1, 2]


def test_pipeline_rank_added():
    plan = {
        "window": [{"fn": "rank", "col": "rnk", "partition": ["dept"], "order": "salary"}]
    }
    result = run_pipeline(DATA, plan)
    assert all("rnk" in r for r in result)


def test_pipeline_lag_added():
    plan = {
        "window": [{"fn": "lag", "col": "prev_salary", "source": "salary", "partition": ["dept"], "order": "salary"}]
    }
    result = run_pipeline(DATA, plan)
    assert all("prev_salary" in r for r in result)
    # first in each partition should be None
    none_count = sum(1 for r in result if r["prev_salary"] is None)
    assert none_count == 2


def test_pipeline_lead_added():
    plan = {
        "window": [{"fn": "lead", "col": "next_salary", "source": "salary", "partition": ["dept"], "order": "salary"}]
    }
    result = run_pipeline(DATA, plan)
    none_count = sum(1 for r in result if r["next_salary"] is None)
    assert none_count == 2


def test_pipeline_window_then_limit():
    plan = {
        "window": [{"fn": "row_number", "col": "rn", "partition": [], "order": "salary"}],
        "limit": 2,
    }
    result = run_pipeline(DATA, plan)
    assert len(result) == 2


def test_pipeline_no_window_unchanged():
    plan = {}
    result = run_pipeline(DATA, plan)
    assert len(result) == len(DATA)
    assert "rn" not in result[0]
