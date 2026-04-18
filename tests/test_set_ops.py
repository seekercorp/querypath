import pytest
from querypath.set_ops import apply_union, apply_intersect, apply_except, parse_set_op_spec

A = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}, {"id": 3, "v": "c"}]
B = [{"id": 2, "v": "b"}, {"id": 3, "v": "c"}, {"id": 4, "v": "d"}]


def test_union_distinct_removes_dupes():
    result = apply_union(A, B)
    assert len(result) == 4
    ids = [r["id"] for r in result]
    assert sorted(ids) == [1, 2, 3, 4]


def test_union_all_keeps_dupes():
    result = apply_union(A, B, distinct=False)
    assert len(result) == 6


def test_union_empty_right():
    result = apply_union(A, [])
    assert result == A


def test_union_empty_left():
    result = apply_union([], B)
    assert len(result) == 3


def test_intersect_common_rows():
    result = apply_intersect(A, B)
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {2, 3}


def test_intersect_no_common():
    c = [{"id": 9, "v": "z"}]
    result = apply_intersect(A, c)
    assert result == []


def test_intersect_distinct():
    duped = A + [{"id": 2, "v": "b"}]
    result = apply_intersect(duped, B)
    assert len(result) == 2


def test_except_removes_right():
    result = apply_except(A, B)
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_except_no_overlap_returns_left():
    c = [{"id": 9, "v": "z"}]
    result = apply_except(A, c)
    assert len(result) == 3


def test_except_distinct():
    duped = A + [{"id": 1, "v": "a"}]
    result = apply_except(duped, B)
    assert len(result) == 1


def test_parse_set_op_spec_valid():
    spec = parse_set_op_spec({"op": "union", "right": B, "all": True})
    assert spec["op"] == "union"
    assert spec["all"] is True


def test_parse_set_op_spec_defaults():
    spec = parse_set_op_spec({"op": "intersect", "right": []})
    assert spec["all"] is False


def test_parse_set_op_spec_invalid():
    with pytest.raises(ValueError, match="Unknown set operation"):
        parse_set_op_spec({"op": "merge", "right": []})
