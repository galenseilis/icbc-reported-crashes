# Build and explore your first export

In this tutorial you will take a fresh clone of the project, run the complete
data pipeline, confirm that the artifacts are present, and run your first
analysis over the exported data.

The pipeline downloads a public Tableau workbook, extracts the embedded Hyper
data, writes a CSV and schema metadata, and splits the CSV into 3,360 small
files. By the end you will know which file to open for which task and why a row
is not the same thing as a crash.

**Time:** about 10–20 minutes, depending on network and disk speed.

## What you will build

```text
data/
├── raw/tableau/
│   ├── ICBCReportedCrashes.twb
│   └── extracted/
│       ├── 2021-2025 public data set.hyper
│       └── ICBC Reported Crashes.twb
└── processed/
    ├── icbc_reported_crashes.csv
    ├── icbc_reported_crashes.schema.json
    └── records/
        └── 2021/01_JANUARY/1_MONDAY/0900_1159.csv
```

The exact row counts and file sizes depend on the current source snapshot. The
examples below use the 2021–2025 snapshot documented in this repository.

## Before you start

You need:

- [git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/)
- network access to `public.tableau.com`
- about 700 MB of free disk space

You do **not** need to install Python, pandas, or the Tableau Hyper API
separately. `uv` installs the project's Python environment from
`pyproject.toml` and `uv.lock`.

Check that the tools are available:

```bash
git --version
uv --version
```

If `uv` is missing, install it by following the
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Step 1: Get the project and install dependencies

Clone the repository and move into it:

```bash
git clone git@github.com:galenseilis/icbc-reported-crashes.git
cd icbc-reported-crashes
```

Create the project environment:

```bash
uv sync
```

`uv` reads `pyproject.toml`, resolves the locked dependencies, and prepares a
virtual environment. The project requires Python 3.14 or newer; `uv` can download
a suitable interpreter if your system does not already have one.

## Step 2: Run the pipeline

Run the four-stage wrapper:

```bash
./run
```

This is equivalent to running these four commands in order:

```bash
uv run src/icbc_reported_crashes/tableau.py
uv run src/icbc_reported_crashes/extract_tableau.py
uv run src/icbc_reported_crashes/export_dashboard_data.py
uv run src/icbc_reported_crashes/split_records.py
```

Each stage has a clear responsibility:

| Stage | What it does |
|---|---|
| `tableau.py` | Downloads the public workbook to `data/raw/tableau/ICBCReportedCrashes.twb`. |
| `extract_tableau.py` | Unpacks the workbook's `.hyper` and `.twb` entries into `data/raw/tableau/extracted/`. |
| `export_dashboard_data.py` | Reads the main Hyper table and writes the CSV plus schema metadata. |
| `split_records.py` | Splits the CSV into the `records/` directory tree. |

The export stage prints progress every 100,000 rows. At the end of a successful
run you should see a summary like this:

```text
Processing complete.
Input rows:  1,453,136
Output rows: 1,453,136
Files created: 3,360
Output root: /path/to/icbc-reported-crashes/data/processed/records
```

> The wrapper runs the stages in sequence but does not stop automatically if an
> earlier stage fails. If you see an error, check the output before relying on the
> final summary. See [Troubleshoot the pipeline](../how-to-guides/troubleshoot-pipeline.md)
> if a stage does not complete.

## Step 3: Check the main artifacts

List the processed directory:

```bash
ls -lh data/processed
```

You should see the full CSV, its schema, and the `records/` directory. The CSV is
about 300 MB in the documented snapshot.

Count the lines in the CSV:

```bash
wc -l data/processed/icbc_reported_crashes.csv
```

On the documented snapshot the count is `1,453,137`: one header row plus
1,453,136 data rows.

Look at the header and the first data row:

```bash
head -n 2 data/processed/icbc_reported_crashes.csv
```

The header has 27 columns. The first three begin `ANIMAL_FLAG`,
`CRASH_SEVERITY`, and `CROSS_STREET_FULL_NAME`. Columns are sorted
alphabetically so the schema is stable between runs.

