import pytest
from querypath.query_engine import QueryEngine

USERS = [
    {"id": 1, "name": "Alice", "dept": "Eng"},
    {"id": 2, "name": "Bob", "dept": "HR"},
    {"id": 3, "name": "Carol", "dept": "Eng"},
]

SCORES = [
    {"uid": 1, "score": 95},
    {"uid": 2, "score": 80},
]


@pytest.fixture
def engine():
    return QueryEngine(USERS)


def test_inner_join_reduces_rows(engine):
    result = engine.execute(join_data=SCORES, join_left_key="id", join_right_key="uid")
    assert len(result) == 2


def test_left_join_keeps_unmatched(engine):
    result = engine.execute(
        join_data=SCORES, join_left_key="id", join_right_key="uid", join_type="left"
    )
    assert len(result) == 3


def test_join_with_prefix(engine):
    result = engine.execute(
        join_data=SCORES,
        join_left_key="id",
        join_right_key="uid",
        join_prefix="s",
    )
    assert "s.score" in result[0]


def test_join_then_where(engine):
    result = engine.execute(
        join_data=SCORES,
        join_left_key="id",
        join_right_key="uid",
        where={"score": {"op": "gt", "value": 85}},
    )
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_join_then_select(engine):
    result = engine.execute(
        join_data=SCORES,
        join_left_key="id",
        join_right_key="uid",
        select=["name", "score"],
    )
    for row in result:
        assert set(row.keys()) == {"name", "score"}


def test_no_join_data_unchanged(engine):
    result = engine.execute()
    assert len(result) == len(USERS)
