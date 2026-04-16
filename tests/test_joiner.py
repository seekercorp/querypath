import pytest
from querypath.joiner import apply_join

USERS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Carol"},
]

ORDERS = [
    {"user_id": 1, "item": "Book"},
    {"user_id": 1, "item": "Pen"},
    {"user_id": 2, "item": "Desk"},
]


def test_inner_join_basic():
    result = apply_join(USERS, ORDERS, "id", "user_id")
    assert len(result) == 3
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" not in names


def test_inner_join_multiple_matches():
    result = apply_join(USERS, ORDERS, "id", "user_id")
    alice_rows = [r for r in result if r["name"] == "Alice"]
    assert len(alice_rows) == 2
    items = {r["item"] for r in alice_rows}
    assert items == {"Book", "Pen"}


def test_left_join_includes_unmatched():
    result = apply_join(USERS, ORDERS, "id", "user_id", join_type="left")
    assert len(result) == 4
    carol_rows = [r for r in result if r["name"] == "Carol"]
    assert len(carol_rows) == 1
    assert carol_rows[0].get("item") is None


def test_right_prefix():
    result = apply_join(USERS, ORDERS, "id", "user_id", right_prefix="order")
    assert "order.item" in result[0]
    assert "order.user_id" in result[0]


def test_no_matches_inner_returns_empty():
    result = apply_join(USERS, [], "id", "user_id", join_type="inner")
    assert result == []


def test_no_matches_left_returns_all_left():
    result = apply_join(USERS, [], "id", "user_id", join_type="left")
    assert len(result) == len(USERS)


def test_invalid_join_type_raises():
    with pytest.raises(ValueError, match="Unsupported join type"):
        apply_join(USERS, ORDERS, "id", "user_id", join_type="right")


def test_merged_row_contains_left_fields():
    result = apply_join(USERS, ORDERS, "id", "user_id")
    for row in result:
        assert "id" in row
        assert "name" in row
