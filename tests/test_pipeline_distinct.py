"""Integration: deduplication wired through run_pipeline."""
import pytest
from querypath.pipeline import run_pipeline


ROWS = [
    {"city": "London", "score": 10},
    {"city": "London", "score": 10},
    {"city": "Paris", "score": 20},
    {"city": "London", "score": 30},
]


def _run(rows, **kwargs):
    return run_pipeline(list(rows), **kwargs)


def test_distinct_removes_duplicates():
    result = _run(ROWS, distinct=True)
    assert len(result) == 3


def test_distinct_on_city_keeps_first():
    result = _run(ROWS, distinct_on=["city"])
    assert len(result) == 2
    london = next(r for r in result if r["city"] == "London")
    assert london["score"] == 10


def test_distinct_on_city_keeps_last():
    result = _run(ROWS, distinct_on=["city"], distinct_keep="last")
    assert len(result) == 2
    london = next(r for r in result if r["city"] == "London")
    assert london["score"] == 30


def test_no_distinct_returns_all():
    result = _run(ROWS)
    assert len(result) == 4


def test_distinct_combined_with_limit():
    result = _run(ROWS, distinct=True, limit=2)
    assert len(result) == 2
