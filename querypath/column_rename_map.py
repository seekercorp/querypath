"""Bulk column rename mapping: rename multiple columns via a dict or list of pairs."""

from typing import Any, Dict, List, Optional, Union


def apply_rename_map(
    rows: List[Dict[str, Any]],
    rename_map: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Return rows with columns renamed according to rename_map.

    Keys not present in a row are silently skipped.  Columns not in
    rename_map are passed through unchanged.
    """
    if not rename_map:
        return rows
    result = []
    for row in rows:
        new_row: Dict[str, Any] = {}
        for k, v in row.items():
            new_key = rename_map.get(k, k)
            new_row[new_key] = v
        result.append(new_row)
    return result


def parse_rename_map_spec(
    opts: Optional[Dict[str, Any]]
) -> Optional[Dict[str, str]]:
    """Extract a rename map from pipeline opts.

    Accepts:
      opts["rename"] = {"old": "new", ...}          # plain dict
      opts["rename"] = [["old", "new"], ...]         # list of pairs
    Returns None when the key is absent or empty.
    """
    if not opts:
        return None
    spec = opts.get("rename")
    if not spec:
        return None
    if isinstance(spec, dict):
        return {str(k): str(v) for k, v in spec.items()}
    if isinstance(spec, list):
        mapping: Dict[str, str] = {}
        for item in spec:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                mapping[str(item[0])] = str(item[1])
        return mapping or None
    return None


def run_pipeline_with_rename_map(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Convenience wrapper used by the main pipeline."""
    rename_map = parse_rename_map_spec(opts)
    if not rename_map:
        return rows
    return apply_rename_map(rows, rename_map)
