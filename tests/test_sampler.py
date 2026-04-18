import pytest
from querypath.sampler import (
    apply_sample,
    apply_sample_fraction,
    parse_sample_spec,
    apply_sample_spec,
)

ROWS = [{"id": i, "val": i * 2} for i in range(20)]


def test_sample_returns_correct_count():
    result = apply_sample(ROWS, 5, seed=0)
    assert len(result) == 5


def test_sample_reproducible_with_seed():
    a = apply_sample(ROWS, 5, seed=99)
    b = apply_sample(ROWS, 5, seed=99)
    assert a == b


def test_sample_different_seeds_differ():
    a = apply_sample(ROWS, 10, seed=1)
    b = apply_sample(ROWS, 10, seed=2)
    assert a != b


def test_sample_n_larger_than_rows_returns_all():
    result = apply_sample(ROWS, 100, seed=0)
    assert len(result) == len(ROWS)


def test_sample_n_zero_returns_empty():
    assert apply_sample(ROWS, 0) == []


def test_sample_fraction_basic():
    result = apply_sample_fraction(ROWS, 0.5, seed=0)
    assert len(result) == 10


def test_sample_fraction_zero_returns_empty():
    assert apply_sample_fraction(ROWS, 0.0) == []


def test_sample_fraction_one_returns_all():
    result = apply_sample_fraction(ROWS, 1.0)
    assert len(result) == len(ROWS)


def test_parse_sample_spec_n():
    spec = parse_sample_spec({"n": "7", "seed": "42"})
    assert spec == {"n": 7, "seed": 42}


def test_parse_sample_spec_fraction():
    spec = parse_sample_spec({"fraction": 0.25})
    assert spec["fraction"] == 0.25


def test_parse_sample_spec_invalid_fraction():
    with pytest.raises(ValueError):
        parse_sample_spec({"fraction": 1.5})


def test_parse_sample_spec_missing_key():
    with pytest.raises(ValueError):
        parse_sample_spec({"seed": 1})


def test_parse_sample_spec_not_dict():
    with pytest.raises(ValueError):
        parse_sample_spec("bad")


def test_apply_sample_spec_n():
    spec = parse_sample_spec({"n": 3, "seed": 7})
    result = apply_sample_spec(ROWS, spec)
    assert len(result) == 3


def test_apply_sample_spec_fraction():
    spec = parse_sample_spec({"fraction": 0.1, "seed": 7})
    result = apply_sample_spec(ROWS, spec)
    assert len(result) >= 1
