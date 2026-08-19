from pathlib import Path
import pandas as pd


# Paths are relative to the Python project root.
INPUT_PATH = Path("data/processed/icbc_reported_crashes.csv")
OUTPUT_ROOT = Path("data/processed/records")


# Monday = 1, Sunday = 7.
WEEKDAY_NUMBERS = {
    "MONDAY": 1,
    "TUESDAY": 2,
    "WEDNESDAY": 3,
    "THURSDAY": 4,
    "FRIDAY": 5,
    "SATURDAY": 6,
    "SUNDAY": 7,
}

MONTH_NUMBERS = {
    "JANUARY": 1,
    "FEBRUARY": 2,
    "MARCH": 3,
    "APRIL": 4,
    "MAY": 5,
    "JUNE": 6,
    "JULY": 7,
    "AUGUST": 8,
    "SEPTEMBER": 9,
    "OCTOBER": 10,
    "NOVEMBER": 11,
    "DECEMBER": 12,
}


def format_month(month: str) -> str:
    """Convert a month name to NN_MONTH_NAME."""
    month = str(month).strip().upper()

    if month not in MONTH_NUMBERS:
        raise ValueError(f"Unknown month: {month!r}")

    return f"{MONTH_NUMBERS[month]:02d}_{month}"


def format_weekday(day: str) -> str:
    """Convert a weekday name to N_WEEKDAY_NAME."""
    day = str(day).strip().upper()

    if day not in WEEKDAY_NUMBERS:
        raise ValueError(f"Unknown weekday: {day!r}")

    return f"{WEEKDAY_NUMBERS[day]}_{day}"


def format_time_category(time_category: str) -> str:
    """
    Convert TIME_CATEGORY to a filesystem-friendly filename.

    Example:
        15:00-17:59 -> 1500_1759.csv
    """
    time_category = str(time_category).strip()

    # Remove colons and replace dashes with underscores.
    return time_category.replace(":", "").replace("-", "_") + ".csv"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input CSV not found: {INPUT_PATH.resolve()}"
        )

    print(f"Reading: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_columns = {
        "DATE_OF_LOSS_YEAR",
        "MONTH_OF_YEAR",
        "DAY_OF_WEEK",
        "TIME_CATEGORY",
    }

    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # Group rows by the complete temporal hierarchy.
    groups = df.groupby(
        [
            "DATE_OF_LOSS_YEAR",
            "MONTH_OF_YEAR",
            "DAY_OF_WEEK",
            "TIME_CATEGORY",
        ],
        dropna=False,
        sort=True,
    )

    file_count = 0
    row_count = 0

    for (year, month, weekday, time_category), group in groups:
        month_dir = format_month(month)
        weekday_dir = format_weekday(weekday)
        filename = format_time_category(time_category)

        output_dir = (
            OUTPUT_ROOT
            / str(year)
            / month_dir
            / weekday_dir
        )

        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / filename

        group.to_csv(output_path, index=False)

        file_count += 1
        row_count += len(group)

        print(f"Created: {output_path} ({len(group):,} rows)")

    print()
    print("Processing complete.")
    print(f"Input rows:  {len(df):,}")
    print(f"Output rows: {row_count:,}")
    print(f"Files created: {file_count:,}")
    print(f"Output root: {OUTPUT_ROOT.resolve()}")


if __name__ == "__main__":
    main()
