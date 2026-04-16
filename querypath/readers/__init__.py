"""Reader registry — returns the appropriate reader for a given file path."""
from pathlib import Path

from .json_reader import JsonReader
from .csv_reader import CsvReader
from .yaml_reader import YamlReader
from .ndjson_reader import NdJsonReader

_EXTENSION_MAP = {
    ".json": JsonReader,
    ".csv": CsvReader,
    ".yaml": YamlReader,
    ".yml": YamlReader,
    ".ndjson": NdJsonReader,
    ".jsonl": NdJsonReader,
}


def get_reader(path: str):
    ext = Path(path).suffix.lower()
    cls = _EXTENSION_MAP.get(ext)
    if cls is None:
        raise ValueError(f"Unsupported file extension: '{ext}'")
    return cls(path)
