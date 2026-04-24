"""Tests for querypath/conditional_agg.py"""
import pytest
from querypath.conditional_agg import (
    _eval_condition,
    apply_count_if,
    apply_sum_if,
    apply_avg_if,
    parse_conditional_agg_spec,
)

ROWS = [
    {"name": "Alice", "dept": "eng", "salary": 90000},
    {"name": "Bob",   "dept": "eng", "salary": 80000},
    {"name": "Carol", "dept": "hr",  "salary": 70000},
    {"name": "Dave",  "dept": "hr",  "salary": None},
]


# --- _eval_condition ---

def test_eval_eq_match():
    assert _eval_condition({"dept": "eng"}, {"field": "dept", "op": "eq", "value": "eng"}) is True

def test_eval_eq_no_match():
    assert _eval_condition({"dept": "hr"}, {"field": "dept", "op": "eq", "value": "eng"}) is False

def test_eval_gt():
    assert _eval_condition({"salary": 85000}, {"field": "salary", "op": "gt", "value": 80000}) is True

def test_eval_gt_none_returns_false():
    assert _eval_condition({"salary": None}, {"field": "salary", "op": "gt", "value": 0}) is False

def test_eval_is_null():
    assert _eval_condition({"salary": None}, {"field": "salary", "op": "is_null"}) is True

def test_eval_is_not_null():
    assert _eval_condition({"salary": 100}, {"field": "salary", "op": "is_not_null"}) is True

def test_eval_unknown_op_returns_false():
    assert _eval_condition({"x": 1}, {"field": "x", "op": "between", "value": 0}) is False


# --- apply_count_if ---

def test_count_if_matches_subset():
    result = apply_count_if(ROWS, {"field": "dept", "op": "eq", "value": "eng"}, alias="eng_count")
    assert all(r["eng_count"] == 2 for r in result)

def test_count_if_no_match_returns_zero():
    result = apply_count_if(ROWS, {"field": "dept", "op": "eq", "value": "finance"}, alias="fin_count")
    assert all(r["fin_count"] == 0 for r in result)

def test_count_if_preserves_original_keys():
    result = apply_count_if(ROWS, {"field": "dept", "op": "eq", "value": "hr"})
    assert result[0]["name"] == "Alice"


# --- apply_sum_if ---

def test_sum_if_numeric_field():
    result = apply_sum_if(ROWS, "salary", {"field": "dept", "op": "eq", "value": "eng"}, alias="eng_salary")
    assert all(r["eng_salary"] == 170000 for r in result)

def test_sum_if_skips_none_values():
    result = apply_sum_if(ROWS, "salary", {"field": "dept", "op": "eq", "value": "hr"}, alias="hr_salary")
    # Carol=70000, Dave=None -> sum=70000
    assert all(r["hr_salary"] == 70000 for r in result)

def test_sum_if_no_match_returns_zero():
    result = apply_sum_if(ROWS, "salary", {"field": "dept", "op": "eq", "value": "finance"}, alias="s")
    assert all(r["s"] == 0 for r in result)


# --- apply_avg_if ---

def test_avg_if_basic():
    result = apply_avg_if(ROWS, "salary", {"field": "dept", "op": "eq", "value": "eng"}, alias="avg_eng")
    assert all(r["avg_eng"] == 85000.0 for r in result)

def test_avg_if_no_match_returns_none():
    result = apply_avg_if(ROWS, "salary", {"field": "dept", "op": "eq", "value": "finance"}, alias="avg_fin")
    assert all(r["avg_fin"] is None for r in result)


# --- parse_conditional_agg_spec ---

def test_parse_no_key_returns_empty():
    assert parse_conditional_agg_spec({}) == []

def test_parse_single_dict_wrapped_in_list():
    spec = {"func": "count_if", "condition": {}}
    result = parse_conditional_agg_spec({"conditional_agg": spec})
    assert result == [spec]

def test_parse_list_returned_as_is():
    specs = [{"func": "sum_if"}, {"func": "avg_if"}]
    result = parse_conditional_agg_spec({"conditional_agg": specs})
    assert result == specs
