# ICBC Reported Crashes

A small, reproducible data pipeline for the
[ICBC Reported Crashes](https://catalogue.data.gov.bc.ca/dataset/icbc-reported-crashes)
open dataset. It downloads the public Tableau workbook, extracts the embedded
Hyper data, exports a deterministic CSV with machine-readable schema metadata,
and splits the export into small files by year, month, weekday, and time of day.

The repository currently describes the **2021–2025 public extract**: 1,453,136
aggregated records covering 1,465,435 crashes and 347,413 victims. Source data is
published by ICBC and is subject to revision.

> **Independent project.** This repository is not affiliated with or endorsed by
> ICBC. Read the [data caveats and licence](docs/reference/caveats-and-licence.md)
> before publishing analysis based on this data.

## Quick start

Requirements:

- [git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/) (it can install the required Python 3.14)
- network access to Tableau Public
- about 700 MB of free disk space

```bash
git clone git@github.com:galenseilis/icbc-reported-crashes.git
cd icbc-reported-crashes
uv sync
./run
```

`./run` performs the four main stages:

1. download the Tableau workbook;
2. extract its embedded `.hyper` and `.twb` files;
3. export the crash table to `data/processed/icbc_reported_crashes.csv` and write
   `data/processed/icbc_reported_crashes.schema.json`;
4. split the export into `data/processed/records/`.

A successful run ends with a summary such as:

```text
Processing complete.
Input rows:  1,453,136
Output rows: 1,453,136
Files created: 3,360
Output root: /path/to/icbc-reported-crashes/data/processed/records
```

The full CSV and schema are git-ignored because of their size. The partitioned
record files under `data/processed/records/` are tracked in git.

## Documentation

The documentation follows the [Diátaxis](https://diataxis.fr/) framework. Start
with the tutorial if this is your first time using the project.

| | |
|---|---|
| **Learning** | [Build and explore your first export](docs/tutorials/first-export.md) |
| **Doing a task** | [How-to guides](docs/how-to-guides/index.md) |
| **Looking something up** | [Reference](docs/reference/index.md) |
| **Understanding** | [Explanation](docs/explanation/index.md) |

The full map, including recommended reading paths, is in
[`docs/index.md`](docs/index.md).

## Repository layout

```text
.
├── run                              # four-stage pipeline entry point
├── pyproject.toml                   # Python project metadata and dependencies
├── src/icbc_reported_crashes/       # pipeline and inspection scripts
├── data/
│   ├── raw/                         # downloaded and extracted source files (ignored)
│   ├── processed/                   # full CSV, schema, and partitioned records
│   └── metadata/                    # optional inspection/catalogue JSON (created on demand)
└── docs/                            # Diátaxis documentation
```

See [Data layout](docs/reference/data-layout.md) for the complete file reference.

## Common commands

```bash
# Re-run everything from the public source
./run

# Rebuild only the CSV and schema from an existing Hyper extract
uv run src/icbc_reported_crashes/export_dashboard_data.py

# Rebuild only the partitioned records from an existing CSV
uv run src/icbc_reported_crashes/split_records.py

# Inspect the downloaded workbook and its embedded data
uv run src/icbc_reported_crashes/inspect_tableau.py
uv run src/icbc_reported_crashes/inspect_hyper.py

# Fetch the BC Data Catalogue record (not part of ./run)
uv run src/icbc_reported_crashes/catalogue.py
```

Run these commands from the repository root. Several scripts use paths relative
to the current working directory.

## Data source and licence

- Catalogue record: [ICBC Reported Crashes](https://catalogue.data.gov.bc.ca/dataset/icbc-reported-crashes)
- Tableau Public workbook: [ICBCReportedCrashes.twb](https://public.tableau.com/workbooks/ICBCReportedCrashes.twb)
- Data licence: [ICBC Open Data Licence](https://www.icbc.com/policies/Pages/open-data-licence.aspx)

Required attribution:

> Contains information licensed under ICBC's Open Data Licence.

The repository does not contain a licence file for the code itself. The ICBC
Open Data Licence applies to the data, not automatically to the source code.

## Status and scope

- The pipeline is a full refresh, not an incremental update. The source is an
  annual snapshot, so rerunning it replaces the processed artifacts.
- There is no test suite or CI configuration yet.
- The declared console script `icbc-reported-crashes` is not implemented; run the
  modules directly as shown above.
- The dataset is aggregated. Count rows with `SUM(TOTAL_CRASHES)`, not `COUNT(*)`.
  See [Data limitations](docs/explanation/data-limitations.md).
