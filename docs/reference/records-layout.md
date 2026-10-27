# Records layout

The split stage writes one CSV per distinct combination of year, month, weekday,
and time category. The path itself is the index: there is no manifest or database.

## Path template

```text
data/processed/records/<year>/<MM_MONTH>/<D_WEEKDAY>/<HHMM_HHMM>.csv
```

Example:

```text
data/processed/records/2021/01_JANUARY/1_MONDAY/0900_1159.csv
```

This file contains records where:

- `DATE_OF_LOSS_YEAR` is `2021`;
- `MONTH_OF_YEAR` is `JANUARY`;
- `DAY_OF_WEEK` is `MONDAY`;
- `TIME_CATEGORY` is `09:00-11:59`.

## Path components

| Component | Source | Rule | Example |
|---|---|---|---|
| Year | `DATE_OF_LOSS_YEAR` | String form of the year | `2021` |
| Month | `MONTH_OF_YEAR` | Uppercase English name, numeric prefix with two digits | `01_JANUARY` |
| Weekday | `DAY_OF_WEEK` | Uppercase English name, numeric prefix with one digit; Monday = 1, Sunday = 7 | `1_MONDAY` |
| Time | `TIME_CATEGORY` | Remove `:`, replace `-` with `_`, append `.csv` | `0900_1159.csv` |

### Month mapping

| Value | Directory |
|---|---|
| `JANUARY` | `01_JANUARY` |
| `FEBRUARY` | `02_FEBRUARY` |
| `MARCH` | `03_MARCH` |
| `APRIL` | `04_APRIL` |
| `MAY` | `05_MAY` |
| `JUNE` | `06_JUNE` |
| `JULY` | `07_JULY` |
| `AUGUST` | `08_AUGUST` |
| `SEPTEMBER` | `09_SEPTEMBER` |
| `OCTOBER` | `10_OCTOBER` |
| `NOVEMBER` | `11_NOVEMBER` |
| `DECEMBER` | `12_DECEMBER` |

The script strips whitespace and uppercases the value before lookup. Any value not
in the mapping raises `ValueError: Unknown month`.

### Weekday mapping

| Value | Directory |
|---|---|
| `MONDAY` | `1_MONDAY` |
| `TUESDAY` | `2_TUESDAY` |
| `WEDNESDAY` | `3_WEDNESDAY` |
| `THURSDAY` | `4_THURSDAY` |
| `FRIDAY` | `5_FRIDAY` |
| `SATURDAY` | `6_SATURDAY` |
| `SUNDAY` | `7_SUNDAY` |

Any value not in the mapping raises `ValueError: Unknown weekday`.

### Time bucket mapping

| Value | File |
|---|---|
| `00:00-02:59` | `0000_0259.csv` |
| `03:00-05:59` | `0300_0559.csv` |
| `06:00-08:59` | `0600_0859.csv` |
| `09:00-11:59` | `0900_1159.csv` |
| `12:00-14:59` | `1200_1459.csv` |
| `15:00-17:59` | `1500_1759.csv` |
| `18:00-20:59` | `1800_2059.csv` |
| `21:00-23:59` | `2100_2359.csv` |

The transformation is generic: remove colons, replace hyphens with underscores,
append `.csv`. A new time category would produce a new filename automatically.

## File contents

Each partition is a normal CSV with:

- the same 27-column header as `data/processed/icbc_reported_crashes.csv`;
- one row per record in that temporal group;
- `index=False`, so there is no pandas index column;
- UTF-8 encoding;
- a newline at the end of each line on Linux.

Rows inside a file follow the order they had in the full CSV. The splitter does
not apply an additional sort within a group.

There is no row-count column, checksum, or manifest. To verify the tree, compare
the sum of data rows with the full CSV. See
[Verify an export](../how-to-guides/verify-an-export.md).

## Counts

For a complete year × month × weekday × time-bucket grid:

| Level | Files |
|---|---:|
| One time bucket within one weekday and month | 1 |
| One weekday within one month | 8 |
| One month | 56 |
| One year | 672 |
| Five years (2021–2025) | 3,360 |

The documented snapshot has all 3,360 files and 1,453,136 data rows across them.
Partition sizes vary with activity; there is no fixed number of rows per file.

A file count below the full grid is not automatically an error. The source may not
contain every combination, or a year may have been added or removed. A file count
above the grid indicates stale or unexpected files.

## Ordering and completeness

- **One record, one partition.** Every record maps to exactly one path because the
  four grouping columns are single-valued.
- **No calendar reconstruction.** A year, month, and weekday can correspond to
  several actual dates. The path does not identify a specific day.
- **Overwrite, not synchronize.** Rerunning the split overwrites generated files
  but does not delete old ones. Remove `data/processed/records/` before a full
  rebuild if partitions may have disappeared.
- **Tracked output.** The record files are tracked in git. The full CSV is not.

## Related pages

- [Dataset schema](dataset-schema.md)
- [Data layout](data-layout.md)
- [Rebuild only the partitioned records](../how-to-guides/rebuild-partitioned-records.md)
- [Pipeline script reference: split_records](pipeline-scripts.md#split_records)
