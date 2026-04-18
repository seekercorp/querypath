"""Pipeline integration for string functions."""
from querypath.string_funcs import parse_string_func_spec, apply_string_func


def extract_string_func_specs(opts):
    """Extract list of string func specs from opts dict.

    opts["string_funcs"] may be a list of strings like ["upper:name", "trim:city:city"]
    where the optional third segment is the output field name.
    """
    raw = opts.get("string_funcs") or []
    specs = []
    for entry in raw:
        # Support optional output field: "func:field:...args:>out_field"
        output_field = None
        if ">" in entry:
            entry, output_field = entry.rsplit(">", 1)
            output_field = output_field.strip()
            entry = entry.strip()
        spec = parse_string_func_spec(entry)
        if spec:
            specs.append((spec, output_field))
    return specs


def run_pipeline_with_string_funcs(rows, opts):
    """Apply all string function specs to rows in order."""
    specs = extract_string_func_specs(opts)
    for spec, output_field in specs:
        rows = apply_string_func(rows, spec, output_field=output_field)
    return rows


if __name__ == "__main__":  # pragma: no cover
    sample = [{"name": "alice", "city": "  london  "}]
    result = run_pipeline_with_string_funcs(sample, {
        "string_funcs": ["upper:name>name_upper", "trim:city>city_clean"]
    })
    print(result)
