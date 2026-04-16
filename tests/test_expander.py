import pytest
from querypath.expander import expand_rows, expand_column, _flatten


def test_flatten_simple_dict():
    row = {"a": 1, "b": 2}
    assert _flatten(row) == {"a": 1, "b": 2}


def test_flatten_nested_dict():
    row = {"a": {"b": {"c": 42}}}
    assert _flatten(row) == {"a.b.c": 42}


def test_flatten_list_values():
    row = {"tags": ["x", "y"]}
    assert _flatten(row) == {"tags.0": "x", "tags.1": "y"}


def test_flatten_mixed():
    row = {"user": {"name": "Alice", "scores": [10, 20]}}
    result = _flatten(row)
    assert result["user.name"] == "Alice"
    assert result["user.scores.0"] == 10
    assert result["user.scores.1"] == 20


def test_expand_rows_multiple():
    rows = [
        {"a": {"b": 1}},
        {"a": {"b": 2}},
    ]
    result = expand_rows(rows)
    assert result == [{"a.b": 1}, {"a.b": 2}]


def test_expand_rows_empty():
    assert expand_rows([]) == []


def test_expand_column_only_target():
    rows = [{"id": 1, "meta": {"city": "NY", "zip": "10001"}}]
    result = expand_column(rows, "meta")
    assert result == [{"id": 1, "meta.city": "NY", "meta.zip": "10001"}]


def test_expand_column_non_dict_value():
    rows = [{"id": 1, "meta": "plain"}]
    result = expand_column(rows, "meta")
    assert result == [{"id": 1, "meta": "plain"}]


def test_expand_column_missing_key():
    rows = [{"id": 1}]
    result = expand_column(rows, "meta")
    assert result == [{"id": 1, "meta": None}]


def test_expand_rows_custom_sep():
    rows = [{"a": {"b": 99}}]
    result = expand_rows(rows, sep="/")
    assert result == [{"a/b": 99}]
