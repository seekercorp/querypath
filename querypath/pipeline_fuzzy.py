"""Pipeline integration for fuzzy/LIKE/REGEX filtering."""
from typing import List, Dict, Any, Optional
from querypath.fuzzy_filter import parse_fuzzy_spec, apply_fuzzy_spec


def extract_fuzzy_spec(options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract fuzzy filter spec from pipeline options dict."""
    raw = options.get("fuzzy")
    if not raw:
        return None
    return parse_fuzzy_spec(raw)


def run_pipeline_with_fuzzy(
    rows: List[Dict[str, Any]],
    options: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Run rows through fuzzy filter if a spec is present in options.

    options keys:
      fuzzy: str  e.g. 'name LIKE Al%'
    """
    spec = extract_fuzzy_spec(options)
    if spec:
        rows = apply_fuzzy_spec(rows, spec)
    return rows


# Integration test included here per project convention
def test_pipeline_fuzzy_like_integration():
    rows = [
        {"city": "Amsterdam", "pop": 900000},
        {"city": "Berlin", "pop": 3700000},
        {"city": "Athens", "pop": 660000},
    ]
    result = run_pipeline_with_fuzzy(rows, {"fuzzy": "city LIKE A%"})
    assert len(result) == 2
    assert all(r["city"].startswith("A") for r in result)


def test_pipeline_fuzzy_no_spec():
    rows = [{"x": 1}, {"x": 2}]
    result = run_pipeline_with_fuzzy(rows, {})
    assert result == rows
