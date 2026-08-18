from __future__ import annotations

import json
from pathlib import Path

from tableauhyperapi import (
    Connection,
    HyperProcess,
    TableName,
    Telemetry,
)


ROOT = Path(__file__).resolve().parents[2]

HYPER_FILE = (
    ROOT
    / "data"
    / "raw"
    / "tableau"
    / "extracted"
    / "2021-2025 public data set.hyper"
)

METADATA_DIR = ROOT / "data" / "metadata"


def main() -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    with HyperProcess(
        telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU
    ) as hyper:
        with Connection(
            endpoint=hyper.endpoint,
            database=str(HYPER_FILE),
        ) as connection:

            # ---------------------------------------------------------
            # Schemas and tables
            # ---------------------------------------------------------

            print("=== SCHEMAS ===")

            schemas = connection.catalog.get_schema_names()

            for schema in schemas:
                print(f"\n{schema}")

                tables = connection.catalog.get_table_names(schema)

                if not tables:
                    print("  (no tables)")
                    continue

                for table in tables:
                    print(f"  {table}")

            # ---------------------------------------------------------
            # Main table
            # ---------------------------------------------------------

            table_name = TableName("Extract", "Extract")
            table_sql = '"Extract"."Extract"'

            # ---------------------------------------------------------
            # Row count
            # ---------------------------------------------------------

            print("\n=== ROW COUNT ===")

            row_count = connection.execute_scalar_query(
                f"SELECT COUNT(*) FROM {table_sql}"
            )

            print(f"{row_count:,}")

            # ---------------------------------------------------------
            # Table definition
            # ---------------------------------------------------------

            print("\n=== COLUMNS ===")

            definition = connection.catalog.get_table_definition(
                table_name
            )

            schema_metadata = []

            for ordinal, column in enumerate(definition.columns):
                info = {
                    "ordinal": ordinal,
                    "name": str(column.name),
                    "type": str(column.type),
                    "nullable": column.nullability.name,
                }

                schema_metadata.append(info)

                print(
                    f"{ordinal:>2}  "
                    f"{info['name']:<35} "
                    f"{info['type']:<15} "
                    f"{info['nullable']}"
                )

            # ---------------------------------------------------------
            # Save schema metadata
            # ---------------------------------------------------------

            output = METADATA_DIR / "hyper_schema.json"

            metadata = {
                "file": str(HYPER_FILE),
                "table": table_sql,
                "row_count": row_count,
                "columns": schema_metadata,
            }

            output.write_text(
                json.dumps(
                    metadata,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            print(f"\nSchema written to: {output}")

            # ---------------------------------------------------------
            # Sample rows
            # ---------------------------------------------------------

            print("\n=== SAMPLE ROWS ===")

            rows = connection.execute_list_query(
                f"""
                SELECT *
                FROM {table_sql}
                LIMIT 10
                """
            )

            for row_number, row in enumerate(rows, start=1):
                print(f"\n--- Row {row_number} ---")

                for column, value in zip(
                    definition.columns,
                    row,
                ):
                    print(f"{column.name}: {value}")


if __name__ == "__main__":
    main()
