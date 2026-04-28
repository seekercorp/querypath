"""Tests for querypath/lookup.py."""

import pytest
from querypath.lookup import apply_lookup, parse_lookup_spec, run_pipeline_with_lookup


DEPT_MAP = {
    "eng": {"name": "Engineering", "floor": 3},
    "hr": {"name": "Human Resources", "floor": 1},
    "fin": {"name": "Finance", "floor": 2},
}

ROWS = [
    {"id": 1, "dept": "eng", "salary": 90000},
    {"id": 2, "dept": "hr", "salary": 70000},
    {"id": 3, "dept": "fin", "salary": 80000},
    {"id": 4, "dept": "unknown", "salary": 60000},
]


def test_apply_lookup_adds_prefixed_columns():
    result = apply_lookup(ROWS, "dept", DEPT_MAP)
    assert "lkp_name" in result[0]
    assert "lkp_floor" in result[0]


def test_apply_lookup_correct_values():
    result = apply_lookup(ROWS, "dept", DEPT_MAP)
    assert result[0]["lkp_name"] == "Engineering"
    assert result[1]["lkp_floor"] == 1
    assert result[2]["lkp_name"] == "Finance"


def test_apply_lookup_unmatched_key_gets_none_by_default():
    result = apply_lookup(ROWS, "dept", DEPT_MAP)
    # Row 4 has dept='unknown' which is not in DEPT_MAP
    unmatched = next(r for r in result if r["dept"] == "unknown")
    assert unmatched["lkp_name"] is None
    assert unmatched["lkp_floor"] is None


def test_apply_lookup_custom_prefix():
    result = apply_lookup(ROWS[:1], "dept", DEPT_MAP, prefix="dept_")
    assert "dept_name" in result[0]
    assert "dept_floor" in result[0]


def test_apply_lookup_custom_default():
    default = {"name": "Unknown Dept", "floor": 0}
    result = apply_lookup(ROWS, "dept", DEPT_MAP, default=default)
    unmatched = next(r for r in result if r["dept"] == "unknown")
    assert unmatched["lkp_name"] == "Unknown Dept"
    assert unmatched["lkp_floor"] == 0


def test_apply_lookup_preserves_original_columns():
    result = apply_lookup(ROWS, "dept", DEPT_MAP)
    assert result[0]["id"] == 1
    assert result[0]["salary"] == 90000


def test_apply_lookup_all_rows_have_same_keys():
    result = apply_lookup(ROWS, "dept", DEPT_MAP)
    keys = [set(r.keys()) for r in result]
    assert all(k == keys[0] for k in keys)


def test_apply_lookup_empty_rows():
    assert apply_lookup([], "dept", DEPT_MAP) == []


def test_apply_lookup_empty_mapping():
    result = apply_lookup(ROWS[:1], "dept", {})
    # No extra keys added when mapping is empty and default is empty
    assert result[0] == ROWS[0]


# --- parse_lookup_spec ---

def test_parse_lookup_spec_valid():
    opts = {"lookup_field": "dept", "lookup_map": DEPT_MAP}
    spec = parse_lookup_spec(opts)
    assert spec is not None
    assert spec["source_field"] == "dept"
    assert spec["prefix"] == "lkp_"


def test_parse_lookup_spec_custom_prefix():
    opts = {"lookup_field": "dept", "lookup_map": DEPT_MAP, "lookup_prefix": "x_"}
    spec = parse_lookup_spec(opts)
    assert spec["prefix"] == "x_"


def test_parse_lookup_spec_missing_field_returns_none():
    assert parse_lookup_spec({"lookup_map": DEPT_MAP}) is None


def test_parse_lookup_spec_missing_map_returns_none():
    assert parse_lookup_spec({"lookup_field": "dept"}) is None


def test_parse_lookup_spec_none_returns_none():
    assert parse_lookup_spec(None) is None


# --- run_pipeline_with_lookup ---

def test_pipeline_lookup_enriches_rows():
    opts = {"lookup_field": "dept", "lookup_map": DEPT_MAP}
    result = run_pipeline_with_lookup(ROWS, opts)
    assert result[0]["lkp_name"] == "Engineering"


def test_pipeline_lookup_no_opts_returns_rows_unchanged():
    result = run_pipeline_with_lookup(ROWS, None)
    assert result == ROWS


def test_pipeline_lookup_empty_opts_returns_rows_unchanged():
    result = run_pipeline_with_lookup(ROWS, {})
    assert result == ROWS
