"""Pipeline integration for pivot/unpivot steps."""
from querypath.pivotter import apply_pivot, apply_unpivot, parse_pivot_spec


def extract_pivot_spec(query: dict) -> dict | None:
    """Return pivot spec from query dict, or None."""
    return query.get("pivot")


def extract_unpivot_spec(query: dict) -> dict | None:
    """Return unpivot spec from query dict, or None."""
    return query.get("unpivot")


def run_pipeline_with_pivot(rows: list[dict], query: dict) -> list[dict]:
    """Apply pivot or unpivot if specified in query, then return rows."""
    pivot_spec = extract_pivot_spec(query)
    if pivot_spec:
        spec = parse_pivot_spec(pivot_spec)
        return apply_pivot(
            rows,
            index=spec["index"],
            columns=spec["columns"],
            values=spec["values"],
        )

    unpivot_spec = extract_unpivot_spec(query)
    if unpivot_spec:
        id_cols = unpivot_spec.get("id_columns", [])
        val_cols = unpivot_spec.get("value_columns", [])
        var_name = unpivot_spec.get("var_name", "variable")
        val_name = unpivot_spec.get("val_name", "value")
        return apply_unpivot(rows, id_cols, val_cols, var_name, val_name)

    return rows


def test_pipeline_pivot_integration():
    rows = [
        {"region": "east", "product": "x", "sales": 1},
        {"region": "east", "product": "y", "sales": 2},
    ]
    query = {"pivot": {"index": "region", "columns": "product", "values": "sales"}}
    result = run_pipeline_with_pivot(rows, query)
    assert len(result) == 1
    assert result[0]["x"] == 1
