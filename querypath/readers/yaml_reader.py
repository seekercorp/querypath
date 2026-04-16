from typing import List, Dict, Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError("PyYAML is required for YAML support. Install it with: pip install pyyaml") from exc


class YamlReader:
    """Reads a YAML file and returns a list of record dicts."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read(self) -> List[Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if isinstance(data, list):
            records = data
        elif isinstance(data, dict):
            records = [data]
        else:
            raise ValueError("YAML root must be a mapping or sequence of mappings.")

        if not all(isinstance(r, dict) for r in records):
            raise ValueError("All YAML sequence elements must be mappings.")

        return records
