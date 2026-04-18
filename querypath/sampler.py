"""Row sampling utilities for querypath."""
import random
from typing import List, Dict, Any, Optional


def apply_sample(rows: List[Dict[str, Any]], n: int, seed: Optional[int] = None) -> List[Dict[str, Any]]:
    """Return up to n randomly sampled rows."""
    if n <= 0:
        return []
    if n >= len(rows):
        return list(rows)
    rng = random.Random(seed)
    return rng.sample(rows, n)


def apply_sample_fraction(
    rows: List[Dict[str, Any]], fraction: float, seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Return a random fraction of rows (0.0 to 1.0)."""
    if fraction <= 0.0:
        return []
    if fraction >= 1.0:
        return list(rows)
    n = max(1, round(len(rows) * fraction))
    return apply_sample(rows, n, seed=seed)


def parse_sample_spec(spec: Any) -> Dict[str, Any]:
    """Parse a sample spec dict with keys: n or fraction, optional seed.

    Examples:
        {"n": 5}
        {"fraction": 0.2, "seed": 42}
    """
    if not isinstance(spec, dict):
        raise ValueError(f"Sample spec must be a dict, got {type(spec)}")
    result = {}
    if "n" in spec:
        result["n"] = int(spec["n"])
    elif "fraction" in spec:
        result["fraction"] = float(spec["fraction"])
        if not (0.0 <= result["fraction"] <= 1.0):
            raise ValueError("fraction must be between 0.0 and 1.0")
    else:
        raise ValueError("Sample spec must contain 'n' or 'fraction'")
    if "seed" in spec:
        result["seed"] = int(spec["seed"])
    return result


def apply_sample_spec(rows: List[Dict[str, Any]], spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply a parsed sample spec to rows."""
    seed = spec.get("seed")
    if "n" in spec:
        return apply_sample(rows, spec["n"], seed=seed)
    return apply_sample_fraction(rows, spec["fraction"], seed=seed)
