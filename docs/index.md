# ICBC Reported Crashes documentation

This documentation covers the pipeline in the
[`icbc-reported-crashes`](https://github.com/galenseilis/icbc-reported-crashes)
repository: how to run it, how to use its outputs, what the files and fields
contain, and why the pipeline is designed the way it is.

It follows the [Diátaxis](https://diataxis.fr/) framework. Each page belongs to
one of four modes, so you can choose the page that matches what you need rather
than reading everything in order.

## The four modes

| | **Doing** | **Thinking** |
|---|---|---|
| **Learning** | [Tutorials](tutorials/index.md): guided lessons that build a working result | [Explanation](explanation/index.md): context, tradeoffs, and design rationale |
| **Working** | [How-to guides](how-to-guides/index.md): recipes for specific tasks | [Reference](reference/index.md): exact facts, paths, schemas, and commands |

## Start here

**I want to learn by doing.** Take the
[first-export tutorial](tutorials/first-export.md). It starts from a fresh clone
and ends with a query over the exported data.

**I need to refresh or rebuild something.** Go to the
[how-to guides](how-to-guides/index.md), especially
[Refresh from the public source](how-to-guides/refresh-from-source.md).

**I need the exact column names, file paths, or commands.** Use the
[reference](reference/index.md), especially the
[dataset schema](reference/dataset-schema.md) and
[pipeline script reference](reference/pipeline-scripts.md).

**I need to understand whether a conclusion is defensible.** Read
[Data limitations](explanation/data-limitations.md) and
[Data provenance](explanation/data-provenance.md).

## Common questions

| Question | Page |
|---|---|
| What does this project actually produce? | [Data layout](reference/data-layout.md) |
| What does one row represent? | [Dataset schema: grain](reference/dataset-schema.md#grain) |
| Why is `COUNT(*)` not a crash count? | [Data limitations](explanation/data-limitations.md#rows-are-not-crashes) |
| How do I read the `\N` nulls? | [Dataset schema: nulls](reference/dataset-schema.md#nulls-and-missing-values) |
| Where did the data come from? | [Data provenance](explanation/data-provenance.md) |
| Why are the CSV columns alphabetical? | [Deterministic exports](explanation/deterministic-exports.md) |
| Which files are in git? | [Data layout: tracked and ignored](reference/data-layout.md#tracked-and-ignored-files) |
| What are the official caveats? | [Caveats and licence](reference/caveats-and-licence.md) |
| Something failed. What now? | [Troubleshooting](how-to-guides/troubleshoot-pipeline.md) |

## Conventions used in these docs

- **Paths** are relative to the repository root unless stated otherwise.
- **Commands** use `uv run` so they execute inside the project environment. You
  can also run many of them through the `./run` wrapper.
- **Snapshot numbers** (row counts, distinct values, file sizes) describe the
  2021–2025 extract inspected while writing these docs. The live source can be
  revised, so treat exact counts as observations rather than guarantees.
- **"Record"** means one row of the exported dataset. A record is an aggregate,
  not necessarily one crash. See the [glossary](reference/glossary.md).

## Project status

This is a research-oriented pipeline, not a production data service. It has no
test suite, CI, database, scheduler, or incremental update mechanism. The code is
intentionally small and readable, and every stage can be rerun independently.
