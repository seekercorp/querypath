"""Tests for querypath/column_stats.py"""
import math
import pytest
from querypath.column_stats import (
    stat_min, stat_max, stat_mean, stat_median, stat_stddev,
    stat_count_non_null, compute_column_stats, apply_column_stats,
)

ROWS = [
    {"name": "Alice", "score": 10, "age": 30},
    {"name": "Bob",   "score": 20, "age": 25},
    {"name": "Carol", "score": 30, "age": None},
    {"name": "Dave",  "score": 40, "age": 35},
    {"name": "Eve",   "score": None, "age": 28},
]


def test_stat_min():
    assert stat_min([3.0, 1.0, 2.0]) == 1.0


def test_stat_min_empty_returns_none():
    assert stat_min([]) is None


def test_stat_max():
    assert stat_max([3.0, 1.0, 2.0]) == 3.0


def test_stat_mean():
    assert stat_mean([1.0, 2.0, 3.0]) == 2.0


def test_stat_mean_empty_returns_none():
    assert stat_mean([]) is None


def test_stat_median_odd():
    assert stat_median([1.0, 3.0, 2.0]) == 2.0


def test_stat_median_even():
    assert stat_median([1.0, 2.0, 3.0, 4.0]) == 2.5


def test_stat_median_empty_returns_none():
    assert stat_median([]) is None


def test_stat_stddev_basic():
    result = stat_stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert result is not None
    assert round(result, 4) == 2.1381


def test_stat_stddev_single_returns_none():
    assert stat_stddev([5.0]) is None


def test_stat_count_non_null_skips_none():
    assert stat_count_non_null(ROWS, "age") == 4


def test_stat_count_non_null_all_present():
    assert stat_count_non_null(ROWS, "name") == 5


def test_compute_column_stats_score():
    stats = compute_column_stats(ROWS, "score")
    assert stats["field"] == "score"
    assert stats["count"] == 4          # Eve has None
    assert stats["numeric_count"] == 4
    assert stats["min"] == 10.0
    assert stats["max"] == 40.0
    assert stats["mean"] == 25.0
    assert stats["median"] == 25.0


def test_compute_column_stats_non_numeric_field():
    stats = compute_column_stats(ROWS, "name")
    assert stats["numeric_count"] == 0
    assert stats["min"] is None
    assert stats["mean"] is None


def test_apply_column_stats_returns_one_row_per_field():
    result = apply_column_stats(ROWS, ["score", "age"])
    assert len(result) == 2
    assert result[0]["field"] == "score"
    assert result[1]["field"] == "age"


def test_apply_column_stats_empty_rows():
    result = apply_column_stats([], ["score"])
    assert result[0]["count"] == 0
    assert result[0]["min"] is None
