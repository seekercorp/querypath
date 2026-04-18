from querypath.pipeline_set_ops import run_pipeline_with_set_op, extract_set_op_spec

LEFT = [{"id": 1, "city": "NY"}, {"id": 2, "city": "LA"}, {"id": 3, "city": "SF"}]
RIGHT = [{"id": 2, "city": "LA"}, {"id": 3, "city": "SF"}, {"id": 4, "city": "Chicago"}]


def _opts(op, right=None, all_=False):
    return {"set_op": {"op": op, "right": right or RIGHT, "all": all_}}


def test_no_spec_returns_rows_unchanged():
    result = run_pipeline_with_set_op(LEFT, {})
    assert result == LEFT


def test_union_distinct():
    result = run_pipeline_with_set_op(LEFT, _opts("union"))
    assert len(result) == 4
    ids = {r["id"] for r in result}
    assert ids == {1, 2, 3, 4}


def test_union_all():
    result = run_pipeline_with_set_op(LEFT, _opts("union", all_=True))
    assert len(result) == 6


def test_intersect():
    result = run_pipeline_with_set_op(LEFT, _opts("intersect"))
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {2, 3}


def test_except():
    result = run_pipeline_with_set_op(LEFT, _opts("except"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_extract_set_op_spec_missing_returns_none():
    assert extract_set_op_spec({}) is None


def test_extract_set_op_spec_present():
    opts = _opts("union")
    spec = extract_set_op_spec(opts)
    assert spec["op"] == "union"
    assert spec["all"] is False
