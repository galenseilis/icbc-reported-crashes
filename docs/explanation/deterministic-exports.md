# Deterministic exports

The export is designed so that the same source and code produce the same CSV, and
so that a small source change produces a small, reviewable diff rather than a
complete rewrite. This page explains the choices that make that possible and the
tradeoffs they introduce.

## The determinism checklist

| Property | Choice |
|---|---|
| Column order | Case-insensitive alphabetical |
| Row order | Year ascending, then month chronologically, then every remaining column ascending |
| Null representation | Literal `\N` |
| Encoding | UTF-8 |
| Line endings | `\n` |
| CSV quoting | Minimal, as needed |
| Index column | None |
| Timestamps in output | None |
| Schema key order | Alphabetical JSON keys |

For a fixed source, code version, and dependency set, rerunning the export should
produce no diff. The lockfile pins the Python dependencies; the artifacts contain no
run timestamp or random identifier.

This is a design goal, not a cross-version guarantee. A different Python, pandas,
or Hyper API version can change quoting, formatting, or query behavior.

## Why columns are alphabetical

Alphabetical order makes the schema independent of the source's physical column
order. If Tableau or the extract reorders columns, the CSV header stays the same.
It also makes generated schemas easy to compare and keeps downstream code from
depending on an incidental source order.

The cost is readability. The columns are not grouped by domain:

```text
ANIMAL_FLAG
CRASH_SEVERITY
CROSS_STREET_FULL_NAME
CYCLIST_FLAG
DATE_OF_LOSS_YEAR
...
Municipality Name (ifnull)
MUNICIPALITY_NAME
...
Street Full Name (ifnull)
STREET_FULL_NAME
```

The two derived fields sort by their mixed-case names, so they appear near related
source fields rather than at the end. Use the
[dataset schema](../reference/dataset-schema.md) when you need a domain grouping.

## Why rows are ordered this way

The export's `ORDER BY` is:

1. `DATE_OF_LOSS_YEAR` ascending;
2. `MONTH_OF_YEAR` in calendar order (January = 1, ..., December = 12);
3. `MONTH_OF_YEAR` text ascending as a tie-breaker;
4. every other exported column ascending, with nulls first.

The first key is deliberate. When the source gains a new year, the new rows appear
at the end of the file instead of causing the entire CSV to be rearranged. That
keeps year-over-year diffs localized.

The month key cannot use plain text order, because `APRIL` would come before
`JANUARY`. The export maps month names to numbers with a `CASE` expression, then
uses the text value as a tie-breaker.

The remaining columns are a deterministic tie-breaker. Without a total order, the
database could return rows in any order for records that share a year and month.

### The important tradeoff

All remaining exported columns participate in the sort. **Adding or removing an
exported column can change the order of rows within a month.** The year boundary is
stable, but intra-month order is not guaranteed across schema changes. New years
append; new columns can reshuffle.

If your workflow depends on row order, sort explicitly for your analysis rather
than relying on the file's order.

## Why nulls are `\N`

The export writes every null as the two-character sequence `\N`:

- it is visually distinct from the valid flag value `N`;
- it is distinct from `NA`, `N/A`, `NULL`, `None`, and an empty string;
- it is a common convention in database and analytical exports;
- it round-trips without ambiguity in CSV.

The cost is that readers must opt in. Pandas, for example, does not treat `\N` as
missing by default:

```python
pd.read_csv(path, keep_default_na=False, na_values=[r"\N"])
```

Without that configuration, a numeric column with a `\N` becomes an object column,
and arithmetic fails or behaves unexpectedly. See
[Nulls and missing values](../reference/dataset-schema.md#nulls-and-missing-values).

The sentinel also means null numeric columns become floating-point `NaN` in pandas,
even when the underlying Hyper type is an integer. Cast to a nullable integer type
if you need to preserve integer semantics.

## Why the schema is JSON

The CSV header tells you column names but not types, source table, nullability,
calculated fields, or parameter choices. The schema JSON records those facts next
to the data. It is written with `sort_keys=True`, indent 2, and a trailing newline,
so it is stable and diff-friendly.

The schema is generated from the Hyper table definition, not hand-maintained. That
reduces the chance that the documentation and the data disagree, though the
parameter and calculated-field formulas are summaries rather than exact Tableau
syntax.

## What validation does and does not cover

The export validates:

- the CSV row count matches the Hyper row count;
- the CSV header is in alphabetical order.

It does not validate:

- the total crashes or victims against a published figure;
- null rates;
- duplicate rows;
- partition coverage;
- the content of the schema against the CSV types.

Those checks are available separately in
[Verify an export](../how-to-guides/verify-an-export.md). Validation is a guard
against an interrupted export, not a full data-quality audit.

## Determinism in the partition tree

The splitter groups by four temporal columns with `sort=True` and writes one file
per group. For a fixed CSV and pandas version, the output paths and row contents
are stable. The path structure is deterministic by construction.

The splitter does not delete stale files, so a tree can be non-deterministic in a
different sense: it can contain files from an older run. Clear
`data/processed/records/` before a full rebuild if partition membership may have
changed.

## Tradeoffs in one table

| Choice | Benefit | Cost |
|---|---|---|
| Alphabetical columns | Stable schema, easy comparison | Less readable domain order |
| Year-first sort | New years append | Intra-month order changes when columns change |
| Full-column tie-break | Deterministic rows | More sorting work |
| `\N` nulls | Unambiguous | Readers must configure missing values |
| No timestamp in output | Byte-stable reruns | Provenance must be recorded separately |
| Full refresh | Simple and reproducible | Large diffs when source changes |
| Partition tree | Reviewable chunks | Thousands of files, stale-file risk |

## Related pages

- [Architecture](architecture.md)
- [Design decisions](design-decisions.md)
- [Dataset schema](../reference/dataset-schema.md)
- [Verify an export](../how-to-guides/verify-an-export.md)
