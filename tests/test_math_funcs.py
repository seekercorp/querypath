"""Tests for querypath/math_funcs.py."""

import pytest
from querypath.math_funcs import (
    fn_round,
    fn_abs,
    fn_ceil,
    fn_floor,
    fn_mod,
    apply_math_func,
    run_pipeline_with_math_funcs,
)


# ---------------------------------------------------------------------------
# Unit tests for individual functions
# ---------------------------------------------------------------------------

def test_round_basic():
    assert fn_round(3.14159, 2) == 3.14


def test_round_zero_decimals():
    assert fn_round(2.7) == 3.0


def test_round_none_returns_none():
    assert fn_round(None) is None


def test_round_non_numeric_returns_none():
    assert fn_round("hello") is None


def test_abs_positive():
    assert fn_abs(5) == 5.0


def test_abs_negative():
    assert fn_abs(-9.5) == 9.5


def test_abs_none_returns_none():
    assert fn_abs(None) is None


def test_ceil_basic():
    assert fn_ceil(2.1) == 3


def test_ceil_exact_int():
    assert fn_ceil(4.0) == 4


def test_ceil_none_returns_none():
    assert fn_ceil(None) is None


def test_floor_basic():
    assert fn_floor(2.9) == 2


def test_floor_negative():
    assert fn_floor(-2.1) == -3


def test_floor_none_returns_none():
    assert fn_floor(None) is None


def test_mod_basic():
    assert fn_mod(10, 3) == pytest.approx(1.0)


def test_mod_zero_divisor_returns_none():
    assert fn_mod(10, 0) is None


def test_mod_none_value_returns_none():
    assert fn_mod(None, 3) is None


def test_mod_none_divisor_returns_none():
    assert fn_mod(10, None) is None


# ---------------------------------------------------------------------------
# apply_math_func
# ---------------------------------------------------------------------------

def test_apply_math_func_round_adds_alias():
    rows = [{"price": 1.999}, {"price": 2.001}]
    result = apply_math_func(rows, "ROUND", "price", "price_r", extra_arg=2)
    assert result[0]["price_r"] == 2.0
    assert result[1]["price_r"] == 2.0


def test_apply_math_func_preserves_original_column():
    rows = [{"val": -7.3}]
    result = apply_math_func(rows, "ABS", "val", "abs_val")
    assert result[0]["val"] == -7.3
    assert result[0]["abs_val"] == 7.3


def test_apply_math_func_unknown_raises():
    with pytest.raises(ValueError, match="Unknown math function"):
        apply_math_func([{"x": 1}], "SQRT", "x", "y")


def test_apply_math_func_missing_col_uses_none():
    rows = [{"other": 5}]
    result = apply_math_func(rows, "ABS", "missing", "out")
    assert result[0]["out"] is None


# ---------------------------------------------------------------------------
# run_pipeline_with_math_funcs
# ---------------------------------------------------------------------------

def test_pipeline_no_specs_returns_rows_unchanged():
    rows = [{"a": 1}]
    assert run_pipeline_with_math_funcs(rows, {}) == rows


def test_pipeline_multiple_specs():
    rows = [{"price": 9.876, "delta": -4}]
    opts = {
        "math_funcs": [
            {"func": "ROUND", "col": "price", "alias": "price_r", "arg": 1},
            {"func": "ABS", "col": "delta", "alias": "abs_delta"},
        ]
    }
    result = run_pipeline_with_math_funcs(rows, opts)
    assert result[0]["price_r"] == 9.9
    assert result[0]["abs_delta"] == 4.0


def test_pipeline_floor_spec():
    rows = [{"score": 7.8}, {"score": 3.2}]
    opts = {"math_funcs": [{"func": "FLOOR", "col": "score", "alias": "score_floor"}]}
    result = run_pipeline_with_math_funcs(rows, opts)
    assert [r["score_floor"] for r in result] == [7, 3]
