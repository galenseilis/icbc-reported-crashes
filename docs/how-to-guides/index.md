# How-to guides

How-to guides are task-oriented. Each page assumes you already have a working
checkout and focuses on completing one job. For a guided introduction, start with
the [tutorial](../tutorials/first-export.md) instead.

## Refresh and rebuild

- [Refresh from the public source](refresh-from-source.md) — run the full
  download, extract, export, and split sequence.
- [Rebuild only the dashboard export](rebuild-dashboard-export.md) — regenerate
  the CSV and schema from an existing Hyper extract.
- [Rebuild only the partitioned records](rebuild-partitioned-records.md) —
  re-split an existing CSV into the `records/` tree.

## Inspect and verify

- [Inspect the Tableau and Hyper assets](inspect-tableau-assets.md) — list the
  workbook archive, read its XML, and profile the Hyper table.
- [Verify an export](verify-an-export.md) — check row counts, totals, schema
  order, null counts, and partition coverage.
- [Troubleshoot the pipeline](troubleshoot-pipeline.md) — diagnose common
  failures and decide whether to rerun or stop.

## Use the data

- [Query the export](query-the-export.md) — load the columns or partitions you
  need without reading the entire 300 MB CSV.
- [Fetch dataset metadata](fetch-dataset-metadata.md) — save the BC Data
  Catalogue record for provenance and citation.

## How these guides are written

Commands assume you are in the repository root. They use `uv run` so that the
project environment is used automatically. If a guide tells you to remove a
directory, read the warning first: some generated files are tracked in git.
