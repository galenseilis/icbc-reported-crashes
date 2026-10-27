# Rebuild only the dashboard export

Use this guide when the extracted Hyper data already exists but you want to
regenerate `data/processed/icbc_reported_crashes.csv` and its schema metadata. This
is useful after changing the export code, after a partial run, or when you want
to inspect an existing extract without downloading it again.

This guide does **not** download the workbook, unpack the extract, or split the
result into partitions.

## Before you start

Confirm that the main Hyper file exists:

```bash
ls -lh "data/raw/tableau/extracted/2021-2025 public data set.hyper"
```

If it is missing, run the full pipeline or follow
[Inspect the Tableau and Hyper assets](inspect-tableau-assets.md) to download and
extract the workbook first.

## Steps

### 1. Run the export

From the repository root:

```bash
uv run src/icbc_reported_crashes/export_dashboard_data.py
```

The script will:

1. open the Hyper file;
2. discover the table whose columns match the expected 25-column crash schema;
3. print the source table, row count, and physical columns;
4. export the physical columns plus two row-level calculated fields;
5. write the CSV and schema JSON;
6. re-read the CSV to validate its row count and alphabetical header.

The important output sections are `=== SOURCE ===`, `=== EXPORT ===`, and
`=== VALIDATION ===`. A successful run ends with:

```text
Validation: OK

=== COMPLETE ===
CSV:    /path/to/icbc-reported-crashes/data/processed/icbc_reported_crashes.csv
Schema: /path/to/icbc-reported-crashes/data/processed/icbc_reported_crashes.schema.json
```

### 2. Check the output

```bash
ls -lh data/processed/icbc_reported_crashes.csv \
       data/processed/icbc_reported_crashes.schema.json
wc -l data/processed/icbc_reported_crashes.csv
```

The CSV has one header row plus one row per source record. For the documented
snapshot that is `1,453,137` lines. The schema's `source.row_count` should match
the number of data rows.

### 3. Rebuild the partitions if needed

The export and the partition tree are independent. If you changed the CSV, the
old partitions are now stale. Rebuild them with:

```bash
uv run src/icbc_reported_crashes/split_records.py
```

See [Rebuild only the partitioned records](rebuild-partitioned-records.md) for
details, including how to remove stale files first.

## What the export includes

The CSV contains 27 columns:

- the 25 physical columns from the Hyper table;
- `Municipality Name (ifnull)`, derived with
  `COALESCE("MUNICIPALITY_NAME", 'Unknown')`;
- `Street Full Name (ifnull)`, derived with
  `COALESCE("STREET_FULL_NAME", 'Unknown')`.

Two Tableau fields are **not** materialized as row-level columns:

- `Metric Selector` is an aggregate controlled by a parameter.
- `Crash Breakdown 2` is a parameter-controlled dimension.

Both are documented in the schema JSON's `calculated_fields` and `parameters`
sections. This avoids inventing a single value for a field that depends on a
dashboard selection.

## What can go wrong

- **`Hyper file does not exist`** — the extraction stage has not run, or the
  expected filename changed.
- **`Could not find the ICBC crash source table`** — the extract no longer
  contains all expected physical columns. Inspect the catalog with
  [Inspect the Tableau and Hyper assets](inspect-tableau-assets.md), then update
  the expected column set in `export_dashboard_data.py` only if the source change
  is understood.
- **`Export row count mismatch`** — the CSV was interrupted, the disk is full, or
  the source changed during export. Free space and rerun.
- **Columns missing or extra** — the export warns about extra physical columns
  but treats missing expected columns as an error.

## Related pages

- [Pipeline script reference](../reference/pipeline-scripts.md#export_dashboard_data)
- [Dataset schema](../reference/dataset-schema.md)
- [Deterministic exports](../explanation/deterministic-exports.md)
