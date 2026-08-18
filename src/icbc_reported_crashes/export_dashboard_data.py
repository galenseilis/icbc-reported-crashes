from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

from tableauhyperapi import (
    Connection,
    HyperProcess,
    TableName,
    Telemetry,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

HYPER_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "tableau"
    / "extracted"
    / "2021-2025 public data set.hyper"
)

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

CSV_PATH = OUTPUT_DIR / "icbc_reported_crashes.csv"
SCHEMA_PATH = OUTPUT_DIR / "icbc_reported_crashes.schema.json"


# ---------------------------------------------------------------------------
# Expected physical source columns
# ---------------------------------------------------------------------------

EXPECTED_COLUMNS = {
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
}


# ---------------------------------------------------------------------------
# Tableau calculated fields
# ---------------------------------------------------------------------------

CALCULATED_FIELDS = {
    "Municipality Name (ifnull)": {
        "formula": 'IFNULL("MUNICIPALITY_NAME", \'Unknown\')',
        "description": (
            "Municipality name with NULL values replaced by "
            "'Unknown'."
        ),
    },
    "Street Full Name (ifnull)": {
        "formula": 'IFNULL("STREET_FULL_NAME", \'Unknown\')',
        "description": (
            "Street name with NULL values replaced by "
            "'Unknown'."
        ),
    },
    "Metric Selector": {
        "formula": (
            'SUM("TOTAL_CRASHES") when Metric Selector = "Crash Count"; '
            'SUM("TOTAL_VICTIMS") when Metric Selector = "Victim Count"'
        ),
        "description": "Tableau parameter-controlled metric.",
    },
    "Crash Breakdown 2": {
        "formula": (
            'Crash Severity -> "CRASH_SEVERITY"; '
            'Crash Configuration -> "DERIVED_CRASH_CONFIGURATION"; '
            'Region -> "REGION"; '
            'Municipality -> Municipality Name (ifnull); '
            'Street Name -> Street Full Name (ifnull); '
            'Road Location Description -> "ROAD_LOCATION_DESCRIPTION"'
        ),
        "description": "Tableau parameter-controlled breakdown dimension.",
    },
}


