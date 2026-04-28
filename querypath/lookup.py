"""lookup.py – enrich rows by joining a field value against a static mapping dict.

Provides SQL-style LEFT JOIN semantics against an in-memory dictionary so that
pipeline stages can annotate rows without a second file reader.
"""

from typing import Any, Dict, List, Optional


def apply_lookup(
    rows: List[Dict[str, Any]],
    source_field: str,
    mapping: Dict[Any, Dict[str, Any]],
    *,
    prefix: str = "lkp_",
    default: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Return *rows* enriched with columns from *mapping* keyed on *source_field*.

    For each row the value of *source_field* is looked up in *mapping*.  If
    found, the matched sub-dict is merged into the row with keys prefixed by
    *prefix*.  If not found, *default* (or an empty dict) is used instead,
    so every row gets the same set of extra keys.
    """
    if default is None:
        default = {}

    # Collect all possible extra keys so every row stays rectangular
    all_extra_keys: set = set()
    for v in mapping.values():
        all_extra_keys.update(v.keys())
    if default:
        all_extra_keys.update(default.keys())

    result: List[Dict[str, Any]] = []
    for row in rows:
        key = row.get(source_field)
        matched = mapping.get(key, default)
        new_row = dict(row)
        for k in all_extra_keys:
            new_row[f"{prefix}{k}"] = matched.get(k)
        result.append(new_row)
    return result


def parse_lookup_spec(opts: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Extract and validate a lookup spec from pipeline *opts*.

    Expected keys in *opts*:
        lookup_field   – source field name in the row (str)
        lookup_map     – dict mapping key -> {col: value, ...}
        lookup_prefix  – optional column prefix (default 'lkp_')
        lookup_default – optional fallback dict when key is missing
    """
    if not opts:
        return None
    if "lookup_field" not in opts or "lookup_map" not in opts:
        return None
    return {
        "source_field": opts["lookup_field"],
        "mapping": opts["lookup_map"],
        "prefix": opts.get("lookup_prefix", "lkp_"),
        "default": opts.get("lookup_default", {}),
    }


def run_pipeline_with_lookup(
    rows: List[Dict[str, Any]],
    opts: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Pipeline entry-point: enrich *rows* if a valid lookup spec is present."""
    spec = parse_lookup_spec(opts)
    if spec is None:
        return rows
    return apply_lookup(
        rows,
        source_field=spec["source_field"],
        mapping=spec["mapping"],
        prefix=spec["prefix"],
        default=spec["default"],
    )
