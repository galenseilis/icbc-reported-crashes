# Rebuild only the partitioned records

Use this guide when `data/processed/icbc_reported_crashes.csv` already exists and
you want to regenerate the `data/processed/records/` tree. This is faster than a
full refresh and is useful after changing the splitting rules or after a partial
run.

## Before you start

The splitter reads a path relative to the **current working directory**. Run the
command from the repository root.

Confirm that the CSV exists:

```bash
ls -lh data/processed/icbc_reported_crashes.csv
```

If it is missing, follow
[Rebuild only the dashboard export](rebuild-dashboard-export.md) first.

## Steps

### 1. Decide whether to clear the old tree

`split_records.py` overwrites the files it generates, but it never deletes files
that are no longer generated. If the source lost a year, month, weekday, or time
bucket, old files will remain and the tree will not be an exact mirror of the
CSV.

To rebuild from scratch, remove the old tree:

```bash
rm -rf data/processed/records
```

> **Warning:** the record files are tracked in git. Removing them makes them show
> up as deletions until the split recreates them. Do not commit the deletions
> on their own.

If you know the source only gained data and no partitions disappeared, you can
skip this step.

### 2. Run the splitter

```bash
uv run src/icbc_reported_crashes/split_records.py
```

The script groups rows by `DATE_OF_LOSS_YEAR`, `MONTH_OF_YEAR`, `DAY_OF_WEEK`,
and `TIME_CATEGORY`, then writes one CSV per group. It prints each file as it is
created, followed by a summary:

```text
Processing complete.
Input rows:  1,453,136
Output rows: 1,453,136
Files created: 3,360
Output root: /path/to/icbc-reported-crashes/data/processed/records
```

`Input rows` and `Output rows` must match. A mismatch means rows were lost or
duplicated during grouping.

### 3. Verify the tree

Count files and data rows directly from the filesystem:

```bash
uv run python - <<'PY'
import csv
from pathlib import Path

root = Path("data/processed/records")
files = sorted(root.rglob("*.csv"))

rows = 0
for path in files:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader)  # header
        rows += sum(1 for _ in reader)

print(f"{len(files):,} files, {rows:,} data rows")
PY
```

For the documented 2021–2025 snapshot this prints:

```text
3,360 files, 1,453,136 data rows
```

Every file has the same 27-column header as the full CSV. Spot-check one:

```bash
head -n 2 data/processed/records/2021/01_JANUARY/1_MONDAY/0900_1159.csv
```

### 4. Review the diff

```bash
git status --short data/processed/records
git diff --stat -- data/processed/records
```

With unchanged source data and unchanged splitting rules, the split is
deterministic and should produce no diff.

## Naming rules

The path is:

```text
records/<year>/<MM_MONTH>/<D_WEEKDAY>/<HHMM_HHMM>.csv
```

Examples:

| Source value | Path segment |
|---|---|
| `2021` | `2021` |
| `JANUARY` | `01_JANUARY` |
| `MONDAY` | `1_MONDAY` |
| `09:00-11:59` | `0900_1159.csv` |

Month numbers are two-digit; weekday numbers are one-digit with Monday = 1 and
Sunday = 7. See [Records layout](../reference/records-layout.md) for the complete
reference.

## What can go wrong

- **`Input CSV not found`** — you are not in the repository root, or the export
  has not run.
- **`Missing required columns`** — the CSV is not the dashboard export, or its
  schema has drifted.
- **`Unknown month` or `Unknown weekday`** — a temporal field contains an
  unexpected value or a null. The splitter groups with `dropna=False` but then
  tries to format the missing value, which fails. Inspect the CSV before rerunning.
- **Fewer files than expected** — one or more partitions are missing, likely
  because the source is missing a temporal combination. This is not necessarily
  an error, but the tree will not have the full 3,360-file shape.

## Related pages

- [Records layout](../reference/records-layout.md)
- [Pipeline script reference](../reference/pipeline-scripts.md#split_records)
- [Verify an export](verify-an-export.md)
