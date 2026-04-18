"""Integration of sampling into the query pipeline."""
from typing import List, Dict, Any, Optional
from querypath.sampler import parse_sample_spec, apply_sample_spec


def run_pipeline_with_sample(
    rows: List[Dict[str, Any]],
    sample_spec: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Apply sampling step if a sample spec is provided.

    Intended to be called after filtering/sorting but before formatting.
    """
    if not sample_spec:
        return rows
    parsed = parse_sample_spec(sample_spec)
    return apply_sample_spec(rows, parsed)


def extract_sample_spec(query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract the sample spec from a query dict, if present.

    Supported query keys:
        sample_n      -> {"n": value}
        sample_frac   -> {"fraction": value}
        sample_seed   -> optional seed for either

    Example query:
        {"sample_n": 10, "sample_seed": 42}
    """
    seed = query.get("sample_seed")
    if "sample_n" in query:
        spec: Dict[str, Any] = {"n": int(query["sample_n"])}
        if seed is not None:
            spec["seed"] = int(seed)
        return spec
    if "sample_frac" in query:
        spec = {"fraction": float(query["sample_frac"])}
        if seed is not None:
            spec["seed"] = int(seed)
        return spec
    return None
