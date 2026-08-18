from __future__ import annotations

from pathlib import Path
from typing import Iterable

from tableauhyperapi import HyperProcess, Connection, Telemetry


ROOT = Path(__file__).resolve().parents[2]

HYPER_PATH = (
    ROOT
    / "data"
    / "raw"
    / "tableau"
    / "extracted"
    / "2021-2025 public data set.hyper"
)

SCHEMA = "Extract"
TABLE = "Extract"

# Exact column names from the Hyper extract.
COLUMNS = [
    "MID_BLOCK_CRASH",
    "DERIVED_CRASH_CONFIGURATION",
    "CYCLIST_FLAG",
    "DATE_OF_LOSS_YEAR",
    "DAY_OF_WEEK",
    "HEAVY_VEH_FLAG",
    "CRASH_SEVERITY",
    "TIME_CATEGORY",
    "INTERSECTION_CRASH",
    "LATITUDE",
    "LONGITUDE",
    "MONTH_OF_YEAR",
    "MOTORCYCLE_FLAG",
    "PEDESTRIAN_FLAG",
    "ANIMAL_FLAG",
    "MUNICIPALITY_WITH_BOUNDARY",
    "MUNICIPALITY_NAME",
    "CROSS_STREET_FULL_NAME",
    "PARKED_VEHICLE_FLAG",
    "PARKING_LOT_FLAG",
    "REGION",
    "STREET_FULL_NAME",
    "ROAD_LOCATION_DESCRIPTION",
    "TOTAL_VICTIMS",
    "TOTAL_CRASHES",
]


def quote_identifier(identifier: str) -> str:
    """
    Quote a SQL identifier for Hyper.

    Tableau Hyper identifiers are case-sensitive, so identifiers such as
    MID_BLOCK_CRASH must be quoted exactly as they appear in the extract.
    """
    return '"' + identifier.replace('"', '""') + '"'


def table_sql() -> str:
    """Return the fully-qualified table name."""
    return (
        f"{quote_identifier(SCHEMA)}."
        f"{quote_identifier(TABLE)}"
    )


def column_sql(column: str) -> str:
    """Return a correctly quoted column identifier."""
    return quote_identifier(column)


def run_query(
    connection: Connection,
    sql: str,
) -> list[list]:
    """Execute a query and return rows as ordinary Python lists."""
    return [list(row) for row in connection.execute_list_query(sql)]


def scalar(
    connection: Connection,
    sql: str,
):
    """Execute a scalar query."""
    return connection.execute_scalar_query(sql)


def print_section(title: str) -> None:
    print()
    print(f"=== {title} ===")


def print_distribution(
    connection: Connection,
    column: str,
    limit: int | None = None,
) -> None:
    """
    Print a frequency distribution for a column.
    """
    col = column_sql(column)

    sql = f"""
        SELECT
            {col},
            COUNT(*) AS row_count
        FROM {table_sql()}
        GROUP BY {col}
        ORDER BY
            row_count DESC,
            {col}
    """

    if limit is not None:
        sql += f"\nLIMIT {limit}"

    rows = run_query(connection, sql)

    for value, count in rows:
        print(f"{str(value):40} {count:>12,}")


def print_null_counts(connection: Connection) -> None:
    """
    Print NULL counts for every column.
    """
    for column in COLUMNS:
        col = column_sql(column)

        sql = f"""
            SELECT COUNT(*)
            FROM {table_sql()}
            WHERE {col} IS NULL
        """

        count = scalar(connection, sql)

        print(f"{column:40} {int(count):>12,}")


def print_distinct_counts(connection: Connection) -> None:
    """
    Print number of distinct non-null values for every column.
    """
    for column in COLUMNS:
        col = column_sql(column)

        sql = f"""
            SELECT COUNT(DISTINCT {col})
            FROM {table_sql()}
        """

        count = scalar(connection, sql)

        print(f"{column:40} {int(count):>12,}")


def print_year_distribution(connection: Connection) -> None:
    """
    Print rows, crashes, and victims by year.
    """
    year = column_sql("DATE_OF_LOSS_YEAR")
    crashes = column_sql("TOTAL_CRASHES")
    victims = column_sql("TOTAL_VICTIMS")

    sql = f"""
        SELECT
            {year},
            COUNT(*) AS rows,
            SUM({crashes}) AS crashes,
            SUM({victims}) AS victims
        FROM {table_sql()}
        GROUP BY {year}
        ORDER BY {year}
    """

    rows = run_query(connection, sql)

    for year_value, row_count, crash_count, victim_count in rows:
        print(
            f"Year {year_value}: "
            f"rows={int(row_count):,}, "
            f"crashes={int(crash_count):,}, "
            f"victims={int(victim_count):,}"
        )


def print_numeric_distribution(
    connection: Connection,
    column: str,
) -> None:
    """
    Print a frequency distribution for an integer/numeric column.
    """
    col = column_sql(column)

    sql = f"""
        SELECT
            {col},
            COUNT(*) AS row_count
        FROM {table_sql()}
        GROUP BY {col}
        ORDER BY {col}
    """

    rows = run_query(connection, sql)

    for value, count in rows:
        print(f"{str(value):>4} {int(count):>12,}")


