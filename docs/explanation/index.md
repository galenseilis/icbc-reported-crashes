# Explanation

Explanation pages are understanding-oriented. They discuss context, design
decisions, tradeoffs, and limitations. They do not give step-by-step instructions
and do not replace the exact facts in the [reference](../reference/index.md).

## Pages

| Page | Question it answers |
|---|---|
| [Architecture](architecture.md) | What are the stages, and how does data flow through them? |
| [Data provenance](data-provenance.md) | Where did this data come from, and how current is it? |
| [Data limitations](data-limitations.md) | What can and cannot be concluded from the data? |
| [Deterministic exports](deterministic-exports.md) | Why are the CSV and partitions ordered and formatted this way? |
| [Tableau workbook anatomy](tableau-workbook-anatomy.md) | Why is the `.twb` a ZIP, and what do the embedded files contain? |
| [Design decisions](design-decisions.md) | Why scripts, CSV, a partition tree, and full refreshes? |

## How to use these pages

Read [Data provenance](data-provenance.md) and
[Data limitations](data-limitations.md) before publishing an analysis. The other
pages are useful when you need to change the pipeline, debug an unexpected result,
or explain the project to someone else.

For official ICBC wording, see
[Caveats and licence](../reference/caveats-and-licence.md). This section explains
the consequences; it does not replace the source's own statements.
