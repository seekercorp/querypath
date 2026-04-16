from .json_reader import JsonReader
from .csv_reader import CsvReader
from .yaml_reader import YamlReader

READER_MAP = {
    ".json": JsonReader,
    ".csv": CsvReader,
    ".yaml": YamlReader,
    ".yml": YamlReader,
}


def get_reader(file_path: str):
    """Return the appropriate reader instance based on file extension."""
    import os
    ext = os.path.splitext(file_path)[-1].lower()
    if ext not in READER_MAP:
        raise ValueError(f"Unsupported file type: '{ext}'. Supported types: {list(READER_MAP.keys())}")
    return READER_MAP[ext](file_path)