def print_geographic_extent(connection: Connection) -> None:
    """
    Print latitude/longitude bounds and non-null counts.
    """
    lat = column_sql("LATITUDE")
    lon = column_sql("LONGITUDE")

    sql = f"""
        SELECT
            MIN({lat}),
            MAX({lat}),
            MIN({lon}),
            MAX({lon}),
            COUNT({lat}),
            COUNT({lon})
        FROM {table_sql()}
    """

    (
        min_lat,
        max_lat,
        min_lon,
        max_lon,
        lat_count,
        lon_count,
    ) = run_query(connection, sql)[0]

    print(f"Latitude:  {min_lat} to {max_lat}")
    print(f"Longitude: {min_lon} to {max_lon}")
    print(f"Latitude non-null:  {int(lat_count):,}")
    print(f"Longitude non-null: {int(lon_count):,}")


def print_duplicate_check(connection: Connection) -> None:
    """
    Check for completely duplicated rows.

    The extract has no obvious row ID, so this compares all 25 columns.
    """
    column_list = ",\n            ".join(
        column_sql(column) for column in COLUMNS
    )

    sql = f"""
        SELECT
            COUNT(*) AS duplicate_groups,
            COALESCE(
                SUM(group_count - 1),
                0
            ) AS rows_beyond_first
        FROM (
            SELECT
                COUNT(*) AS group_count
            FROM {table_sql()}
            GROUP BY
                {column_list}
            HAVING COUNT(*) > 1
        ) AS duplicate_groups
    """

    duplicate_groups, rows_beyond_first = run_query(connection, sql)[0]

    print(f"Duplicate value groups:       {int(duplicate_groups):,}")
    print(f"Rows beyond first in groups:  {int(rows_beyond_first):,}")


def print_values(
    connection: Connection,
    column: str,
    max_values: int = 100,
) -> None:
    """
    Print the most common values for a categorical column.

    NULL is included explicitly.
    """
    col = column_sql(column)

    sql = f"""
        SELECT
            {col},
            COUNT(*) AS row_count
        FROM {table_sql()}
        GROUP BY {col}
        ORDER BY
            row_count DESC,
            {col}
        LIMIT {max_values}
    """

    rows = run_query(connection, sql)

    for value, count in rows:
        print(f"{str(value):50} {int(count):>12,}")


def print_basic_counts(connection: Connection) -> None:
    """
    Print overall row, crash, and victim counts.
    """
    crashes = column_sql("TOTAL_CRASHES")
    victims = column_sql("TOTAL_VICTIMS")

    sql = f"""
        SELECT
            COUNT(*) AS rows,
            SUM({crashes}) AS total_crashes,
            SUM({victims}) AS total_victims
        FROM {table_sql()}
    """

    row_count, crash_count, victim_count = run_query(connection, sql)[0]

    print(f"Rows:          {int(row_count):,}")
    print(f"Total crashes: {int(crash_count):,}")
    print(f"Total victims: {int(victim_count):,}")


def print_sample_rows(
    connection: Connection,
    limit: int = 10,
) -> None:
    """
    Print a small sample using the extract's natural column order.
    """
    column_list = ", ".join(
        column_sql(column) for column in COLUMNS
    )

    sql = f"""
        SELECT {column_list}
        FROM {table_sql()}
        LIMIT {limit}
    """

    rows = run_query(connection, sql)

    for index, row in enumerate(rows, start=1):
        print()
        print(f"--- Row {index} ---")

        for column, value in zip(COLUMNS, row):
            print(f"{column!r}: {value!r}")


def main() -> None:
    if not HYPER_PATH.exists():
        raise FileNotFoundError(
            f"Hyper extract not found:\n{HYPER_PATH}"
        )

    print(f"Opening: {HYPER_PATH}")

    with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=str(HYPER_PATH),
        ) as connection:

            print_section("BASIC COUNTS")
            print_basic_counts(connection)

            print_section("YEAR DISTRIBUTION")
            print_year_distribution(connection)

            print_section("TOTAL_CRASHES DISTRIBUTION")
            print_numeric_distribution(
                connection,
                "TOTAL_CRASHES",
            )

            print_section("TOTAL_VICTIMS DISTRIBUTION")
            print_numeric_distribution(
                connection,
                "TOTAL_VICTIMS",
            )

            print_section("GEOGRAPHIC EXTENT")
            print_geographic_extent(connection)

            print_section("NULL COUNTS")
            print_null_counts(connection)

            print_section("DISTINCT COUNTS")
            print_distinct_counts(connection)

            print_section("DUPLICATE ROW CHECK")
            print_duplicate_check(connection)

            print_section("VALUES: MID_BLOCK_CRASH")
            print_values(
                connection,
                "MID_BLOCK_CRASH",
            )

            print_section("VALUES: DERIVED_CRASH_CONFIGURATION")
            print_values(
                connection,
                "DERIVED_CRASH_CONFIGURATION",
            )

            print_section("VALUES: CRASH_SEVERITY")
            print_values(
                connection,
                "CRASH_SEVERITY",
            )

            print_section("VALUES: REGION")
            print_values(
                connection,
                "REGION",
            )

            print_section("VALUES: DAY_OF_WEEK")
            print_values(
                connection,
                "DAY_OF_WEEK",
            )

            print_section("VALUES: TIME_CATEGORY")
            print_values(
                connection,
                "TIME_CATEGORY",
            )

            print_section("VALUES: ROAD_LOCATION_DESCRIPTION")
            print_values(
                connection,
                "ROAD_LOCATION_DESCRIPTION",
                max_values=50,
            )

            print_section("SAMPLE ROWS")
            print_sample_rows(connection, limit=10)


if __name__ == "__main__":
    main()
