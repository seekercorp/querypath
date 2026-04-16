import pytest
from querypath.formatter import format_output, format_table, format_json, format_csv


SAMPLE = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob", "age": 25, "city": "LA"},
]


def test_format_table_headers():
    out = format_table(SAMPLE)
    assert "name" in out
    assert "age" in out
    assert "city" in out


def test_format_table_values():
    out = format_table(SAMPLE)
    assert "Alice" in out
    assert "Bob" in out
    assert "NYC" in out


def test_format_table_empty():
    assert format_table([]) == "(no results)"


def test_format_json_valid():
    import json
    out = format_json(SAMPLE)
    parsed = json.loads(out)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "Alice"


def test_format_csv_headers():
    out = format_csv(SAMPLE)
    lines = out.splitlines()
    assert lines[0] == "name,age,city"


def test_format_csv_values():
    out = format_csv(SAMPLE)
    assert "Alice,30,NYC" in out
    assert "Bob,25,LA" in out


def test_format_csv_empty():
    assert format_csv([]) == ""


def test_format_output_dispatches_table():
    out = format_output(SAMPLE, fmt="table")
    assert "+" in out


def test_format_output_dispatches_json():
    out = format_output(SAMPLE, fmt="json")
    assert out.startswith("[")


def test_format_output_dispatches_csv():
    out = format_output(SAMPLE, fmt="csv")
    assert "name,age,city" in out


def test_format_output_invalid_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        format_output(SAMPLE, fmt="xml")
