import pytest
from querypath.window import apply_row_number, apply_rank, apply_lag, apply_lead

ROWS = [
    {"dept": "eng", "name": "Alice", "salary": 90},
    {"dept": "eng", "name": "Bob",   "salary": 70},
    {"dept": "eng", "name": "Carol", "salary": 70},
    {"dept": "hr",  "name": "Dave",  "salary": 60},
    {"dept": "hr",  "name": "Eve",   "salary": 80},
]


def test_row_number_no_partition():
    result = apply_row_number(ROWS, "rn", [], order_by="salary")
    nums = [r["rn"] for r in result]
    assert sorted(nums) == list(range(1, 6))


def test_row_number_with_partition():
    result = apply_row_number(ROWS, "rn", ["dept"], order_by="salary")
    eng = sorted([r["rn"] for r in result if r["dept"] == "eng"])
    hr  = sorted([r["rn"] for r in result if r["dept"] == "hr"])
    assert eng == [1, 2, 3]
    assert hr  == [1, 2]


def test_rank_ties_get_same_rank():
    result = apply_rank(ROWS, "rnk", ["dept"], order_by="salary")
    eng_rows = {r["name"]: r["rnk"] for r in result if r["dept"] == "eng"}
    assert eng_rows["Bob"] == eng_rows["Carol"]
    assert eng_rows["Alice"] == 3


def test_rank_no_ties():
    result = apply_rank(ROWS, "rnk", ["dept"], order_by="salary")
    hr_rows = {r["name"]: r["rnk"] for r in result if r["dept"] == "hr"}
    assert hr_rows["Dave"] == 1
    assert hr_rows["Eve"] == 2


def test_lag_basic():
    simple = [{"g": "a", "v": i} for i in [10, 20, 30]]
    result = apply_lag(simple, "prev_v", "v", [], order_by="v")
    vals = [r["prev_v"] for r in result]
    assert vals[0] is None
    assert 10 in vals
    assert 20 in vals


def test_lead_basic():
    simple = [{"g": "a", "v": i} for i in [10, 20, 30]]
    result = apply_lead(simple, "next_v", "v", [], order_by="v")
    vals = [r["next_v"] for r in result]
    assert vals[-1] is None
    assert 20 in vals
    assert 30 in vals


def test_lag_offset_2():
    simple = [{"v": i} for i in [1, 2, 3, 4]]
    result = apply_lag(simple, "lag2", "v", [], order_by="v")
    result2 = apply_lag(simple, "lag2", "v", [], order_by="v", offset=2)
    nones = [r for r in result2 if r["lag2"] is None]
    assert len(nones) == 2


def test_does_not_mutate_original():
    original = [{"dept": "eng", "salary": 100}]
    apply_row_number(original, "rn", ["dept"])
    assert "rn" not in original[0]
