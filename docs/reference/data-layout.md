# Data layout

This page describes every directory and artifact the project reads or writes.

## Directory tree

```text
.
├── run                                  # four-stage pipeline wrapper
├── pyproject.toml                       # project metadata and dependencies
├── uv.lock                              # locked Python dependency graph
├── README.md
├── src/
│   └── icbc_reported_crashes/
│       ├── __init__.py
│       ├── catalogue.py
│       ├── export_dashboard_data.py
│       ├── extract_tableau.py
│       ├── inspect_hyper.py
│       ├── inspect_tableau.py
│       ├── inspect_workbook.py
│       ├── profile_hyper.py
│       ├── split_records.py
│       └── tableau.py
├── data/
│   ├── raw/                             # ignored by git
│   │   └── tableau/
│   │       ├── ICBCReportedCrashes.twb  # downloaded ZIP container
│   │       └── extracted/
│   │           ├── 2021-2025 public data set.hyper
│   │           ├── ICBC Reported Crashes.twb
│   │           ├── Caveats (Public data sets - Metadata) (2).hyper
│   │           ├── federated_0bn82t81yj94ap1fr622a1.hyper
│   │           ├── federated_1oll1kn0e530bn1d8o3ar0.hyper
│   │           └── federated_1p7tlca06yuz791brgeig0.hyper
│   ├── processed/
│   │   ├── icbc_reported_crashes.csv    # ignored by git
│   │   ├── icbc_reported_crashes.schema.json  # ignored by git
│   │   └── records/                     # tracked in git
│   │       └── <year>/<MM_MONTH>/<D_WEEKDAY>/<HHMM_HHMM>.csv
│   └── metadata/                        # created on demand, not ignored by default
│       ├── catalogue.json
│       └── hyper_schema.json
└── docs/
```

The exact files inside `data/raw/tableau/extracted/` depend on the workbook
archive. The names above are the ones used by the scripts.

## Artifact reference

| Path | Produced by | Used by | Tracked | Approximate size |
|---|---|---|---|---|
| `data/raw/tableau/ICBCReportedCrashes.twb` | `tableau.py` | `extract_tableau.py`, `inspect_tableau.py` | No | 24 MB |
| `data/raw/tableau/extracted/2021-2025 public data set.hyper` | `extract_tableau.py` | export, profile, `inspect_hyper.py` | No | 45 MB |
| `data/raw/tableau/extracted/ICBC Reported Crashes.twb` | `extract_tableau.py` | `inspect_workbook.py` | No | 853 KB |
| Other extracted `.hyper` files | `extract_tableau.py` | Inspection only | No | 64–128 KB each |
| `data/processed/icbc_reported_crashes.csv` | `export_dashboard_data.py` | `split_records.py`, analysis | No | 289 MB |
| `data/processed/icbc_reported_crashes.schema.json` | `export_dashboard_data.py` | Documentation, downstream tools | No | 4.5 KB |
| `data/processed/records/` | `split_records.py` | Analysis, git history | Yes | 290 MB, 3,360 files |
| `data/metadata/catalogue.json` | `catalogue.py` | Provenance and citation | No (untracked by default) | A few KB |
| `data/metadata/hyper_schema.json` | `inspect_hyper.py` | Inspection | No (untracked by default) | A few KB |

Sizes and counts are from the documented 2021–2025 snapshot. The CSV and records
are intentionally not linked to each other by a manifest; consistency is checked
by [Verify an export](../how-to-guides/verify-an-export.md).

## Tracked and ignored files

The relevant `.gitignore` rules are:

```gitignore
data/raw/
data/processed/icbc_reported_crashes.csv
data/processed/icbc_reported_crashes.schema.json
*.log
```

Consequences:

- `data/raw/` is always local. A clone must download and extract the source.
- The full CSV and its schema are local. They are large and reproducible; keeping
  them out of git keeps the repository manageable.
- `data/processed/records/` is **not** ignored. The partition tree is the
  versioned, shareable representation of the processed data.
- `data/metadata/` is not ignored. Files created there show up as untracked until
  you decide whether to commit them.
- `hyperd.log`, if the Hyper process writes one, is ignored by `*.log`.

## Regeneration order

```text
tableau.py
    └── extract_tableau.py
            ├── inspect_tableau.py        (optional, reads the downloaded archive)
            ├── inspect_workbook.py       (optional, reads the extracted XML)
            ├── inspect_hyper.py          (optional, writes data/metadata/)
            ├── profile_hyper.py          (optional, prints only)
            └── export_dashboard_data.py
                    ├── split_records.py
                    └── catalogue.py      (independent; network only)
```

Each downstream stage needs the artifact from the stage above it. The inspection
and catalogue scripts are optional and do not feed the main pipeline.

## Hardcoded filenames

Several scripts use exact filenames rather than discovering them:

| Script | Hardcoded value |
|---|---|
| `tableau.py` | output filename `ICBCReportedCrashes.twb` |
| `extract_tableau.py` | input filename `ICBCReportedCrashes.twb` |
| `inspect_workbook.py` | `ICBC Reported Crashes.twb` |
| `inspect_hyper.py`, `profile_hyper.py`, export | `2021-2025 public data set.hyper` |
| `inspect_hyper.py`, `profile_hyper.py` | schema/table `Extract.Extract` |
| export | discovers the source table by its column set, then exports all its physical columns |
| split | `data/processed/icbc_reported_crashes.csv` |

If a new source release changes the embedded filename, the affected scripts will
fail until the constants are updated. The export's table discovery is more
flexible: it finds a table by its column set rather than requiring the exact table
name.

## Related pages

- [Records layout](records-layout.md)
- [Metadata files](metadata-files.md)
- [Dataset schema](dataset-schema.md)
- [Pipeline scripts](pipeline-scripts.md)
