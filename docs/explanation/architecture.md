# Architecture

The project is a linear, file-based pipeline with two optional side branches. It
has no database, service, scheduler, or shared application state. Every stage
reads files and writes files, so a stage can be rerun or replaced without
rewriting the others.

## Data flow

```text
public.tableau.com
        │
        │  tableau.py
        ▼
data/raw/tableau/ICBCReportedCrashes.twb        (ZIP container)
        │
        │  extract_tableau.py
        ▼
data/raw/tableau/extracted/
        ├── 2021-2025 public data set.hyper ──┬──► export_dashboard_data.py
        │                                     ├──► inspect_hyper.py
        │                                     └──► profile_hyper.py
        └── ICBC Reported Crashes.twb ───────────► inspect_workbook.py
                                                │
                                                ▼
data/processed/icbc_reported_crashes.csv
data/processed/icbc_reported_crashes.schema.json
                                                │
                                                │  split_records.py
                                                ▼
data/processed/records/<year>/<month>/<weekday>/<time>.csv

catalogue.data.gov.bc.ca
        │
        │  catalogue.py
        ▼
data/metadata/catalogue.json
```

The export is the narrow waist of the system. Everything upstream produces or
describes the Hyper source; everything downstream consumes the CSV and schema.
That boundary is what makes the analysis artifacts portable.

## Stages and contracts

| Stage | Input contract | Output contract | Side effects |
|---|---|---|---|
| Download | A public workbook URL | A file at a fixed path | Network request |
| Extract | A ZIP workbook | `.hyper` and `.twb` files with fixed names | Overwrites extracted files |
| Export | A Hyper file with a discoverable crash table | CSV with a stable header, schema JSON | Writes large files |
| Split | A CSV with four temporal columns | A path-indexed tree of CSV files | Overwrites files, leaves stale files |
| Inspect | A workbook, Hyper file, or export | Console output and optional metadata | May write `data/metadata/` |
| Catalogue | A dataset ID | Raw CKAN JSON | Network request |

Each contract is a file or a filename pattern. There is no in-memory interface
between stages, which means you can inspect, replace, or rerun any stage
independently. It also means a broken filename or schema is discovered only when
the next stage runs.

## Why the pipeline is shaped this way

### Raw data is preserved separately

The downloaded workbook and extracted files live under `data/raw/`, which is
git-ignored. The raw files are large (about 70 MB) and reproducible from the
public source. Keeping them separate from processed data makes it clear which
files are inputs and which are derived.

### Hyper is flattened to CSV

Hyper is Tableau's format. Reading it requires the Tableau Hyper API and a local
Hyper process. CSV is portable, inspectable with ordinary tools, and usable from
Python, R, SQL loaders, spreadsheets, and web applications. The export stage pays
the Tableau-specific cost once and gives every downstream consumer a simple format.

The tradeoff is size: the CSV is about 289 MB, and the split tree is about 290 MB.
The project accepts that cost in exchange for portability and transparent diffs.

### The partition tree is the versioned representation

Git is good at text and bad at large binaries. The full CSV is ignored, but the
partition tree is tracked. Splitting by time makes each file small enough to
review, and makes a year or month of data addressable without reading the whole
export. The path itself is the index, so no separate catalogue is needed.

The tradeoff is that the repository contains thousands of small files and a clone
is larger than a code-only project. See
[Design decisions](design-decisions.md) for the alternatives.

### Table discovery is by column set

The export does not trust the table name alone. It enumerates schemas and tables,
then selects the table containing all 25 expected physical columns. This tolerates
Tableau's internal table naming and catches the case where the extract contains
more than one candidate. If no table matches, the run stops rather than exporting
an unrelated table.

The inspection and profiling scripts are less flexible: they hardcode
`Extract.Extract` because they are diagnostic tools, not the production path.

### Metadata is optional

The catalogue fetch and the Hyper/workbook inspections are not part of `./run`.
They answer provenance and debugging questions, and their outputs are not needed to
produce the CSV or partitions. Keeping them separate means a network outage at the
catalogue does not block a data refresh.

## Failure boundaries

The stages are separate processes. Most failures leave the last successful
artifact in place, and a rerun picks up from that artifact. This is convenient for
development but has two consequences:

1. **The wrapper is not fail-fast.** `./run` does not stop after a failed stage, so
   later stages may run against old files. Read each stage's output.
2. **Outputs are overwritten, not synchronized.** A rerun replaces files it
   generates but never deletes files it no longer generates. A source that loses a
   partition can leave a stale file behind.

Both behaviors are documented in
[Troubleshoot the pipeline](../how-to-guides/troubleshoot-pipeline.md) and
[Rebuild only the partitioned records](../how-to-guides/rebuild-partitioned-records.md).

## Scale

The documented snapshot has:

- 1,453,136 records and 27 columns;
- 1,465,435 crashes and 347,413 victims;
- a 289 MB CSV;
- 3,360 partition files totaling 290 MB;
- five years (2021–2025) and eight time buckets per day.

The design is sized for this scale: a single-process pandas split, no sharding, no
parallelism, and no database. A much larger source would need a different storage
and partitioning strategy.

## Related pages

- [Data provenance](data-provenance.md)
- [Deterministic exports](deterministic-exports.md)
- [Design decisions](design-decisions.md)
- [Pipeline script reference](../reference/pipeline-scripts.md)
