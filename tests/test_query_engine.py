import pytest
from querypath.query_engine import QueryEngine

SAMPLE_DATA = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "London"},
    {"name": "Charlie", "age": 35, "city": "New York"},
    {"name": "Diana", "age": 28, "city": "Paris"},
]


def engine():
    return QueryEngine(SAMPLE_DATA)


def test_select_all():
    results = engine().execute("SELECT * FROM data")
    assert len(results) == 4
    assert results[0]["name"] == "Alice"


def test_select_columns():
    results = engine().execute("SELECT name, age FROM data")
    assert len(results) == 4
    assert "city" not in results[0]
    assert results[1]["name"] == "Bob"


def test_where_equals_string():
    results = engine().execute("SELECT * FROM data WHERE city = 'New York'")
    assert len(results) == 2
    assert all(r["city"] == "New York" for r in results)


def test_where_equals_int():
    results = engine().execute("SELECT * FROM data WHERE age = 25")
    assert len(results) == 1
    assert results[0]["name"] == "Bob"


def test_where_greater_than():
    results = engine().execute("SELECT name FROM data WHERE age > 28")
    assert len(results) == 2
    names = {r["name"] for r in results}
    assert names == {"Alice", "Charlie"}


def test_where_not_equals():
    results = engine().execute("SELECT * FROM data WHERE city != 'London'")
    assert len(results) == 3


def test_limit():
    results = engine().execute("SELECT * FROM data LIMIT 2")
    assert len(results) == 2


def test_where_and_limit():
    results = engine().execute("SELECT name FROM data WHERE age >= 28 LIMIT 2")
    assert len(results) == 2


def test_invalid_query():
    with pytest.raises(ValueError, match="Unsupported or malformed query"):
        engine().execute("INSERT INTO data VALUES (1)")


def test_invalid_where():
    with pytest.raises(ValueError, match="Invalid WHERE clause"):
        engine().execute("SELECT * FROM data WHERE age BETWEEN 1 AND 10")


def test_trailing_semicolon():
    results = engine().execute("SELECT * FROM data;")
    assert len(results) == 4
