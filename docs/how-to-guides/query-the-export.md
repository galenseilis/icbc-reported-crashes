# Query the export

Use this guide when you want to analyze the data in Python without loading the
full 300 MB CSV into memory, or when you want to read only one slice of the
partitioned records.

The examples use pandas, which is already a project dependency. Run them from the
repository root with `uv run python`.

## Read only the columns you need

```python
import pandas as pd

columns = ["REGION", "TOTAL_CRASHES", "TOTAL_VICTIMS"]

df = pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=columns,
    keep_default_na=False,
    na_values=[r"\N"],
)

totals = df.groupby("REGION")[["TOTAL_CRASHES", "TOTAL_VICTIMS"]].sum()
print(totals.sort_values("TOTAL_CRASHES", ascending=False))
```

`usecols` reduces memory use, but pandas still scans the file. The two null
arguments matter:

- `na_values=[r"\N"]` converts the CSV's literal `\N` marker to a missing value.
- `keep_default_na=False` stops pandas from treating ordinary codes such as `N`
  or `Y` as missing values by accident.

## Filter to one region or municipality

```python
import pandas as pd

df = pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=[
        "REGION",
        "MUNICIPALITY_NAME",
        "TOTAL_CRASHES",
        "TOTAL_VICTIMS",
    ],
    keep_default_na=False,
    na_values=[r"\N"],
)

lower_mainland = df[df["REGION"] == "LOWER MAINLAND"]
print(lower_mainland[["TOTAL_CRASHES", "TOTAL_VICTIMS"]].sum())

vancouver = df[df["MUNICIPALITY_NAME"] == "VANCOUVER"]
print(len(vancouver), int(vancouver["TOTAL_CRASHES"].sum()))
```

Remember that `len()` is a count of records, not crashes. Use
`TOTAL_CRASHES.sum()` for crashes.

## Read one partition file

Every partition has the same 27-column schema as the full CSV, so it can be read
directly:

```python
import pandas as pd

path = "data/processed/records/2021/01_JANUARY/1_MONDAY/0900_1159.csv"

df = pd.read_csv(
    path,
    keep_default_na=False,
    na_values=[r"\N"],
)

print(df[["TOTAL_CRASHES", "TOTAL_VICTIMS"]].sum())
```

This is the cheapest way to work with a specific year, month, weekday, and time
bucket. See [Records layout](../reference/records-layout.md) for the path rules.

## Read one month from partitions

```python
from pathlib import Path

import pandas as pd

files = sorted(Path("data/processed/records/2025/07_JULY").rglob("*.csv"))

frames = [
    pd.read_csv(path, keep_default_na=False, na_values=[r"\N"])
    for path in files
]

df = pd.concat(frames, ignore_index=True)
print(f"{len(files)} files, {len(df):,} records")
print(df[["TOTAL_CRASHES", "TOTAL_VICTIMS"]].sum())
```

Reading a whole month means opening 56 files. Reading a whole year means 672
files. For whole-year or multi-year aggregations, the full CSV is usually faster
than concatenating thousands of partitions; use partitions when you want a
specific slice or want to stream smaller files.

## Process the full file in chunks

If a filter must scan every row but you do not want the whole table in memory,
process fixed-size chunks and accumulate:

```python
import pandas as pd

crashes = 0
victims = 0

for chunk in pd.read_csv(
    "data/processed/icbc_reported_crashes.csv",
    usecols=["TOTAL_CRASHES", "TOTAL_VICTIMS"],
    keep_default_na=False,
    na_values=[r"\N"],
    chunksize=250_000,
):
    crashes += int(chunk["TOTAL_CRASHES"].sum())
    victims += int(chunk["TOTAL_VICTIMS"].sum())

print(f"crashes={crashes:,} victims={victims:,}")
```

## Common mistakes

| Mistake | Effect | Fix |
|---|---|---|
| `COUNT(*)` or `len(df)` as the crash count | Counts records, not crashes | Sum `TOTAL_CRASHES`. |
| Leaving `\N` as a string | Arithmetic on a text column fails or silently does the wrong thing | Use `na_values=[r"\N"]`. |
| Using pandas' default NA handling blindly | Codes such as `N`/`Y` or names such as `NA` can be misread | Set `keep_default_na=False`. |
| Assuming one row is one crash | Understates crash totals | Read [Rows are not crashes](../explanation/data-limitations.md#rows-are-not-crashes). |
| Using `STREET_FULL_NAME` for intersection analysis | It is null for some records and does not identify the cross street | Use `CROSS_STREET_FULL_NAME` and account for its high null rate. |
| Reconstructing exact dates | Year, month, weekday, and time bucket are present, but day-of-month is not | Do not claim exact dates. |

## Related pages

- [Dataset schema](../reference/dataset-schema.md)
- [Records layout](../reference/records-layout.md)
- [Data limitations](../explanation/data-limitations.md)
- [Verify an export](verify-an-export.md)
