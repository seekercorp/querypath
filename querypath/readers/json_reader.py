import json
from typing import List, Dict, Any


class JsonReader:
    """Reads a JSON file and returns a list of flat record dicts."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> List[Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            # Wrap single object in a list
            records = [data]
        else:
            raise ValueError("JSON root must be an object or array of objects.")

        if not all(isinstance(r, dict) for r in records):
            raise ValueError("All JSON array elements must be objects.")

        return records
