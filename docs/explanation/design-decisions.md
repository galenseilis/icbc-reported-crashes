# Design decisions

This page records the main design choices and the tradeoffs behind them. The goal
is to make the project easy to inspect and reproduce, not to build a general-purpose
data platform.

## Scripts instead of a library API

The pipeline is a set of standalone scripts under `src/icbc_reported_crashes/`.
Each script has a `main()` and is run directly. There is no supported Python API,
CLI framework, plugin system, or service layer.

**Why:** the project is small and the stages are sequential. A script is the
shortest path from "read this file" to "write that file", and a reader can follow
it top to bottom.

**Cost:** there is no stable programmatic interface, no argument parsing, and the
declared console entry point is unimplemented. Reuse means importing functions from
a script or copying logic.

**When to reconsider:** if other tools need to call the pipeline, add a small,
typed API or a CLI with explicit arguments and exit codes. Keep the scripts as thin
wrappers around it.

## Full refresh instead of incremental updates

Every run replaces the processed artifacts from a complete public snapshot.

**Why:** the source is an annual snapshot, not an event stream. There is no stable
crash identifier to upsert against, and the aggregate grain can change when ICBC
revises counts. A full refresh avoids pretending the data is append-only.

**Cost:** the export rewrites a 289 MB CSV and the split rewrites 3,360 files. A
source revision can produce a large diff.

**When to reconsider:** if the source publishes stable identifiers and incremental
updates, or if the extract becomes too large for a single process. That would need
a different data model, not just a faster loop.

## CSV as the interchange format

The export is a CSV plus a JSON schema.

**Why:** CSV is portable, inspectable with ordinary tools, and readable by Python,
R, SQL loaders, spreadsheets, and web applications. It does not require the Tableau
Hyper API. The schema carries the types and provenance that the CSV header cannot.

**Cost:** the file is large, untyped, and has no compression. Readers must handle
the `\N` sentinel and parse numeric columns. CSV cannot represent nested data.

**Alternatives considered:**

| Format | Why not chosen |
|---|---|
| Parquet | Smaller and typed, but adds a dependency and is less universally inspectable |
| SQLite | Queryable, but adds a database artifact and schema migration concerns |
| JSON Lines | Verbose and slower to scan for this row count |
| Keep Hyper only | Requires Tableau tooling; poor portability |

**When to reconsider:** if downstream users need typed columns, predicate pushdown,
or much larger data. Parquet would be the natural next step, with CSV retained as a
compatibility export.

## A partition tree as the versioned representation

The full CSV is git-ignored. The partitioned records are tracked.

**Why:** git handles many small text files better than one 289 MB file, and a path
like `2021/01_JANUARY/1_MONDAY/0900_1159.csv` is addressable without a separate
index. A year or month can be reviewed on its own.

**Cost:** the repository carries thousands of files and a clone is large. There is
no manifest, so consistency is checked by convention and by
[Verify an export](../how-to-guides/verify-an-export.md). The splitter does not
delete stale files.

**When to reconsider:** if clone size or file count becomes a problem. Alternatives
include Git LFS for the full CSV, a single compressed archive, or keeping only
aggregate tables in git and publishing the full export as a release asset.

## Hybrid case naming in the output

Physical columns keep the source's uppercase names. The two derived fields use
mixed-case names with spaces and parentheses, matching the Tableau captions.

**Why:** the physical columns remain recognizable against the source and the
workbook. The derived fields are clearly marked as additions.

**Cost:** column names are inconsistent, and the derived fields sort in the middle
of the alphabetical header rather than at the end. Consumers that normalize names
may collide `MUNICIPALITY_NAME` and `Municipality Name (ifnull)`.

**When to reconsider:** if the CSV becomes a long-lived public interface. A
normalized naming convention would be cleaner, but it would break existing queries.

## `\N` as the null marker

**Why:** it is unambiguous against `N`, `NA`, `NULL`, and empty strings, and it is a
common analytical export convention.

**Cost:** every reader must configure it. The benefit is that a missing value can
never be confused with a valid flag value or a literal string.

## Minimal validation at the export boundary

The export checks row count and header order. The split checks required columns.
There is no schema registry, checksum manifest, or content validation.

**Why:** the most common failure is an interrupted export or a source schema drift,
and a few cheap checks catch those. The project does not claim to be a data-quality
system.

**Cost:** a changed null rate, an unexpected categorical value, or a stale
partition can pass silently. Those checks are documented as separate tasks rather
than enforced.

**When to reconsider:** if the data is used in an automated publication. Add
schema validation, expected value sets, null-rate thresholds, and a checksum
manifest.

## Hardcoded paths and filenames

Constants such as `HYPER_PATH` and `EXPECTED_COLUMNS` live in the scripts.

**Why:** the project has one source and one layout. Constants are easier to read
than a configuration layer, and they keep the number of moving parts low.

**Cost:** a source release that renames the embedded file requires a code change.
Running `split_records.py` from the wrong directory writes to the wrong place or
fails.

**When to reconsider:** if the pipeline supports multiple sources, environments, or
years with different layouts. Then paths and column expectations should be
configuration, not constants.

## No test suite or CI

There is no automated test suite, CI workflow, or release process.

**Why:** the project is exploratory and the source is external and revised. The
current checks are the validation built into the export and the manual verification
guide.

**Cost:** changes to the scripts are not protected by regression tests, and source
drift is discovered at runtime. The documented snapshot can become stale without
any warning.

**When to reconsider:** before relying on the pipeline for recurring publication.
The highest-value tests would be a tiny fixture Hyper file, a golden CSV/schema
pair, partition-count checks, and a CI run that does not require the public network.

## Related pages

- [Architecture](architecture.md)
- [Deterministic exports](deterministic-exports.md)
- [Data limitations](data-limitations.md)
- [Environment](../reference/environment.md)
