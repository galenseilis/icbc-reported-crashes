# Pipeline script reference

The project is a set of standalone Python scripts. None of them accept command-line
arguments or environment variables; behavior is controlled by constants in the
source. Run them from the repository root with `uv run`.

## Summary

| Script | Stage | Reads | Writes | Network |
|---|---|---|---|---|
| `run` | Orchestration | — | — | Indirectly |
| `tableau.py` | Download | — | `data/raw/tableau/ICBCReportedCrashes.twb` | Yes |
| `extract_tableau.py` | Extract | downloaded workbook | `data/raw/tableau/extracted/*` | No |
| `inspect_tableau.py` | Inspect | downloaded workbook | — | No |
| `inspect_workbook.py` | Inspect | extracted workbook XML | — | No |
| `inspect_hyper.py` | Inspect | main Hyper extract | `data/metadata/hyper_schema.json` | No |
| `profile_hyper.py` | Profile | main Hyper extract | — | No |
| `export_dashboard_data.py` | Export | main Hyper extract | CSV and export schema | No |
| `split_records.py` | Split | exported CSV | `data/processed/records/` tree | No |
| `catalogue.py` | Metadata | BC Data Catalogue API | `data/metadata/catalogue.json` | Yes |

All scripts live in `src/icbc_reported_crashes/`.

## Common conventions

- **Working directory:** most scripts resolve project paths from
  `Path(__file__).resolve().parents[2]`, so they work from any directory.
  `split_records.py` is the exception: it uses paths relative to the current
  working directory and should be run from the repository root.
- **No arguments:** scripts ignore `sys.argv`. To change a path, URL, column set,
  or ordering, edit the constants in the script.
- **No configuration file:** there are no `.env` files, config files, or CLI flags.
- **Errors:** most errors are uncaught exceptions, so Python exits with status 1
  and prints a traceback. The exception is `export_dashboard_data.py`, which
  returns status 1 with a short message when the Hyper file is missing.
- **Overwrites:** output files are overwritten. Directories are created on demand.
  No script deletes stale outputs.

## `run`

Path: `run` (Bash, executable)

Runs the four main stages in order:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run ./src/icbc_reported_crashes/extract_tableau.py
uv run ./src/icbc_reported_crashes/export_dashboard_data.py
uv run --with pandas ./src/icbc_reported_crashes/split_records.py
```

Behavior and caveats:

- The commands are separate lines, not joined with `&&`.
- The script does not use `set -e` or `set -o pipefail`.
- The script's exit status is the exit status of the final command.
- A failure in an earlier stage does not stop later stages, and can be masked by a
  final success. Read each stage's output.
- `--with pandas` is redundant because pandas is already a project dependency.
- Run `./run` from the repository root; its relative script paths depend on the
  current directory.

## `tableau.py`

Path: `src/icbc_reported_crashes/tableau.py`

Downloads the public Tableau workbook.

- **Source URL:** `https://public.tableau.com/workbooks/ICBCReportedCrashes.twb`
- **Output:** `data/raw/tableau/ICBCReportedCrashes.twb`
- **Timeout:** 60 seconds
- **Headers:** project user agent and `Accept: */*`
- **Prints:** HTTP status, content type, content length, final URL, output path,
  and byte count.
- **Does not:** validate that the response is a ZIP file, retry, or resume.

The downloaded file keeps the `.twb` extension but is a ZIP container. See
[Tableau workbook anatomy](../explanation/tableau-workbook-anatomy.md).

## `extract_tableau.py`

Path: `src/icbc_reported_crashes/extract_tableau.py`

Unpacks `.hyper` and `.twb` entries from the downloaded workbook.

- **Input:** `data/raw/tableau/ICBCReportedCrashes.twb`
- **Output directory:** `data/raw/tableau/extracted/`
- **Selection:** entries whose filenames end in `.hyper` or `.twb`,
  case-insensitively, anywhere in the archive.
- **Naming:** each entry is written using its base filename, so nested archive
  paths are flattened.
- **Prints:** counts by type, uncompressed size, output path, and SHA-256 for each
  extracted file.
- **Overwrites:** files with the same base name.
- **Does not:** delete files from previous extractions, preserve archive directory
  structure, or verify the entries after writing.

## `inspect_tableau.py`

Path: `src/icbc_reported_crashes/inspect_tableau.py`

Lists the entries in the downloaded workbook archive.

- **Input:** `data/raw/tableau/ICBCReportedCrashes.twb`
- **Prints:** archive path, number of entries, then each entry's uncompressed size,
  compressed size, and filename.
- **Writes:** nothing.
- **Fails:** if the file is missing or is not a valid ZIP archive.

## `inspect_workbook.py`

Path: `src/icbc_reported_crashes/inspect_workbook.py`

Parses the extracted workbook XML and prints a structural summary.

- **Input:** `data/raw/tableau/extracted/ICBC Reported Crashes.twb`
- **Prints:** workbook build, platform, version, repository ID, revision;
  datasources and columns; parameters and allowed values; calculated fields and
  formulas; target-field matches; worksheet names; dashboard names.
- **Writes:** nothing.
- **Exit status:** returns 1 if the workbook is missing; otherwise 0.
- **Namespace handling:** XML tags are compared without namespaces.

The target-field section matches a small hardcoded set of internal names and
captions. Some captions can appear under `Not found` even when the field exists
under an internal name.

