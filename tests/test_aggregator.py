"""Tests for the aggregator module."""
import pytest
from querypath.aggregator import apply_aggregation


RECORDS = [
    {"name": "Alice", "dept": "eng", "salary": 90000},
    {"name": "Bob", "dept": "eng", "salary": 80000},
    {"name": "Carol", "dept": "hr", "salary": 70000},
    {"name": "Dave", "dept": "hr", "salary": 75000},
    {"name": "Eve", "dept": "eng", "salary": 95000},
]


def test_count_all():
    result = apply_aggregation(RECORDS, "COUNT", None)
    assert result == [{"COUNT(*)": 5}]


def test_sum():
    result = apply_aggregation(RECORDS, "SUM", "salary")
    assert result == [{"SUM(salary)": 410000.0}]


def test_avg():
    result = apply_aggregation(RECORDS, "AVG", "salary")
    assert result[0]["AVG(salary)"] == pytest.approx(82000.0)


def test_min():
    result = apply_aggregation(RECORDS, "MIN", "salary")
    assert result == [{"MIN(salary)": 70000.0}]


def test_max():
    result = apply_aggregation(RECORDS, "MAX", "salary")
    assert result == [{"MAX(salary)": 95000.0}]


def test_group_by_count():
    result = apply_aggregation(RECORDS, "COUNT", "salary", group_by="dept")
    by_dept = {r["dept"]: r["COUNT(salary)"] for r in result}
    assert by_dept["eng"] == 3
    assert by_dept["hr"] == 2


def test_group_by_sum():
    result = apply_aggregation(RECORDS, "SUM", "salary", group_by="dept")
    by_dept = {r["dept"]: r["SUM(salary)"] for r in result}
    assert by_dept["eng"] == pytest.approx(265000.0)
    assert by_dept["hr"] == pytest.approx(145000.0)


def test_unsupported_func():
    with pytest.raises(ValueError, match="Unsupported"):
        apply_aggregation(RECORDS, "MEDIAN", "salary")


def test_empty_records():
    result = apply_aggregation([], "COUNT", None)
    assert result == [{"COUNT(*)": 0}]


def test_missing_field_returns_none():
    result = apply_aggregation(RECORDS, "SUM", "bonus")
    assert result == [{"SUM(bonus)": None}]
