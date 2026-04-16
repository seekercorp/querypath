import csv
from typing import List, Dict, Any


class CsvReader:
    """Reads a CSV file and returns a list of record dicts."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> List[Dict[str, Any]]:
        records = []
        with open(self.file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV file appears to be empty or missing a header row.")
            for row in reader:
                records.append(self._coerce_types(dict(row)))
        return records

    @staticmethod
    def _coerce_types(row: Dict[str, str]) -> Dict[str, Any]:
        """Attempt to cast numeric strings to int or float."""
        coerced = {}
        for key, value in row.items():
            try:
                coerced[key] = int(value)
            except (ValueError, TypeError):
                try:
                    coerced[key] = float(value)
                except (ValueError, TypeError):
                    coerced[key] = value
        return coerced
