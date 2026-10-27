# Refresh from the public source

Use this guide when you want the processed artifacts to match the current public
ICBC Reported Crashes workbook. It runs the complete pipeline: download, extract,
export, and split.

This is a **full refresh**, not an incremental update. Existing processed files
are overwritten.

## Before you start

1. Check that you are in the repository root:

   ```bash
   pwd
   ```

2. Record the current state so you can review what changed:

   ```bash
   git status --short
   ```

   The run rewrites files under `data/processed/records/`, which are tracked in
   git. A refresh that picks up new source data will therefore produce a large
   diff.

3. Check free disk space. The download is about 24 MB, the extracted assets about
   70 MB, and the full CSV plus partitions about 600 MB:

   ```bash
   df -h .
   ```

4. Make sure you have network access to `public.tableau.com`.

## Steps

### 1. Run the pipeline

```bash
./run
```

The wrapper executes four stages in order:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run src/icbc_reported_crashes/extract_tableau.py
uv run src/icbc_reported_crashes/export_dashboard_data.py
uv run src/icbc_reported_crashes/split_records.py
```

Watch for the completion messages from each stage. The export stage prints a
progress line every 100,000 rows. The split stage ends with a summary containing
the input row count, output row count, number of files, and output directory.

### 2. Confirm that the main artifacts exist

```bash
ls -lh data/processed
```

You should see:

- `icbc_reported_crashes.csv`
- `icbc_reported_crashes.schema.json`
- `records/`

The CSV should be hundreds of megabytes. The schema should be a few kilobytes.

### 3. Confirm that the split is complete

```bash
find data/processed/records -type f -name '*.csv' | wc -l
```

For the 2021–2025 snapshot this prints `3360`. The number is the product of:

```text
5 years × 12 months × 7 weekdays × 8 time buckets = 3,360 files
```

A future refresh with more years will produce more files. A source that is
missing one of the temporal dimensions in some rows can produce fewer files or
fail during splitting.

For a stronger check, including row totals and null counts, use
[Verify an export](verify-an-export.md).

### 4. Review the source changes

```bash
git status --short
git diff --stat
```

The record files dominate the diff. If the source has not changed, the export is
designed to be deterministic, so you should see no changes at all. If you see
changes, inspect them before committing:

```bash
git diff -- data/processed/records/2025/01_JANUARY/1_MONDAY/0900_1159.csv
```

### 5. Optionally refresh the inspection metadata

`./run` does not fetch the BC Data Catalogue record or the Hyper schema metadata.
To refresh those as well:

```bash
uv run src/icbc_reported_crashes/catalogue.py
uv run src/icbc_reported_crashes/inspect_hyper.py
```

This writes `data/metadata/catalogue.json` and
`data/metadata/hyper_schema.json`. Neither file is needed by the main pipeline.
See [Fetch dataset metadata](fetch-dataset-metadata.md) for details.

## What can go wrong

- **The wrapper reports success even if an earlier stage failed.** The stages are
  separate commands, not chained with `&&` or `set -e`. Read the output of each
  stage; do not rely only on the final summary.
- **Stale files survive a refresh.** `split_records.py` overwrites files it
  produces but does not delete files that are no longer generated. If the source
  loses a year, a month, or a time bucket, remove `data/processed/records/` and
  rerun the split. See
  [Rebuild only the partitioned records](rebuild-partitioned-records.md).
- **The source may have changed shape.** The export validates a fixed set of 25
  physical columns. New or removed columns can stop the run or change the output
  schema. See [Troubleshoot the pipeline](troubleshoot-pipeline.md).

## Related pages

- [Rebuild only the dashboard export](rebuild-dashboard-export.md)
- [Rebuild only the partitioned records](rebuild-partitioned-records.md)
- [Data provenance](../explanation/data-provenance.md)
- [Caveats and licence](../reference/caveats-and-licence.md)
