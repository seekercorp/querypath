"""Integration tests for pipeline_conditional_agg."""
import pytest
from querypath.pipeline_conditional_agg import run_pipeline_with_conditional_agg

ROWS = [
    {"name": "Alice", "dept": "eng",     "salary": 90000},
    {"name": "Bob",   "dept": "eng",     "salary": 80000},
    {"name": "Carol", "dept": "hr",      "salary": 70000},
    {"name": "Dave",  "dept": "hr",      "salary": None},
    {"name": "Eve",   "dept": "finance", "salary": 60000},
]


def _run(opts):
    return run_pipeline_with_conditional_agg(ROWS, opts)


def test_no_opts_returns_rows_unchanged():
    result = _run(None)
    assert result == ROWS


def test_empty_opts_returns_rows_unchanged():
    result = _run({})
    assert result == ROWS


def test_count_if_eng_dept():
    opts = {
        "conditional_agg": {
            "func": "count_if",
            "condition": {"field": "dept", "op": "eq", "value": "eng"},
            "alias": "eng_headcount",
        }
    }
    result = _run(opts)
    assert all(r["eng_headcount"] == 2 for r in result)
    assert result[0]["name"] == "Alice"  # original data intact


def test_sum_if_eng_salary():
    opts = {
        "conditional_agg": {
            "func": "sum_if",
            "field": "salary",
            "condition": {"field": "dept", "op": "eq", "value": "eng"},
            "alias": "eng_total_salary",
        }
    }
    result = _run(opts)
    assert all(r["eng_total_salary"] == 170000 for r in result)


def test_avg_if_non_null_salary():
    opts = {
        "conditional_agg": {
            "func": "avg_if",
            "field": "salary",
            "condition": {"field": "salary", "op": "is_not_null"},
            "alias": "avg_known_salary",
        }
    }
    result = _run(opts)
    # 90000+80000+70000+60000 / 4 = 75000
    assert all(r["avg_known_salary"] == 75000.0 for r in result)


def test_multiple_specs_via_list():
    opts = {
        "conditional_agg": [
            {
                "func": "count_if",
                "condition": {"field": "dept", "op": "eq", "value": "hr"},
                "alias": "hr_count",
            },
            {
                "func": "sum_if",
                "field": "salary",
                "condition": {"field": "salary", "op": "gt", "value": 75000},
                "alias": "high_earner_total",
            },
        ]
    }
    result = _run(opts)
    assert all(r["hr_count"] == 2 for r in result)
    assert all(r["high_earner_total"] == 170000 for r in result)


def test_unknown_func_is_skipped():
    opts = {
        "conditional_agg": {
            "func": "median_if",
            "condition": {"field": "dept", "op": "eq", "value": "eng"},
            "alias": "med",
        }
    }
    result = _run(opts)
    assert "med" not in result[0]
