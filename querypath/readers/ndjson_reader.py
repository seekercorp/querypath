"""Reader for newline-delimited JSON (NDJSON / JSON Lines) files."""
import json
from pathlib import Path
from typing import Union


class NdJsonReader:
    """Read a .ndjson / .jsonl file where each line is a JSON object."""

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)

    def read(self) -> list:
        """Return a list of dicts, one per non-empty line."""
        records = []
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
                if not isinstance(obj, dict):
                    raise ValueError(
                        f"Line {lineno} of {self.path} is not a JSON object"
                    )
                records.append(obj)
        return records
