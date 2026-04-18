import pytest
from querypath.fuzzy_filter import (
    apply_like, apply_not_like, apply_regex_filter,
    parse_fuzzy_spec, apply_fuzzy_spec
)

ROWS = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@test.org"},
    {"name": "Charlie", "email": "charlie@example.com"},
    {"name": "alicia", "email": "alicia@work.io"},
]


def test_like_prefix():
    result = apply_like(ROWS, "name", "Al%")
    assert len(result) == 2
    assert all(r["name"].lower().startswith("al") for r in result)


def test_like_suffix():
    result = apply_like(ROWS, "email", "%example.com")
    assert len(result) == 2


def test_like_single_char():
    result = apply_like(ROWS, "name", "Bo_")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_like_no_match():
    result = apply_like(ROWS, "name", "Zara%")
    assert result == []


def test_not_like():
    result = apply_not_like(ROWS, "email", "%example.com")
    assert len(result) == 2
    assert all("example.com" not in r["email"] for r in result)


def test_regex_filter():
    result = apply_regex_filter(ROWS, "email", r"@.*\.org$")
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_regex_filter_no_match():
    result = apply_regex_filter(ROWS, "name", r"^Z")
    assert result == []


def test_parse_fuzzy_spec_like():
    spec = parse_fuzzy_spec("name LIKE Al%")
    assert spec == {"column": "name", "op": "LIKE", "pattern": "Al%"}


def test_parse_fuzzy_spec_not_like():
    spec = parse_fuzzy_spec("email NOT LIKE %example%")
    assert spec == {"column": "email", "op": "NOT LIKE", "pattern": "%example%"}


def test_parse_fuzzy_spec_regex():
    spec = parse_fuzzy_spec("email REGEX ^alice")
    assert spec == {"column": "email", "op": "REGEX", "pattern": "^alice"}


def test_parse_fuzzy_spec_invalid():
    assert parse_fuzzy_spec("just a string") is None
    assert parse_fuzzy_spec(None) is None


def test_apply_fuzzy_spec_like():
    spec = {"column": "name", "op": "LIKE", "pattern": "Ali%"}
    result = apply_fuzzy_spec(ROWS, spec)
    assert len(result) == 2


def test_apply_fuzzy_spec_regex():
    spec = {"column": "email", "op": "REGEX", "pattern": r"\.org$"}
    result = apply_fuzzy_spec(ROWS, spec)
    assert len(result) == 1
