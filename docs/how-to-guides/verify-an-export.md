# Verify an export

Use this guide after a refresh or a partial rebuild to check that the CSV, schema,
and partition tree agree with each other.

These checks catch interrupted exports, stale partitions, and accidental schema
changes. They do not prove that the source data is correct or complete; for that,
read [Caveats and licence](../reference/caveats-and-licence.md).

## Prerequisites

- `data/processed/icbc_reported_crashes.csv`
- `data/processed/icbc_reported_crashes.schema.json`
- `data/processed/records/`

If any are missing, follow
[Rebuild only the dashboard export](rebuild-dashboard-export.md) and
[Rebuild only the partitioned records](rebuild-partitioned-records.md).

## Run the consistency check

From the repository root:

```bash
uv run python - <<'PY'
import csv
import json
from pathlib import Path

csv_path = Path("data/processed/icbc_reported_crashes.csv")
schema_path = Path("data/processed/icbc_reported_crashes.schema.json")
records_root = Path("data/processed/records")

schema = json.loads(schema_path.read_text(encoding="utf-8"))
expected_rows = schema["source"]["row_count"]

with csv_path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    header = reader.fieldnames
    assert header is not None

    if header != sorted(header, key=str.casefold):
        raise SystemExit("FAIL: CSV columns are not alphabetically sorted")

    rows = 0
    crashes = 0
    victims = 0

    for row in reader:
        rows += 1
        crashes += int(row["TOTAL_CRASHES"])
        victims += int(row["TOTAL_VICTIMS"])

if rows != expected_rows:
    raise SystemExit(
        f"FAIL: CSV has {rows:,} rows; schema says {expected_rows:,}"
    )

files = sorted(records_root.rglob("*.csv"))
partition_rows = 0

for path in files:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        partition_header = next(reader)

        if partition_header != header:
            raise SystemExit(f"FAIL: header mismatch in {path}")

        partition_rows += sum(1 for _ in reader)

if partition_rows != rows:
    raise SystemExit(
        f"FAIL: partitions have {partition_rows:,} rows; CSV has {rows:,}"
    )

print(f"CSV rows:        {rows:,}")
print(f"Partition rows:  {partition_rows:,}")
print(f"Partition files: {len(files):,}")
print(f"Total crashes:   {crashes:,}")
print(f"Total victims:   {victims:,}")
print("OK")
PY
```

For the documented 2021–2025 snapshot the output is:

```text
CSV rows:        1,453,136
Partition rows:  1,453,136
Partition files: 3,360
Total crashes:   1,465,435
Total victims:   347,413
OK
```

The crash total is larger than the row count because a record can represent more
than one crash. That is expected. See
[Rows are not crashes](../explanation/data-limitations.md#rows-are-not-crashes).

## Interpret the results

| Result | Meaning |
|---|---|
| CSV rows equal schema `source.row_count` | The export finished and the schema describes the CSV. |
| Partition rows equal CSV rows | No rows were lost or duplicated during splitting. |
| Every partition header matches the CSV header | The splitter wrote a consistent schema. |
| `3,360` partition files | The full year × month × weekday × time-bucket shape is present. |
| Crash total greater than row total | Normal; records are aggregates. |
| Crash or victim totals changed since a previous run | The source was revised; investigate before treating it as a regression. |

A lower partition count is not automatically a failure. It can mean the source
does not contain every temporal combination, or that a year was added or removed.
Compare the count with the data you expect.

## Optional checks

### Inspect null counts

```bash
uv run python - <<'PY'
import csv
from pathlib import Path

path = Path("data/processed/icbc_reported_crashes.csv")
nulls = {}

with path.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    for row in reader:
        for column, value in row.items():
            if value == r"\N":
                nulls[column] = nulls.get(column, 0) + 1

for column in sorted(nulls, key=nulls.get, reverse=True):
    print(f"{column:40} {nulls[column]:>12,}")
PY
```

For the documented snapshot the largest null counts are
`CROSS_STREET_FULL_NAME` (815,517), `LATITUDE` (261,968), `LONGITUDE` (261,968),
and `MUNICIPALITY_WITH_BOUNDARY` (261,968). Nulls in location fields are expected
when the source lacked enough information to geocode a crash.

### Check for duplicate records

```bash
uv run python - <<'PY'
import csv
import hashlib
from collections import Counter

path = "data/processed/icbc_reported_crashes.csv"
seen = Counter()

with open(path, newline="", encoding="utf-8") as handle:
    reader = csv.reader(handle)
    next(reader)
    for row in reader:
        digest = hashlib.blake2b(
            "\x1f".join(row).encode("utf-8"),
            digest_size=16,
        ).digest()
        seen[digest] += 1

duplicate_groups = sum(1 for count in seen.values() if count > 1)
rows_beyond_first = sum(count - 1 for count in seen.values() if count > 1)

print(f"Duplicate groups: {duplicate_groups:,}")
print(f"Rows beyond first: {rows_beyond_first:,}")
PY
```

The documented snapshot has zero duplicate rows. A non-zero result may indicate a
source change or a pipeline bug; inspect before deleting anything.

## If a check fails

| Failure | Likely cause | Next step |
|---|---|---|
| CSV missing or empty | Export did not finish | Rerun the export; check disk space and the terminal output. |
| Header not alphabetical | The export was produced by a different code path or an older version | Rerun `export_dashboard_data.py`. |
| Schema row count mismatch | Interrupted export or schema written from a different run | Rerun the export; do not hand-edit the schema. |
| Partition rows mismatch | Partial split, stale files, or a changed CSV | Clear `records/` and rerun the split. |
| Header mismatch in a partition | Mixed output from different runs | Clear `records/` and rerun the split. |
| Duplicate rows | Source or grouping change | Inspect the affected records and the source extract. |

## Related pages

- [Troubleshoot the pipeline](troubleshoot-pipeline.md)
- [Dataset schema](../reference/dataset-schema.md)
- [Metadata files](../reference/metadata-files.md)
