# Metadata files

The project can write three JSON metadata files. They serve different purposes
and are not interchangeable.

| File | Producer | Describes |
|---|---|---|
| `data/processed/icbc_reported_crashes.schema.json` | `export_dashboard_data.py` | The exported CSV |
| `data/metadata/hyper_schema.json` | `inspect_hyper.py` | The Hyper source table |
| `data/metadata/catalogue.json` | `catalogue.py` | The BC Data Catalogue record |

## Export schema

Path: `data/processed/icbc_reported_crashes.schema.json`

This is the canonical machine-readable description of the CSV. It is written
during export and is not tracked in git.

### Shape

```json
{
  "source": {
    "file": "data/raw/tableau/extracted/2021-2025 public data set.hyper",
    "table": "\"Extract\".\"Extract\"",
    "row_count": 1453136
  },
  "physical_columns": [
    {
      "name": "ANIMAL_FLAG",
      "type": "TEXT",
      "nullability": "Nullability.NULLABLE"
    }
  ],
  "calculated_fields": {
    "Municipality Name (ifnull)": {
      "description": "Municipality name with NULL values replaced by 'Unknown'.",
      "formula": "IFNULL(\"MUNICIPALITY_NAME\", 'Unknown')"
    }
  },
  "parameters": {
    "Metric Selector": ["Crash Count", "Victim Count"]
  },
  "export": {
    "column_order": "alphabetical",
    "format": "CSV",
    "null_value": "\\N",
    "row_order": "DATE_OF_LOSS_YEAR ascending, followed by all remaining exported columns ascending"
  }
}
```

The real file contains all physical columns, all four calculated fields, and both
parameter lists.

### Fields

| Key | Type | Meaning |
|---|---|---|
| `source.file` | string | Path to the Hyper file, relative to the project root |
| `source.table` | string | SQL-qualified source table, including quotes |
| `source.row_count` | integer | Number of source rows, equal to CSV data rows |
| `physical_columns` | array | Source columns with `name`, `type`, and `nullability` |
| `calculated_fields` | object | Export-name keyed objects with `formula` and `description` |
| `parameters` | object | Tableau parameter names and allowed values |
| `export.format` | string | Always `CSV` |
| `export.null_value` | string | Literal `\N`; JSON escapes it as `"\\N"` |
| `export.column_order` | string | `alphabetical` |
| `export.row_order` | string | Human-readable description of the deterministic sort |

### Details

- **Column names are unquoted** in `physical_columns` (`ANIMAL_FLAG`, not
  `"ANIMAL_FLAG"`).
- **Types are physical Hyper types** such as `TEXT`, `BIG_INT`, and `DOUBLE`.
- **Nullability values** come from the Hyper API, e.g.
  `Nullability.NULLABLE`.
- **`calculated_fields` includes derived CSV columns and Tableau-only fields.**
  The two `(ifnull)` fields are materialized; `Metric Selector` and
  `Crash Breakdown 2` are documented but not materialized.
- **Formulas are summaries, not authoritative Tableau syntax** for the
  parameter-driven fields. The workbook XML is authoritative.
- **Serialization** uses `json.dump(..., indent=2, sort_keys=True,
  ensure_ascii=False)` plus a trailing newline. Key order in the file is
  alphabetical, not the order shown above.

### Schema evolution

The export validates a set of 25 expected physical columns:

- **Missing expected column:** the run fails.
- **Extra physical column:** the run prints a warning and still exports the column.

Because the export uses all discovered physical columns, a source with extra
columns produces a CSV with more than 27 columns. In that case, the schema and this
reference are stale until updated. Always inspect `physical_columns` and the CSV
header after a source refresh.

## Hyper inspection metadata

Path: `data/metadata/hyper_schema.json`

This file is written by `inspect_hyper.py`. It documents the Hyper source for
inspection and is not the canonical CSV schema.

### Shape

```json
{
  "file": "/absolute/path/to/data/raw/tableau/extracted/2021-2025 public data set.hyper",
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

### Differences from the export schema

| Aspect | Export schema | Hyper inspection schema |
|---|---|---|
| Path | Relative | Absolute |
| Column key | `physical_columns` | `columns` |
| Column names | Unquoted | Quoted Hyper names |
| Type field | `type` | `type` |
| Nullability field | `nullability` | `nullable` |
| Calculated fields | Included | Not included |
| Parameters | Included | Not included |
| Canonical for CSV | Yes | No |

The quoted names reflect the `str()` representation of Hyper `Name` objects. This
is expected, not a bug.

## Catalogue payload

Path: `data/metadata/catalogue.json`

This file is written by `catalogue.py` and contains the raw `result` object from
the BC Data Catalogue `package_show` API. It is not produced by `./run`.

Useful top-level keys include:

| Key | Contents |
|---|---|
| `title`, `name`, `id` | Dataset identity |
| `notes` | Short description |
| `data_quality` | Official data-quality caveats |
| `lineage_statement` | Source, exclusions, and capture context |
| `license_id`, `license_title`, `license_url` | Data licence |
| `organization` | Publishing organization |
| `contacts` | Point of contact |
| `resources` | Distribution link and field list |
| `metadata_created`, `metadata_modified` | Catalogue record timestamps |

The payload is a catalogue record, not a data dictionary for the current extract.
It can lag the workbook, and its resource URL points to the Tableau Public view
rather than a direct CSV.

## Which file should I use?

| Need | File |
|---|---|
| Parse or validate the CSV | Export schema |
| Know the source table and physical types | Either schema, but prefer the export schema for CSV work |
| Check how a field looked in the Hyper source | Hyper inspection schema |
| Cite the official dataset, licence, or caveats | Catalogue payload or [Caveats and licence](caveats-and-licence.md) |
| Understand the current column set | `data/processed/icbc_reported_crashes.csv` header and the export schema |

## Related pages

- [Dataset schema](dataset-schema.md)
- [Data layout](data-layout.md)
- [Pipeline script reference](pipeline-scripts.md)
- [Fetch dataset metadata](../how-to-guides/fetch-dataset-metadata.md)
