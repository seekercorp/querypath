"""String functions applicable to row fields."""
import re


def fn_upper(value):
    return str(value).upper() if value is not None else None


def fn_lower(value):
    return str(value).lower() if value is not None else None


def fn_trim(value):
    return str(value).strip() if value is not None else None


def fn_length(value):
    return len(str(value)) if value is not None else None


def fn_replace(value, old, new):
    return str(value).replace(old, new) if value is not None else None


def fn_substr(value, start, length=None):
    s = str(value) if value is not None else ""
    start = int(start)
    if length is not None:
        return s[start:start + int(length)]
    return s[start:]


def fn_contains(value, substr):
    return substr in str(value) if value is not None else False


STRING_FUNCS = {
    "upper": fn_upper,
    "lower": fn_lower,
    "trim": fn_trim,
    "length": fn_length,
    "replace": fn_replace,
    "substr": fn_substr,
    "contains": fn_contains,
}


def parse_string_func_spec(spec):
    """Parse spec like 'upper:name' or 'replace:name:foo:bar'."""
    if not spec:
        return None
    parts = spec.split(":")
    func_name = parts[0].lower()
    if func_name not in STRING_FUNCS:
        return None
    return {"func": func_name, "args": parts[1:]}


def apply_string_func(rows, spec, output_field=None):
    """Apply a string function to a field in each row."""
    func_name = spec["func"]
    args = spec["args"]
    if not args:
        return rows
    field = args[0]
    extra_args = args[1:]
    fn = STRING_FUNCS[func_name]
    out_field = output_field or f"{func_name}_{field}"
    result = []
    for row in rows:
        new_row = dict(row)
        val = row.get(field)
        new_row[out_field] = fn(val, *extra_args)
        result.append(new_row)
    return result