## `inspect_hyper.py`

Path: `src/icbc_reported_crashes/inspect_hyper.py`

Opens the main Hyper extract and prints its catalog and a sample.

- **Input:** `data/raw/tableau/extracted/2021-2025 public data set.hyper`
- **Output:** `data/metadata/hyper_schema.json`
- **Prints:** schemas, tables, row count, column definitions (ordinal, name, type,
  nullability), and ten sample rows.
- **Table access:** uses the hardcoded table `"Extract"."Extract"` for the row
  count, definition, and sample, while the schema listing enumerates all tables.
- **Writes:** the JSON file is created with `indent=2` and a trailing newline.
- **Fails:** if the Hyper file is missing or the hardcoded table does not exist.

This metadata file describes the Hyper source. It is not the canonical CSV schema.

## `profile_hyper.py`

Path: `src/icbc_reported_crashes/profile_hyper.py`

Prints a statistical profile of the main Hyper table.

- **Input:** `data/raw/tableau/extracted/2021-2025 public data set.hyper`
- **Writes:** nothing.
- **Prints:**
  - row, crash, and victim totals;
  - rows, crashes, and victims by year;
  - `TOTAL_CRASHES` and `TOTAL_VICTIMS` distributions;
  - latitude/longitude bounds and non-null counts;
  - null and distinct counts for all 25 physical columns;
  - a duplicate-row check across all 25 columns;
  - value distributions for selected categorical columns;
  - ten sample rows.
- **Table access:** hardcodes the `Extract.Extract` schema and table and the 25
  physical column names.
- **Fails:** with a custom `FileNotFoundError` if the Hyper file is missing.

The duplicate check can be expensive because it groups by every physical column.

## export_dashboard_data

Path: `src/icbc_reported_crashes/export_dashboard_data.py`

Exports the crash table to CSV and writes schema metadata.

- **Input:** `data/raw/tableau/extracted/2021-2025 public data set.hyper`
- **Outputs:**
  - `data/processed/icbc_reported_crashes.csv`
  - `data/processed/icbc_reported_crashes.schema.json`
- **Table discovery:** enumerates schemas and tables through the Hyper catalog,
  then selects the table whose column names contain all 25 expected physical
  columns. Exactly one match is required.
- **Validation:** warns about extra physical columns and fails on missing expected
  columns.
- **Exported columns:** all discovered physical columns (25 in the documented
  snapshot) plus `Municipality Name (ifnull)` and `Street Full Name (ifnull)`,
  sorted case-insensitively by name. The documented snapshot therefore has 27
  columns. Extra source columns are warned about and included, so a future schema
  can produce more columns.
- **Null encoding:** literal `\N` for every null value.
- **Row ordering:** `DATE_OF_LOSS_YEAR` ascending, then `MONTH_OF_YEAR`
  chronologically, then every other exported column ascending with nulls first.
- **Progress:** prints a line every 100,000 exported rows.
- **Post-export validation:** re-reads the CSV, checks the row count against the
  Hyper count, and checks that the header is alphabetically sorted.
- **Exit status:** returns 1 if the Hyper file is missing; returns 0 on success.
  Other failures raise exceptions.
- **Does not:** split the CSV, download files, or materialize the aggregate
  `Metric Selector` or parameter-controlled `Crash Breakdown 2` field.

See [Deterministic exports](../explanation/deterministic-exports.md) for the design
rationale.

## split_records

Path: `src/icbc_reported_crashes/split_records.py`

Splits the exported CSV into a directory tree.

- **Input:** `data/processed/icbc_reported_crashes.csv`, resolved relative to the
  current working directory.
- **Output root:** `data/processed/records/`, also relative to the current
  working directory.
- **Required columns:** `DATE_OF_LOSS_YEAR`, `MONTH_OF_YEAR`, `DAY_OF_WEEK`,
  `TIME_CATEGORY`.
- **Grouping:** `pandas.DataFrame.groupby` on those four columns with
  `dropna=False` and `sort=True`.
- **Output file:** one CSV per group, written with `index=False`.
- **Prints:** each created path and row count, then input rows, output rows, file
  count, and the resolved output root.
- **Overwrites:** files with the same path.
- **Does not:** delete stale files, write a manifest, or validate row counts after
  writing.
- **Fails:** if the CSV is missing, required columns are absent, or a temporal
  value cannot be mapped (null or unknown month/weekday).

See [Records layout](records-layout.md) for the naming rules.

## catalogue

Path: `src/icbc_reported_crashes/catalogue.py`

Fetches the BC Data Catalogue record.

- **API:** `https://catalogue.data.gov.bc.ca/api/3/action/package_show`
- **Dataset ID:** `icbc-reported-crashes`
- **Output:** `data/metadata/catalogue.json`
- **Request:** 30-second timeout, JSON accept header, project user agent.
- **Prints:** dataset title, ID, name, resource count, and each resource's name,
  ID, format, and URL.
- **Fails:** with `RuntimeError` if the API returns `success: false`.
- **Does not:** download the resource itself, validate the payload against a
  schema, or run as part of `./run`.

## Packaging entry point

`pyproject.toml` declares:

```toml
[project.scripts]
icbc-reported-crashes = "icbc_reported_crashes:main"
```

The package's `__init__.py` is empty, so this entry point is not implemented. Use
the module scripts directly.
