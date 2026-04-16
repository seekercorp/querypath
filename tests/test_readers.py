import json
import csv
import os
import tempfile
import pytest

from querypath.readers import get_reader
from querypath.readers.csv_reader import CsvReader


def write_temp(suffix, content, mode="w"):
    f = tempfile.NamedTemporaryFile(suffix=suffix, mode=mode, delete=False, encoding="utf-8")
    f.write(content)
    f.close()
    return f.name


def test_json_reader_list():
    path = write_temp(".json", json.dumps([{"a": 1}, {"a": 2}]))
    try:
        records = get_reader(path).read()
        assert records == [{"a": 1}, {"a": 2}]
    finally:
        os.unlink(path)


def test_json_reader_single_object():
    path = write_temp(".json", json.dumps({"x": "hello"}))
    try:
        records = get_reader(path).read()
        assert records == [{"x": "hello"}]
    finally:
        os.unlink(path)


def test_csv_reader_coercion():
    content = "name,age,score\nAlice,30,9.5\nBob,25,8.0\n"
    path = write_temp(".csv", content)
    try:
        records = get_reader(path).read()
        assert records[0]["age"] == 30
        assert records[0]["score"] == 9.5
        assert records[0]["name"] == "Alice"
    finally:
        os.unlink(path)


def test_yaml_reader_list():
    pytest.importorskip("yaml")
    content = "- id: 1\n  city: Paris\n- id: 2\n  city: Rome\n"
    path = write_temp(".yaml", content)
    try:
        records = get_reader(path).read()
        assert len(records) == 2
        assert records[1]["city"] == "Rome"
    finally:
        os.unlink(path)


def test_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        get_reader("data.xml")