## Step 4: Ask a question with pandas

Now load only the columns you need and calculate crashes and victims by year:

```bash
uv run python - <<'PY'
import pandas as pd

columns = [
    "DATE_OF_LOSS_YEAR",
    "CRASH_SEVERITY",
    "TOTAL_CRASHES",
    "TOTAL_VICTIMS",
]

df = pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=columns,
    keep_default_na=False,
    na_values=[r"\N"],
)

by_year = (
    df.groupby("DATE_OF_LOSS_YEAR")[["TOTAL_CRASHES", "TOTAL_VICTIMS"]]
    .sum()
)

print(by_year)
PY
```

You should see output in this shape:

```text
                   TOTAL_CRASHES  TOTAL_VICTIMS
DATE_OF_LOSS_YEAR
2021                      263442          72768
2022                      291779          70370
2023                      296488          67438
2024                      306286          68630
2025                      307440          68207
```

There are two important details in that code:

- `na_values=[r"\N"]` tells pandas to treat the CSV's literal `\N` marker as a
  missing value. `keep_default_na=False` prevents pandas from applying other
  default missing-value rules to codes such as `N` and `Y`.
- The totals use `sum()` on `TOTAL_CRASHES` and `TOTAL_VICTIMS`. Counting rows
  would answer a different question because one row can represent more than one
  crash.

Try one more grouping to see why the two measures behave differently:

```bash
uv run python - <<'PY'
import pandas as pd

df = pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=["CRASH_SEVERITY", "TOTAL_CRASHES", "TOTAL_VICTIMS"],
    keep_default_na=False,
    na_values=[r"\N"],
)

print(
    df.groupby("CRASH_SEVERITY")[["TOTAL_CRASHES", "TOTAL_VICTIMS"]]
    .sum()
)
PY
```

Property-damage-only crashes have zero victims in this dataset; casualty crashes
carry all of the recorded victims. That is a property of the source data, not a
bug in the pipeline.

## Step 5: Open one partition

The partitioned records are easier to browse than the full CSV. List a few files
for January 2021:

```bash
find data/processed/records/2021/01_JANUARY -name '*.csv' | head
```

Open the Monday morning file:

```bash
head -n 3 data/processed/records/2021/01_JANUARY/1_MONDAY/0900_1159.csv
```

Each partition has the same 27-column header as the full CSV. Its path encodes
the year, month, weekday, and three-hour time bucket:

```text
records/<year>/<MM_MONTH>/<D_WEEKDAY>/<HHMM_HHMM>.csv
```

So `2021/01_JANUARY/1_MONDAY/0900_1159.csv` contains January 2021 records for
Mondays between 09:00 and 11:59. The partition files are tracked in git, which is
why the full CSV does not need to be.

## Step 6: Read the schema metadata

The export also writes a machine-readable description of the columns and the
Tableau calculated fields:

```bash
uv run python -m json.tool \
  data/processed/icbc_reported_crashes.schema.json | head -n 40
```

You will see the source table, row count, physical column list, calculated field
definitions, parameter choices, and export conventions. This is the file to read
when you need to know how the CSV was produced without opening the workbook.

## What you learned

You have:

- built a complete local copy of the processed dataset;
- confirmed the row count and output layout;
- grouped crashes and victims by year and severity;
- located a single partition and read its path;
- found the machine-readable schema.

The most important idea is the **grain** of the data: a record is one distinct
combination of the non-measure dimensions, and `TOTAL_CRASHES` says how many
crashes that combination represents. This is why `SUM(TOTAL_CRASHES)` is the
correct crash count.

## Next steps

- Refresh or rebuild a single stage: [How-to guides](../how-to-guides/index.md)
- Look up a column or file: [Reference](../reference/index.md)
- Understand the source and its limits: [Data provenance](../explanation/data-provenance.md) and [Data limitations](../explanation/data-limitations.md)
- Read the official caveats before publishing: [Caveats and licence](../reference/caveats-and-licence.md)
