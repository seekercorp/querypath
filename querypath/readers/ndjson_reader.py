"""Reader for newline-delimited JSON (NDJSON / JSON Lines) files."""
import json
from pathlib import Path
from typing import Any, Dict, List


class NdJsonReader:
    def __init__(self, path: str) -> None:
        self.path = Path(path)

    def read(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {lineno} of {self.path}: {exc}"
                    ) from exc
                if isinstance(obj, dict):
                    records.append(obj)
                else:
                    records.append({"value": obj})
        return records
