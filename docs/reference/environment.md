# Environment

This page lists the runtime requirements, dependencies, network endpoints, and
configuration surface of the project.

## Runtime

| Requirement | Value |
|---|---|
| Python | `>=3.14` (declared in `pyproject.toml`) |
| Package manager | [uv](https://docs.astral.sh/uv/) |
| Shell for `./run` | Bash-compatible shell |
| Disk | About 700 MB for raw and processed artifacts; allow about 1 GB during a refresh |
| Network | Tableau Public for the workbook; BC Data Catalogue for optional metadata |

`uv.lock` pins the resolved dependency graph. `uv sync` creates the environment;
`uv run` uses it automatically and will sync it if needed.

On Windows, use WSL, Git Bash, or invoke the four module commands directly instead
of `./run`.

## Dependencies

Declared in `pyproject.toml`:

| Package | Constraint | Used for |
|---|---|---|
| `pandas` | `>=3.0.5` | Splitting the CSV |
| `tableauhyperapi` | `>=0.0.26225` | Reading the Hyper extract |

Build system:

| Package | Constraint |
|---|---|
| `uv_build` | `>=0.12.3,<0.13.0` |

There are no development, test, or documentation dependencies declared.

## Project metadata

| Field | Value |
|---|---|
| Name | `icbc-reported-crashes` |
| Version | `0.1.0` |
| Requires Python | `>=3.14` |
| Build backend | `uv_build` |
| Console script | `icbc-reported-crashes = "icbc_reported_crashes:main"` (not implemented) |

See [Pipeline script reference: Packaging entry point](pipeline-scripts.md#packaging-entry-point).

## Network endpoints

| Endpoint | Used by | Authentication | Timeout |
|---|---|---|---|
| `https://public.tableau.com/workbooks/ICBCReportedCrashes.twb` | `tableau.py` | None | 60 s |
| `https://catalogue.data.gov.bc.ca/api/3/action/package_show` | `catalogue.py` | None | 30 s |

The Hyper API runs a local Hyper process. The scripts pass
`Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU`, so inspection, profiling, and export
do not send Tableau usage telemetry.

## Configuration

There are no environment variables, `.env` files, YAML/TOML config files, CLI
flags, or database connections. Behavior is controlled by constants in the
scripts:

| Constant | Script | Purpose |
|---|---|---|
| `WORKBOOK_URL` | `tableau.py` | Source workbook |
| `HYPER_PATH` / `HYPER_FILE` | export, profile, inspect | Main Hyper extract |
| `EXPECTED_COLUMNS` | export | Required physical columns |
| `CALCULATED_FIELDS`, `PARAMETERS` | export | Schema metadata |
| `CSV_PATH`, `SCHEMA_PATH` | export | Output paths |
| `INPUT_PATH`, `OUTPUT_ROOT` | split | Input CSV and partition root |
| `API_BASE`, `DATASET_ID` | catalogue | Catalogue API and dataset |
| `ROOT`, `RAW_DIR`, `METADATA_DIR` | various | Project paths |

Most scripts resolve paths relative to the repository, not the current directory.
`split_records.py` is the exception and must run from the repository root.

## Reproducibility notes

- The Python dependencies are locked in `uv.lock`.
- The pipeline does not record a run timestamp, source ETag, or checksum of the
  downloaded workbook in the processed artifacts.
- The export is designed to be deterministic for a fixed source and code version:
  stable column order, stable row order, and a fixed null marker.
- Upgrading pandas can change CSV quoting or formatting in the split stage. If you
  need byte-for-byte reproducibility, keep the lockfile fixed.

## Verification commands

```bash
uv --version
uv run python --version
uv run python -c "import pandas, tableauhyperapi; print(pandas.__version__)"
```

To confirm that the environment matches the project:

```bash
uv sync --locked
```

`--locked` fails instead of updating the lockfile.

## Related pages

- [Data layout](data-layout.md)
- [Pipeline scripts](pipeline-scripts.md)
- [Deterministic exports](../explanation/deterministic-exports.md)
