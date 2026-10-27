# Inspect the Tableau and Hyper assets

Use this guide to look inside the downloaded workbook and its embedded data
without running an export. This is useful for provenance work, schema drift
investigation, and understanding the Tableau calculated fields.

There are four inspection tools. Run only the ones you need.

## Before you start

The tools depend on the following files:

| File | Produced by |
|---|---|
| `data/raw/tableau/ICBCReportedCrashes.twb` | `tableau.py` |
| `data/raw/tableau/extracted/ICBC Reported Crashes.twb` | `extract_tableau.py` |
| `data/raw/tableau/extracted/2021-2025 public data set.hyper` | `extract_tableau.py` |

If the files are missing, run:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run src/icbc_reported_crashes/extract_tableau.py
```

## List the downloaded workbook archive

The file downloaded as `ICBCReportedCrashes.twb` is a ZIP container, not a plain
XML workbook. List its entries:

```bash
uv run src/icbc_reported_crashes/inspect_tableau.py
```

You will see each entry's uncompressed size, compressed size, and path, including
the embedded `.hyper` data files, the workbook XML, and the help image.

## Read the workbook XML

After extraction, the workbook XML is
`data/raw/tableau/extracted/ICBC Reported Crashes.twb`. Parse it and print a
summary:

```bash
uv run src/icbc_reported_crashes/inspect_workbook.py
```

The output includes:

- workbook build, platform, version, repository ID, and revision;
- datasources and their columns;
- parameters and allowed values;
- calculated fields and their formulas;
- target fields used by the export schema;
- worksheet and dashboard names.

For the documented snapshot the workbook contains 33 worksheets and 18
dashboards. These counts are source-dependent.

> The target-field section reports fields by their internal Tableau names. Some
> caption-based entries can appear under `Not found` even though the field is
> present under an internal name such as `[Calculation_...]`. The datasource and
> calculated-field sections are the authoritative listing.

## Inspect the Hyper catalog and columns

Open the main extract, list its schemas and tables, print the row count and column
definitions, and show ten sample rows:

```bash
uv run src/icbc_reported_crashes/inspect_hyper.py
```

The script also writes `data/metadata/hyper_schema.json` with this shape:

```json
{
  "file": "/absolute/path/to/2021-2025 public data set.hyper",
  "table": "\"Extract\".\"Extract\"",
  "row_count": 1453136,
  "columns": [
    {
      "ordinal": 0,
      "name": "\"MID_BLOCK_CRASH\"",
      "type": "TEXT",
      "nullable": "NULLABLE"
    }
  ]
}
```

This inspection metadata is not the same file as the export schema
`data/processed/icbc_reported_crashes.schema.json`. The export schema is the
canonical description of the CSV. See
[Metadata files](../reference/metadata-files.md) for the difference.

## Profile the Hyper table

For a deeper statistical profile, run:

```bash
uv run src/icbc_reported_crashes/profile_hyper.py
```

This prints:

- overall row, crash, and victim totals;
- rows, crashes, and victims by year;
- distributions of `TOTAL_CRASHES` and `TOTAL_VICTIMS`;
- latitude/longitude bounds and non-null counts;
- null and distinct counts for every physical column;
- a duplicate-row check over all 25 physical columns;
- value distributions for selected categorical columns;
- ten sample rows.

`profile_hyper.py` only prints to the terminal; it writes no files. The duplicate
check groups by all 25 columns and can take a few minutes on a large extract.

## Which tool should I use?

| Question | Tool |
|---|---|
| What files are inside the downloaded workbook? | `inspect_tableau.py` |
| What parameters and calculated fields does the workbook define? | `inspect_workbook.py` |
| What tables and columns does the Hyper extract contain? | `inspect_hyper.py` |
| What are the null rates and value distributions? | `profile_hyper.py` |
| What is the canonical schema of the exported CSV? | `export_dashboard_data.py` output, or [Dataset schema](../reference/dataset-schema.md) |

## Related pages

- [Tableau workbook anatomy](../explanation/tableau-workbook-anatomy.md)
- [Pipeline script reference](../reference/pipeline-scripts.md)
- [Metadata files](../reference/metadata-files.md)
