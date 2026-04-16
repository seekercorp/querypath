import pytest
from querypath.transformer import apply_rename, apply_computed_column, parse_alias


ROWS = [
    {"price": 10.0, "qty": 3, "name": "apple"},
    {"price": 5.0,  "qty": 8, "name": "banana"},
]


def test_rename_existing_column():
    result = apply_rename(ROWS, "name", "product")
    assert "product" in result[0]
    assert "name" not in result[0]


def test_rename_missing_column_is_noop():
    result = apply_rename(ROWS, "nonexistent", "x")
    assert result[0] == ROWS[0]


def test_rename_does_not_mutate():
    apply_rename(ROWS, "name", "product")
    assert "name" in ROWS[0]


def test_computed_column_multiply():
    result = apply_computed_column(ROWS, "price * qty", "total")
    assert result[0]["total"] == pytest.approx(30.0)
    assert result[1]["total"] == pytest.approx(40.0)


def test_computed_column_add_literal():
    result = apply_computed_column(ROWS, "qty + 2", "qty_plus")
    assert result[0]["qty_plus"] == pytest.approx(5.0)


def test_computed_column_divide():
    result = apply_computed_column(ROWS, "price / qty", "unit")
    assert result[0]["unit"] == pytest.approx(10.0 / 3)


def test_computed_column_divide_by_zero_returns_none():
    rows = [{"a": 5.0, "b": 0}]
    result = apply_computed_column(rows, "a / b", "r")
    assert result[0]["r"] is None


def test_computed_column_missing_field_returns_none():
    rows = [{"x": 1}]
    result = apply_computed_column(rows, "x * missing", "out")
    assert result[0]["out"] is None


def test_computed_column_bad_expr_raises():
    with pytest.raises(ValueError, match="Cannot parse expression"):
        apply_computed_column(ROWS, "price ?? qty", "bad")


def test_parse_alias_with_as():
    expr, alias = parse_alias("price * qty AS total")
    assert expr == "price * qty"
    assert alias == "total"


def test_parse_alias_without_as():
    expr, alias = parse_alias("price")
    assert expr == "price"
    assert alias is None


def test_parse_alias_case_insensitive():
    expr, alias = parse_alias("score as pts")
    assert alias == "pts"
