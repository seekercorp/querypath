import pytest
from querypath.grouper import apply_group_by, apply_having, flatten_groups

ROWS = [
    {"dept": "eng", "name": "Alice", "salary": 90000},
    {"dept": "eng", "name": "Bob", "salary": 80000},
    {"dept": "hr", "name": "Carol", "salary": 60000},
    {"dept": "hr", "name": "Dave", "salary": 65000},
    {"dept": "eng", "name": "Eve", "salary": 95000},
]


def test_group_by_single_column():
    groups = apply_group_by(ROWS, ["dept"])
    assert set(groups.keys()) == {("eng",), ("hr",)}
    assert len(groups[("eng",)]) == 3
    assert len(groups[("hr",)]) == 2


def test_group_by_empty_returns_all_in_one_group():
    groups = apply_group_by(ROWS, [])
    assert list(groups.keys()) == [()]
    assert len(groups[()]) == len(ROWS)


def test_group_by_preserves_rows():
    groups = apply_group_by(ROWS, ["dept"])
    all_rows = [r for rows in groups.values() for r in rows]
    assert len(all_rows) == len(ROWS)


def test_group_by_multiple_columns():
    rows = [
        {"dept": "eng", "level": "senior", "val": 1},
        {"dept": "eng", "level": "junior", "val": 2},
        {"dept": "eng", "level": "senior", "val": 3},
    ]
    groups = apply_group_by(rows, ["dept", "level"])
    assert len(groups[("eng", "senior")]) == 2
    assert len(groups[("eng", "junior")]) == 1


def test_having_greater_than():
    groups = apply_group_by(ROWS, ["dept"])
    # having COUNT(*) > 2 — but _compute needs a real agg field
    # We test with a numeric field avg check via direct having dict
    # having salary > 70000 (avg of eng = 88333, avg of hr = 62500)
    having = {"field": "COUNT(*)", "op": ">", "value": 2}
    filtered = apply_having(groups, having)
    assert ("eng",) in filtered
    assert ("hr",) not in filtered


def test_having_none_returns_all():
    groups = apply_group_by(ROWS, ["dept"])
    filtered = apply_having(groups, None)
    assert filtered == groups


def test_flatten_groups_injects_keys():
    rows = [
        {"dept": "eng", "salary": 90000},
        {"dept": "hr", "salary": 60000},
    ]
    groups = apply_group_by(rows, ["dept"])
    flat = flatten_groups(groups, ["dept"])
    assert len(flat) == 2
    assert all("dept" in r for r in flat)
