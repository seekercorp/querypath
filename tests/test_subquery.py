"""Tests for querypath.subquery module."""
import pytest
from querypath.subquery import execute_subquery, resolve_value, apply_subquery_where


DEPT_DATA = [
    {"dept_id": 1, "name": "Engineering"},
    {"dept_id": 2, "name": "Marketing"},
    {"dept_id": 3, "name": "HR"},
]

EMP_DATA = [
    {"id": 1, "name": "Alice", "dept_id": 1, "salary": 90000},
    {"id": 2, "name": "Bob",   "dept_id": 2, "salary": 70000},
    {"id": 3, "name": "Carol", "dept_id": 1, "salary": 85000},
    {"id": 4, "name": "Dave",  "dept_id": 3, "salary": 60000},
]


def test_execute_subquery_returns_field_list():
    sq = {"data": DEPT_DATA, "scalar_field": "dept_id"}
    result = execute_subquery(sq, {})
    assert sorted(result) == [1, 2, 3]


def test_execute_subquery_with_where():
    sq = {
        "data": DEPT_DATA,
        "where": {"field": "name", "op": "=", "value": "Engineering"},
        "scalar_field": "dept_id",
    }
    result = execute_subquery(sq, {})
    assert result == [1]


def test_execute_subquery_scalar_true():
    sq = {
        "data": DEPT_DATA,
        "where": {"field": "name", "op": "=", "value": "Marketing"},
        "scalar": True,
        "scalar_field": "dept_id",
    }
    result = execute_subquery(sq, {})
    assert result == 2


def test_execute_subquery_scalar_empty_returns_none():
    sq = {
        "data": DEPT_DATA,
        "where": {"field": "name", "op": "=", "value": "Nonexistent"},
        "scalar": True,
        "scalar_field": "dept_id",
    }
    assert execute_subquery(sq, {}) is None


def test_resolve_value_plain():
    assert resolve_value(42, {}) == 42
    assert resolve_value("hello", {}) == "hello"


def test_resolve_value_subquery():
    sq_wrap = {
        "__subquery__": {
            "data": DEPT_DATA,
            "scalar": True,
            "scalar_field": "dept_id",
            "where": {"field": "name", "op": "=", "value": "HR"},
        }
    }
    assert resolve_value(sq_wrap, {}) == 3


def test_apply_subquery_where_filters_records():
    where = {
        "field": "dept_id",
        "in_subquery": {
            "data": DEPT_DATA,
            "where": {"field": "name", "op": "=", "value": "Engineering"},
            "scalar_field": "dept_id",
        },
    }
    result = apply_subquery_where(EMP_DATA, where, {})
    names = [r["name"] for r in result]
    assert names == ["Alice", "Carol"]


def test_apply_subquery_where_missing_field_returns_all():
    result = apply_subquery_where(EMP_DATA, {}, {})
    assert result == EMP_DATA