PARAMETERS = {
    "Crash Breakdown 2": [
        "Crash Severity",
        "Crash Configuration",
        "Region",
        "Municipality",
        "Street Name",
        "Road Location Description",
    ],
    "Metric Selector": [
        "Crash Count",
        "Victim Count",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def display_name(value: Any) -> str:
    """Return a clean string representation for Hyper API names."""
    if value is None:
        return ""

    # Hyper Name objects have an `unescaped` property.
    unescaped = getattr(value, "unescaped", None)
    if unescaped is not None:
        return str(unescaped)

    return str(value).strip('"')


def quote_identifier(name: str) -> str:
    """Quote a SQL identifier safely for Hyper."""
    return '"' + name.replace('"', '""') + '"'


def table_sql(table: TableName) -> str:
    """
    Return the table's already-qualified SQL representation.

    `str(TableName(...))` produces properly escaped SQL such as:
        "Extract"."Extract"
    """
    return str(table)


def run_query(connection: Connection, sql: str) -> list[list[Any]]:
    return connection.execute_list_query(sql)


# ---------------------------------------------------------------------------
# Hyper catalog discovery
# ---------------------------------------------------------------------------


def discover_source_table(
    connection: Connection,
) -> tuple[TableName, Any]:
    """
    Find the Hyper table containing the ICBC crash dataset.

    Hyper's Python Catalog API is hierarchical:

        get_schema_names()
            -> get_table_names(schema)
                -> get_table_definition(table)

    There is no get_database_names() method in the Python Catalog API.
    """

    candidates: list[tuple[TableName, Any]] = []

    schemas = sorted(
        connection.catalog.get_schema_names(),
        key=lambda schema: str(schema),
    )

    print("=== HYPER CATALOG ===")

    for schema in schemas:
        print(f"Schema: {schema}")

        try:
            tables = connection.catalog.get_table_names(schema)
        except Exception as exc:
            print(f"  Could not enumerate tables: {exc}")
            continue

        for table in sorted(tables, key=lambda table: str(table)):
            definition = connection.catalog.get_table_definition(table)
            candidates.append((table, definition))

            column_names = {
                display_name(column.name)
                for column in definition.columns
            }

            print(
                f"  {table}: "
                f"{len(definition.columns)} columns"
            )

    print()

    exact_matches: list[tuple[TableName, Any]] = []

    for table, definition in candidates:
        column_names = {
            display_name(column.name)
            for column in definition.columns
        }

        if EXPECTED_COLUMNS.issubset(column_names):
            exact_matches.append((table, definition))

    if len(exact_matches) == 1:
        table, definition = exact_matches[0]
        print(f"Source table: {table}")
        print()
        return table, definition

    if len(exact_matches) > 1:
        print("Multiple tables contain the expected ICBC columns:")
        for table, _definition in exact_matches:
            print(f"  {table}")

        raise RuntimeError(
            "More than one possible ICBC crash source table was found."
        )

    print("Discovered tables:")
    for table, definition in candidates:
        print(
            f"  {table} "
            f"({len(definition.columns)} columns)"
        )

    missing_details = []

    for table, definition in candidates:
        names = {
            display_name(column.name)
            for column in definition.columns
        }
        missing = sorted(EXPECTED_COLUMNS - names)

        if len(definition.columns) == len(EXPECTED_COLUMNS):
            missing_details.append(
                f"  {table}: missing {len(missing)} expected columns"
            )

    if missing_details:
        print()
        print("Potential candidates:")
        print("\n".join(missing_details))

    raise RuntimeError(
        "Could not find the ICBC crash source table.\n\n"
        "Expected all of these physical columns:\n"
        + "\n".join(f"  {name}" for name in sorted(EXPECTED_COLUMNS))
    )


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def get_source_schema(
    definition: Any,
) -> list[dict[str, Any]]:
    """
    Convert a Hyper TableDefinition into JSON-friendly metadata.

    Hyper API uses Column.nullability rather than Column.nullable.
    """

    columns: list[dict[str, Any]] = []

    for column in definition.columns:
        columns.append(
            {
                "name": display_name(column.name),
                "type": str(column.type),
                "nullability": str(column.nullability),
            }
        )

    return columns


def write_schema(
    path: Path,
    source_table: TableName,
    definition: Any,
    row_count: int,
) -> None:
    source_columns = get_source_schema(definition)

    payload = {
        "source": {
            "file": str(HYPER_PATH.relative_to(PROJECT_ROOT)),
            "table": str(source_table),
            "row_count": row_count,
        },
        "physical_columns": source_columns,
        "calculated_fields": CALCULATED_FIELDS,
        "parameters": PARAMETERS,
        "export": {
            "format": "CSV",
            "null_value": r"\N",
            "column_order": "alphabetical",
            "row_order": (
                "DATE_OF_LOSS_YEAR ascending, followed by all "
                "remaining exported columns ascending"
            ),
        },
    }

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            payload,
            handle,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        handle.write("\n")


# ---------------------------------------------------------------------------
# Source summary
# ---------------------------------------------------------------------------


def get_row_count(
    connection: Connection,
    table: TableName,
) -> int:
    sql = f"""
        SELECT COUNT(*)
        FROM {table_sql(table)}
    """

    value = connection.execute_scalar_query(sql)
    return int(value)


def get_column_names(definition: Any) -> list[str]:
    return [
        display_name(column.name)
        for column in definition.columns
    ]


def print_source_summary(
    connection: Connection,
    table: TableName,
    definition: Any,
) -> int:
    row_count = get_row_count(connection, table)

    columns = get_column_names(definition)

    print("=== SOURCE ===")
    print(f"Table: {table}")
    print(f"Rows:  {row_count:,}")
    print(f"Columns: {len(columns)}")
    print()

    print("=== PHYSICAL COLUMNS ===")
    for index, name in enumerate(columns):
        print(f"{index:2d}  {name}")

    print()

    return row_count


# ---------------------------------------------------------------------------
# Deterministic CSV export
# ---------------------------------------------------------------------------


def month_sort_expression(column: str) -> str:
    """
    Convert the month names used by the ICBC dataset into a numeric
    chronological order.

    This is useful because the source contains MONTH_OF_YEAR as text.
    """

    month = quote_identifier(column)

    return f"""
        CASE {month}
            WHEN 'JANUARY' THEN 1
            WHEN 'FEBRUARY' THEN 2
            WHEN 'MARCH' THEN 3
            WHEN 'APRIL' THEN 4
            WHEN 'MAY' THEN 5
            WHEN 'JUNE' THEN 6
            WHEN 'JULY' THEN 7
            WHEN 'AUGUST' THEN 8
            WHEN 'SEPTEMBER' THEN 9
            WHEN 'OCTOBER' THEN 10
            WHEN 'NOVEMBER' THEN 11
            WHEN 'DECEMBER' THEN 12
            ELSE 99
        END
    """


def build_export_columns(
    definition: Any,
) -> list[str]:
    """
    Export the physical source columns plus Tableau's calculated fields.

    Columns are sorted alphabetically to make the CSV schema stable.
    """

    physical = {
        display_name(column.name)
        for column in definition.columns
    }

    exported = set(physical)

    exported.update(CALCULATED_FIELDS.keys())

    return sorted(exported, key=str.casefold)


def sql_expression_for_export_column(
    column_name: str,
) -> str:
    """
    Turn an exported column name into its SELECT expression.
    """

    if column_name == "Municipality Name (ifnull)":
        return (
            'COALESCE("MUNICIPALITY_NAME", \'Unknown\') '
            f"AS {quote_identifier(column_name)}"
        )

    if column_name == "Street Full Name (ifnull)":
        return (
            'COALESCE("STREET_FULL_NAME", \'Unknown\') '
            f"AS {quote_identifier(column_name)}"
        )

    # The two Tableau parameter-dependent fields cannot be represented
    # by one fixed row-level value. They are therefore documented in the
    # schema, but are not exported as fabricated values here.
    #
    # We explicitly handle this below rather than silently pretending
    # they are physical columns.
    if column_name == "Metric Selector":
        raise ValueError(
            "Metric Selector is a Tableau aggregate calculated field "
            "and is not a row-level source column."
        )

    if column_name == "Crash Breakdown 2":
        raise ValueError(
            "Crash Breakdown 2 is a Tableau parameter-dependent field "
            "and is not a single row-level source column."
        )

    return quote_identifier(column_name)


def build_physical_export_columns(
    definition: Any,
) -> list[str]:
    """
    Return the physical columns plus the two row-level Tableau
    IFNULL calculated fields.

    Aggregate/parameter-dependent Tableau fields are represented in
    the schema rather than materialized into every row.
    """

    physical = {
        display_name(column.name)
        for column in definition.columns
    }

    physical.update(
        {
            "Municipality Name (ifnull)",
            "Street Full Name (ifnull)",
        }
    )

    return sorted(physical, key=str.casefold)


def export_csv(
    connection: Connection,
    table: TableName,
    definition: Any,
    output_path: Path,
) -> int:
    """
    Export deterministic CSV.

    Ordering strategy:

      1. DATE_OF_LOSS_YEAR ascending
      2. MONTH_OF_YEAR chronologically
      3. every other physical/exported column ascending

    The first key is deliberate: when the source gains a new year,
    the new rows naturally appear at the end of the file instead of
    causing the entire CSV to be rearranged.

    Within each year the rows are completely deterministic.
    """

    columns = build_physical_export_columns(definition)

    select_expressions = [
        sql_expression_for_export_column(name)
        for name in columns
    ]

    # DATE_OF_LOSS_YEAR and MONTH_OF_YEAR are always present in the
    # expected ICBC physical schema.
    other_sort_columns = [
        name
        for name in columns
        if name not in {
            "DATE_OF_LOSS_YEAR",
            "MONTH_OF_YEAR",
        }
    ]

    order_by: list[str] = [
        quote_identifier("DATE_OF_LOSS_YEAR") + " ASC",
        month_sort_expression("MONTH_OF_YEAR") + " ASC",
        quote_identifier("MONTH_OF_YEAR") + " ASC",
    ]

    for name in other_sort_columns:
        order_by.append(
            quote_identifier(name) + " ASC NULLS FIRST"
        )

    sql = f"""
        SELECT
            {", ".join(select_expressions)}
        FROM {table_sql(table)}
        ORDER BY
            {", ".join(order_by)}
    """

    print("=== EXPORT ===")
    print(f"Columns: {len(columns)}")
    print(f"Output:  {output_path}")
    print()
    print("Column order:")

    for index, column in enumerate(columns):
        print(f"{index:2d}  {column}")

    print()
    print("Ordering:")
    print("  1. DATE_OF_LOSS_YEAR ASC")
    print("  2. MONTH_OF_YEAR chronological ASC")
    print("  3. remaining columns ASC")
    print()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    row_count = 0

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.writer(
            handle,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\n",
        )

        writer.writerow(columns)

        with connection.execute_query(sql) as result:
            for row in result:
                output_row = []

                for value in row:
                    if value is None:
                        output_row.append(r"\N")
                    else:
                        output_row.append(str(value))

                writer.writerow(output_row)

                row_count += 1

                if row_count % 100_000 == 0:
                    print(
                        f"  exported {row_count:,} rows...",
                        flush=True,
                    )

    print(f"Exported rows: {row_count:,}")
    print()

    return row_count


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_export(
    output_path: Path,
    expected_rows: int,
) -> None:
    """
    Basic post-export validation without loading the CSV into memory.
    """

    print("=== VALIDATION ===")

    with output_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.reader(handle)

        header = next(reader)

        rows = 0

        for _row in reader:
            rows += 1

    print(f"CSV columns: {len(header)}")
    print(f"CSV rows:    {rows:,}")
    print(f"Hyper rows:  {expected_rows:,}")

    if rows != expected_rows:
        raise RuntimeError(
            f"Export row count mismatch: CSV has {rows:,}, "
            f"Hyper has {expected_rows:,}."
        )

    if header != sorted(header, key=str.casefold):
        raise RuntimeError(
            "CSV columns are not in deterministic alphabetical order."
        )

    print("Validation: OK")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    if not HYPER_PATH.exists():
        print(
            f"ERROR: Hyper file does not exist:\n{HYPER_PATH}",
            file=sys.stderr,
        )
        return 1

    print(f"Opening: {HYPER_PATH}")
    print()

    with HyperProcess(
        telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU,
    ) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=HYPER_PATH,
        ) as connection:

            # --------------------------------------------------------------
            # Discover the actual table through the Hyper catalog.
            # --------------------------------------------------------------

            source_table, definition = discover_source_table(
                connection
            )

            # --------------------------------------------------------------
            # Validate physical columns.
            # --------------------------------------------------------------

            actual_columns = {
                display_name(column.name)
                for column in definition.columns
            }

            missing = EXPECTED_COLUMNS - actual_columns

            if missing:
                raise RuntimeError(
                    "Expected physical columns are missing:\n"
                    + "\n".join(
                        f"  {name}"
                        for name in sorted(missing)
                    )
                )

            extra = actual_columns - EXPECTED_COLUMNS

            if extra:
                print("WARNING: Source contains extra physical columns:")
                for name in sorted(extra):
                    print(f"  {name}")
                print()

            # --------------------------------------------------------------
            # Source summary.
            # --------------------------------------------------------------

            row_count = print_source_summary(
                connection,
                source_table,
                definition,
            )

            # --------------------------------------------------------------
            # Export.
            # --------------------------------------------------------------

            exported_rows = export_csv(
                connection,
                source_table,
                definition,
                CSV_PATH,
            )

            if exported_rows != row_count:
                raise RuntimeError(
                    f"Expected to export {row_count:,} rows but "
                    f"exported {exported_rows:,}."
                )

            # --------------------------------------------------------------
            # Schema metadata.
            # --------------------------------------------------------------

            write_schema(
                SCHEMA_PATH,
                source_table,
                definition,
                row_count,
            )

            # --------------------------------------------------------------
            # Validate generated CSV.
            # --------------------------------------------------------------

            validate_export(
                CSV_PATH,
                row_count,
            )

    print("=== COMPLETE ===")
    print(f"CSV:    {CSV_PATH}")
    print(f"Schema: {SCHEMA_PATH}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
