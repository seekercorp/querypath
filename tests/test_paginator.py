import pytest
from querypath.paginator import (
    apply_offset,
    apply_limit,
    apply_pagination,
    parse_pagination_spec,
)

ROWS = [{"id": i, "val": i * 10} for i in range(1, 8)]  # 7 rows


def test_apply_offset_basic():
    result = apply_offset(ROWS, 3)
    assert [r["id"] for r in result] == [4, 5, 6, 7]


def test_apply_offset_zero_returns_all():
    assert apply_offset(ROWS, 0) == ROWS


def test_apply_offset_negative_returns_all():
    assert apply_offset(ROWS, -1) == ROWS


def test_apply_offset_beyond_length_returns_empty():
    assert apply_offset(ROWS, 100) == []


def test_apply_limit_basic():
    result = apply_limit(ROWS, 3)
    assert [r["id"] for r in result] == [1, 2, 3]


def test_apply_limit_zero_returns_empty():
    assert apply_limit(ROWS, 0) == []


def test_apply_limit_negative_returns_all():
    assert apply_limit(ROWS, -1) == ROWS


def test_apply_limit_beyond_length_returns_all():
    assert apply_limit(ROWS, 100) == ROWS


def test_apply_pagination_limit_and_offset():
    result = apply_pagination(ROWS, limit=3, offset=2)
    assert [r["id"] for r in result] == [3, 4, 5]


def test_apply_pagination_only_limit():
    result = apply_pagination(ROWS, limit=4)
    assert [r["id"] for r in result] == [1, 2, 3, 4]


def test_apply_pagination_only_offset():
    result = apply_pagination(ROWS, offset=5)
    assert [r["id"] for r in result] == [6, 7]


def test_apply_pagination_none_returns_all():
    assert apply_pagination(ROWS) == ROWS


def test_parse_pagination_spec_both():
    spec = parse_pagination_spec({"limit": 10, "offset": 5})
    assert spec == {"limit": 10, "offset": 5}


def test_parse_pagination_spec_strings_coerced():
    spec = parse_pagination_spec({"limit": "3", "offset": "1"})
    assert spec == {"limit": 3, "offset": 1}


def test_parse_pagination_spec_missing_keys():
    spec = parse_pagination_spec({})
    assert spec == {"limit": None, "offset": None}


def test_parse_pagination_spec_invalid_limit():
    with pytest.raises(ValueError, match="Invalid limit"):
        parse_pagination_spec({"limit": "abc"})


def test_parse_pagination_spec_invalid_offset():
    with pytest.raises(ValueError, match="Invalid offset"):
        parse_pagination_spec({"offset": [1, 2]})
