import pytest
from querypath.aggregator import apply_aggregation, _compute

ROWS = [
    {"dept": "eng", "salary": 90000, "bonus": 5000},
    {"dept": "eng", "salary": 80000, "bonus": None},
    {"dept": "hr", "salary": 60000, "bonus": 3000},
]


def test_count_all():
    assert _compute(ROWS, "COUNT(*)") == 3


def test_count_field_skips_none():
    assert _compute(ROWS, "COUNT(bonus)") == 2


def test_sum():
    assert _compute(ROWS, "SUM(salary)") == 230000


def test_avg():
    result = _compute(ROWS, "AVG(salary)")
    assert abs(result - (230000 / 3)) < 0.01


def test_min():
    assert _compute(ROWS, "MIN(salary)") == 60000


def test_max():
    assert _compute(ROWS, "MAX(salary)") == 90000


def test_avg_none_field_returns_none():
    assert _compute([], "AVG(salary)") is None


def test_unknown_expr_returns_none():
    assert _compute(ROWS, "STDDEV(salary)") is None


def test_apply_aggregation_single_group():
    from querypath.grouper import apply_group_by
    groups = apply_group_by(ROWS, [])
    agg_fields = [
        {"func": "COUNT", "field": "*", "alias": "total"},
        {"func": "SUM", "field": "salary", "alias": "total_salary"},
    ]
    result = apply_aggregation(groups, agg_fields)
    assert len(result) == 1
    assert result[0]["total"] == 3
    assert result[0]["total_salary"] == 230000


def test_apply_aggregation_multiple_groups():
    from querypath.grouper import apply_group_by
    groups = apply_group_by(ROWS, ["dept"])
    agg_fields = [{"func": "COUNT", "field": "*", "alias": "n"}]
    result = apply_aggregation(groups, agg_fields)
    totals = {r["n"] for r in result}
    assert totals == {1, 2}


def test_apply_aggregation_auto_alias():
    from querypath.grouper import apply_group_by
    groups = apply_group_by(ROWS, [])
    agg_fields = [{"func": "MAX", "field": "salary"}]
    result = apply_aggregation(groups, agg_fields)
    assert "MAX(salary)" in result[0]
