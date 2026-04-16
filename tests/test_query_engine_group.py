import pytest
from querypath.query_engine import QueryEngine

DATA = [
    {"dept": "eng", "name": "Alice", "salary": 90000},
    {"dept": "eng", "name": "Bob", "salary": 80000},
    {"dept": "hr", "name": "Carol", "salary": 60000},
    {"dept": "hr", "name": "Dave", "salary": 65000},
    {"dept": "eng", "name": "Eve", "salary": 95000},
]


@pytest.fixture
def engine():
    return QueryEngine(DATA)


def test_group_by_count(engine):
    result = engine.execute(
        select=[{"func": "COUNT", "field": "*", "alias": "n"}],
        group_by=["dept"],
    )
    counts = {r["n"] for r in result}
    assert counts == {2, 3}


def test_group_by_sum(engine):
    result = engine.execute(
        select=[{"func": "SUM", "field": "salary", "alias": "total"}],
        group_by=["dept"],
    )
    totals = sorted(r["total"] for r in result)
    assert totals == [125000, 265000]


def test_group_by_with_having(engine):
    result = engine.execute(
        select=[{"func": "COUNT", "field": "*", "alias": "n"}],
        group_by=["dept"],
        having={"field": "COUNT(*)", "op": ">", "value": 2},
    )
    assert len(result) == 1
    assert result[0]["n"] == 3


def test_no_group_by_returns_flat(engine):
    result = engine.execute(select=["*"])
    assert len(result) == len(DATA)


def test_group_by_avg(engine):
    result = engine.execute(
        select=[{"func": "AVG", "field": "salary", "alias": "avg_sal"}],
        group_by=["dept"],
    )
    avgs = sorted(r["avg_sal"] for r in result)
    assert abs(avgs[0] - 62500) < 1
    assert abs(avgs[1] - (265000 / 3)) < 1
