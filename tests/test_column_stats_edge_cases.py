"""Edge-case tests for column_stats helpers."""
import math
import pytest
from querypath.column_stats import (
    stat_stddev, stat_median, compute_column_stats, apply_column_stats,
)


def test_stddev_two_values():
    # population sample of [1, 3] → variance = ((1-2)^2 + (3-2)^2) / 1 = 2
    result = stat_stddev([1.0, 3.0])
    assert result is not None
    assert math.isclose(result, math.sqrt(2), rel_tol=1e-9)


def test_stddev_identical_values_is_zero():
    result = stat_stddev([5.0, 5.0, 5.0])
    assert result == 0.0


def test_median_single_element():
    assert stat_median([7.0]) == 7.0


def test_compute_stats_string_numerics_coerced():
    rows = [{"v": "10"}, {"v": "20"}, {"v": "30"}]
    stats = compute_column_stats(rows, "v")
    assert stats["numeric_count"] == 3
    assert stats["mean"] == 20.0


def test_compute_stats_mixed_numeric_and_string():
    rows = [{"v": 1}, {"v": "hello"}, {"v": 3}]
    stats = compute_column_stats(rows, "v")
    assert stats["numeric_count"] == 2
    assert stats["count"] == 3   # non-null count includes "hello"
    assert stats["mean"] == 2.0


def test_apply_column_stats_preserves_order():
    rows = [{"a": 1, "b": 2}]
    result = apply_column_stats(rows, ["b", "a"])
    assert result[0]["field"] == "b"
    assert result[1]["field"] == "a"


def test_compute_stats_all_none():
    rows = [{"x": None}, {"x": None}]
    stats = compute_column_stats(rows, "x")
    assert stats["count"] == 0
    assert stats["min"] is None
    assert stats["mean"] is None
    assert stats["stddev"] is None


def test_compute_stats_missing_field_entirely():
    rows = [{"a": 1}, {"a": 2}]
    stats = compute_column_stats(rows, "b")
    assert stats["count"] == 0
    assert stats["numeric_count"] == 0
