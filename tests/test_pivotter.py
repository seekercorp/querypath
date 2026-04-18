import pytest
from querypath.pivotter import apply_pivot, apply_unpivot, parse_pivot_spec

RAWS = [
    {"region": "north", "product": "apple", "sales": 10},
    {"region": "north", "product": "banana", "sales": 5},
    {"region": "south", "product": "apple", "sales": 8},
    {"region": "south", "product": "banana", "sales": 3},
]


def test_pivot_creates_columns():
    result = apply_pivot(RAWS, index="region", columns="product", values="sales")
    assert len(result) == 2
    regions = {r["region"] for r in result}
    assert regions == {"north", "south"}


def test_pivot_values_correct():
    result = apply_pivot(RAWS, index="region", columns="product", values="sales")
    north = next(r for r in result if r["region"] == "north")
    assert north["apple"] == 10
    assert north["banana"] == 5


def test_pivot_empty_returns_empty():
    assert apply_pivot([], index="region", columns="product", values="sales") == []


def test_unpivot_expands_rows():
    wide = [
        {"region": "north", "apple": 10, "banana": 5},
        {"region": "south", "apple": 8, "banana": 3},
    ]
    result = apply_unpivot(wide, id_columns=["region"], value_columns=["apple", "banana"])
    assert len(result) == 4


def test_unpivot_var_val_names():
    wide = [{"id": 1, "x": 9, "y": 7}]
    result = apply_unpivot(wide, ["id"], ["x", "y"], var_name="col", val_name="num")
    assert result[0]["col"] == "x"
    assert result[0]["num"] == 9


def test_unpivot_preserves_id_columns():
    wide = [{"id": 42, "a": 1, "b": 2}]
    result = apply_unpivot(wide, ["id"], ["a", "b"])
    assert all(r["id"] == 42 for r in result)


def test_parse_pivot_spec_valid():
    spec = {"index": "r", "columns": "c", "values": "v"}
    assert parse_pivot_spec(spec) == spec


def test_parse_pivot_spec_missing_raises():
    with pytest.raises(ValueError, match="missing keys"):
        parse_pivot_spec({"index": "r"})
