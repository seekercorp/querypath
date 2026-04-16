# querypath

A CLI tool for running SQL-like queries against JSON, CSV, and YAML files without a database.

---

## Installation

```bash
pip install querypath
```

Or install from source:

```bash
git clone https://github.com/yourname/querypath.git && cd querypath && pip install .
```

---

## Usage

```bash
querypath "SELECT name, age FROM data.json WHERE age > 30"
querypath "SELECT * FROM users.csv ORDER BY name LIMIT 10"
querypath "SELECT id, title FROM config.yaml WHERE active = true"
```

**Supported file formats:** JSON, CSV, YAML

**Supported clauses:** `SELECT`, `FROM`, `WHERE`, `ORDER BY`, `LIMIT`

### Example

```bash
$ querypath "SELECT name, score FROM results.json WHERE score > 90"

name           score
─────────────────────
Alice          95
Carlos         92
Priya          98
```

---

## Options

| Flag | Description |
|------|-------------|
| `--output` | Output format: `table` (default), `json`, `csv` |
| `--no-header` | Suppress column headers |
| `--version` | Show version and exit |

```bash
querypath "SELECT * FROM data.csv" --output json
```

---

## License

MIT © 2024 [yourname](https://github.com/yourname)