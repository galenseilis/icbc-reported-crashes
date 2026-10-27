# Troubleshoot the pipeline

Use this guide when a stage fails or produces output you do not trust. Find the
failing stage first, then match the symptom.

## First: identify the failing stage

The four main stages are independent. Run them one at a time to isolate the
problem:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run src/icbc_reported_crashes/extract_tableau.py
uv run src/icbc_reported_crashes/export_dashboard_data.py
uv run src/icbc_reported_crashes/split_records.py
```

The `./run` wrapper does not stop when an earlier stage fails, so a later error can
distract from the real cause. Check the output immediately after each stage.

Also confirm that you are in the repository root:

```bash
pwd
ls run pyproject.toml
```

## Setup and environment

### `uv: command not found`

`uv` is not installed or not on `PATH`. Install it from the
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/),
then open a new shell.

### `ModuleNotFoundError: No module named 'tableauhyperapi'`

You are probably using a system Python instead of the project environment. Run
the script through `uv run`:

```bash
uv run src/icbc_reported_crashes/export_dashboard_data.py
```

If the error persists, rebuild the environment:

```bash
uv sync
```

### `./run: Permission denied`

Make the wrapper executable or invoke it through bash:

```bash
chmod +x run
./run
```

or:

```bash
bash run
```

### `icbc-reported-crashes: command not found` or an import error

The `pyproject.toml` entry point points at a package-level `main()` that is not
implemented. Use the module commands shown above instead. This is a known gap, not
a problem with your environment.

### Python version errors

The project requires Python 3.14 or newer. `uv` can install a suitable
interpreter. If you have pinned an older interpreter in your shell or CI, remove
that override and run `uv sync` again.

## Download and extraction

### `HTTPError`, `URLError`, or a timeout

The download stage could not reach Tableau Public. Check network access and retry:

```bash
curl -I https://public.tableau.com/workbooks/ICBCReportedCrashes.twb
```

If the URL has moved, update `WORKBOOK_URL` in `tableau.py`. Do not silently
substitute a different dataset; record the new source.

### `BadZipFile: File is not a zip file`

The downloaded `.twb` is not a valid ZIP container. This often means Tableau
returned an HTML error page, a login page, or a partial download. Check the file:

```bash
ls -lh data/raw/tableau/ICBCReportedCrashes.twb
file data/raw/tableau/ICBCReportedCrashes.twb
head -c 200 data/raw/tableau/ICBCReportedCrashes.twb
```

Delete the bad file and rerun the download:

```bash
rm data/raw/tableau/ICBCReportedCrashes.twb
uv run src/icbc_reported_crashes/tableau.py
```

### The extracted directory is missing a `.hyper` file

`extract_tableau.py` writes entries by their base filename. Check what was
actually extracted:

```bash
ls -lh data/raw/tableau/extracted
uv run src/icbc_reported_crashes/inspect_tableau.py
```

If the workbook no longer contains a file with the expected name, the downstream
scripts will fail. Compare the archive listing with their hardcoded paths before
changing anything.

## Export

### `ERROR: Hyper file does not exist`

The main extract is missing. Run the download and extraction stages:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run src/icbc_reported_crashes/extract_tableau.py
```

Then confirm the file exists:

```bash
ls -lh "data/raw/tableau/extracted/2021-2025 public data set.hyper"
```

### `Could not find the ICBC crash source table`

The Hyper file does not contain a table with all 25 expected physical columns.
This usually means the source schema changed. Inspect the catalog:

```bash
uv run src/icbc_reported_crashes/inspect_hyper.py
```

Do not simply delete column names from the expected set. First determine whether
the field was renamed, removed, or moved to a different table. Update
`EXPECTED_COLUMNS` in `export_dashboard_data.py` only when the change is
understood, and update the [dataset schema](../reference/dataset-schema.md).

### `Expected physical columns are missing`

The table was found, but some expected columns are absent. The error lists them.
Treat this as schema drift and investigate before exporting.

### `Export row count mismatch` or `Expected to export ... rows`

The number of rows written does not match the Hyper row count. Common causes:

- the process was interrupted;
- the disk filled up;
- the CSV was being read or written by another process;
- the source changed during the run.

Check free space, close other readers, and rerun:

```bash
df -h .
uv run src/icbc_reported_crashes/export_dashboard_data.py
```

### `No space left on device`

The full CSV and partition tree need roughly 600 MB in addition to the raw files.
Free space and rerun the failing stage. Partial files should be overwritten on the
next successful run, but verify with [Verify an export](verify-an-export.md).

## Split

### `Input CSV not found`

Either the export has not run, or you are not in the repository root. The
splitter resolves paths relative to the current directory:

```bash
pwd
ls -lh data/processed/icbc_reported_crashes.csv
```

Run it from the repository root:

```bash
uv run src/icbc_reported_crashes/split_records.py
```

### `Missing required columns`

The CSV does not contain `DATE_OF_LOSS_YEAR`, `MONTH_OF_YEAR`, `DAY_OF_WEEK`, and
`TIME_CATEGORY`. Confirm that you are splitting the exported crash CSV, not a
partition file with a hand-edited header.

### `Unknown month` or `Unknown weekday`

A temporal field contains an unexpected value or a null. The splitter groups with
`dropna=False` but then tries to format the missing value, which raises. Inspect the
distinct values:

```bash
uv run python - <<'PY'
import pandas as pd

df = pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=["MONTH_OF_YEAR", "DAY_OF_WEEK", "TIME_CATEGORY"],
    keep_default_na=False,
)

for column in df.columns:
    print(column)
    print(df[column].value_counts(dropna=False).head(20))
    print()
PY
```

Decide whether the source introduced a new valid value or whether the CSV is
corrupt. Do not guess a mapping without documenting it.

### The tree has fewer or more files than expected

`split_records.py` overwrites generated files but never deletes stale ones. If the
source lost a partition, the old file remains. Clear the tree and rerun:

```bash
rm -rf data/processed/records
uv run src/icbc_reported_crashes/split_records.py
```

Then verify the count with [Verify an export](verify-an-export.md).

## Data looks wrong

### Crash totals do not match the number of rows

This is expected. A record is an aggregate and can represent multiple crashes. Use
`SUM(TOTAL_CRASHES)`, not `COUNT(*)`. See
[Rows are not crashes](../explanation/data-limitations.md#rows-are-not-crashes).

### Latitude, longitude, or cross street is missing

The source only assigns geocode fields when it has enough location information.
The documented snapshot has 261,968 records without coordinates. This is a source
limitation, not a pipeline failure. See
[Caveats and licence](../reference/caveats-and-licence.md).

### Counts changed after a refresh

ICBC revises counts because of late reporting, corrections, and data development.
A changed number is not necessarily a bug. Compare the source capture date and
document the revision. See [Data provenance](../explanation/data-provenance.md).

## Related pages

- [Refresh from the public source](refresh-from-source.md)
- [Verify an export](verify-an-export.md)
- [Pipeline script reference](../reference/pipeline-scripts.md)
- [Data limitations](../explanation/data-limitations.md)
