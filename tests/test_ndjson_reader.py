import json
import pytest
from pathlib import Path
from querypath.readers.ndjson_reader import NdJsonReader
from querypath.readers import get_reader


@pytest.fixture
def tmp_ndjson(tmp_path):
    def _write(lines, suffix=".ndjson"):
        p = tmp_path / f"data{suffix}"
        p.write_text("\n".join(lines), encoding="utf-8")
        return str(p)
    return _write


def test_read_basic(tmp_ndjson):
    path = tmp_ndjson(['{"a": 1}', '{"a": 2}'])
    reader = NdJsonReader(path)
    rows = reader.read()
    assert rows == [{"a": 1}, {"a": 2}]


def test_read_skips_blank_lines(tmp_ndjson):
    path = tmp_ndjson(['{"x": 10}', '', '{"x": 20}'])
    rows = NdJsonReader(path).read()
    assert len(rows) == 2


def test_read_scalar_wrapped(tmp_ndjson):
    path = tmp_ndjson(['42', '"hello"'])
    rows = NdJsonReader(path).read()
    assert rows == [{"value": 42}, {"value": "hello"}]


def test_invalid_json_raises(tmp_ndjson):
    path = tmp_ndjson(['{"a": 1}', 'NOT_JSON'])
    with pytest.raises(ValueError, match="line 2"):
        NdJsonReader(path).read()


def test_get_reader_ndjson(tmp_ndjson):
    path = tmp_ndjson(['{"k": "v"}'], suffix=".ndjson")
    reader = get_reader(path)
    assert isinstance(reader, NdJsonReader)


def test_get_reader_jsonl(tmp_ndjson):
    path = tmp_ndjson(['{"k": "v"}'], suffix=".jsonl")
    reader = get_reader(path)
    assert isinstance(reader, NdJsonReader)


def test_empty_file(tmp_ndjson):
    path = tmp_ndjson([])
    rows = NdJsonReader(path).read()
    assert rows == []
