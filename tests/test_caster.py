import pytest
from datetime import date
from querypath.caster import cast_value, apply_cast, parse_cast_expression


def test_cast_to_int():
    assert cast_value("42", "int") == 42
    assert isinstance(cast_value("7", "int"), int)


def test_cast_to_float():
    assert cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_to_str():
    assert cast_value(100, "str") == "100"


def test_cast_to_bool_truthy():
    assert cast_value("yes", "bool") is True
    assert cast_value("true", "bool") is True
    assert cast_value(1, "bool") is True


def test_cast_to_bool_falsy():
    assert cast_value("false", "bool") is False
    assert cast_value("0", "bool") is False
    assert cast_value("", "bool") is False


def test_cast_to_date():
    result = cast_value("2024-06-15", "date")
    assert result == date(2024, 6, 15)


def test_cast_none_returns_none():
    assert cast_value(None, "int") is None
    assert cast_value(None, "date") is None


def test_cast_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported cast type"):
        cast_value("hello", "list")


def test_apply_cast_modifies_column():
    rows = [{"age": "25", "name": "Alice"}, {"age": "30", "name": "Bob"}]
    result = apply_cast(rows, "age", "int")
    assert result[0]["age"] == 25
    assert result[1]["age"] == 30
    assert result[0]["name"] == "Alice"


def test_apply_cast_missing_column_skips():
    rows = [{"x": 1}, {"age": "20"}]
    result = apply_cast(rows, "age", "int")
    assert result[0] == {"x": 1}
    assert result[1]["age"] == 20


def test_apply_cast_does_not_mutate_original():
    rows = [{"val": "5"}]
    apply_cast(rows, "val", "int")
    assert rows[0]["val"] == "5"


def test_parse_cast_expression_valid():
    assert parse_cast_expression("age::int") == ("age", "int")
    assert parse_cast_expression("score :: float") == ("score", "float")


def test_parse_cast_expression_no_cast():
    assert parse_cast_expression("age") is None
    assert parse_cast_expression("name") is None
