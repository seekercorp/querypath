import pytest
from querypath.string_funcs import (
    fn_upper, fn_lower, fn_trim, fn_length,
    fn_replace, fn_substr, fn_contains,
    parse_string_func_spec, apply_string_func,
)

ROWS = [
    {"name": "Alice", "city": "  New York  "},
    {"name": "bob", "city": "London"},
    {"name": None, "city": "Paris"},
]


def test_upper():
    assert fn_upper("hello") == "HELLO"

def test_lower():
    assert fn_lower("WORLD") == "world"

def test_trim():
    assert fn_trim("  hi  ") == "hi"

def test_length():
    assert fn_length("abc") == 3

def test_replace():
    assert fn_replace("hello world", "world", "there") == "hello there"

def test_substr_with_length():
    assert fn_substr("abcdef", 1, 3) == "bcd"

def test_substr_without_length():
    assert fn_substr("abcdef", 2) == "cdef"

def test_contains_true():
    assert fn_contains("hello world", "world") is True

def test_contains_false():
    assert fn_contains("hello", "xyz") is False

def test_none_returns_none_or_false():
    assert fn_upper(None) is None
    assert fn_length(None) is None
    assert fn_contains(None, "x") is False

def test_parse_string_func_spec_valid():
    spec = parse_string_func_spec("upper:name")
    assert spec == {"func": "upper", "args": ["name"]}

def test_parse_string_func_spec_replace():
    spec = parse_string_func_spec("replace:city:London:Berlin")
    assert spec == {"func": "replace", "args": ["city", "London", "Berlin"]}

def test_parse_string_func_spec_unknown():
    assert parse_string_func_spec("explode:name") is None

def test_parse_string_func_spec_none():
    assert parse_string_func_spec(None) is None

def test_apply_string_func_upper():
    spec = {"func": "upper", "args": ["name"]}
    result = apply_string_func(ROWS, spec, output_field="name_upper")
    assert result[0]["name_upper"] == "ALICE"
    assert result[1]["name_upper"] == "BOB"
    assert result[2]["name_upper"] is None

def test_apply_string_func_default_output_field():
    spec = {"func": "lower", "args": ["name"]}
    result = apply_string_func(ROWS, spec)
    assert "lower_name" in result[0]

def test_apply_string_func_does_not_mutate():
    spec = {"func": "trim", "args": ["city"]}
    result = apply_string_func(ROWS, spec, output_field="city_trimmed")
    assert ROWS[0]["city"] == "  New York  "
    assert result[0]["city_trimmed"] == "New York"
