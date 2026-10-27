# Reference

Reference pages are information-oriented. They describe the project's commands,
files, schemas, and official data caveats without teaching or recommending a
workflow. Use them when you need an exact name, path, type, or behavior.

## Pages

| Page | Contents |
|---|---|
| [Pipeline scripts](pipeline-scripts.md) | Every executable script, its inputs, outputs, side effects, and failure modes |
| [Data layout](data-layout.md) | Directory tree, artifact sizes, tracked versus ignored files |
| [Dataset schema](dataset-schema.md) | All 27 exported columns, types, null handling, grain, and value sets |
| [Records layout](records-layout.md) | Partition path template, naming rules, and file counts |
| [Metadata files](metadata-files.md) | The export schema, Hyper inspection metadata, and catalogue payload |
| [Caveats and licence](caveats-and-licence.md) | Official ICBC caveats and attribution requirements |
| [Environment](environment.md) | Python, uv, dependencies, paths, and network requirements |
| [Glossary](glossary.md) | Terms used across the documentation |

## What is authoritative?

The documentation describes the code as it exists in this repository and the
generated artifacts from the documented snapshot. When they disagree, use this
order:

1. the script that produces the artifact;
2. the generated `data/processed/icbc_reported_crashes.schema.json`;
3. this reference;
4. any example or tutorial.

Counts and distinct values are snapshot observations. They change when the source
is revised. The schema, path rules, and command behavior are stable unless the
code changes.
