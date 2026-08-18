from __future__ import annotations

import sys
from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[2]

WORKBOOK = (
    PROJECT_ROOT
    / "data/raw/tableau/extracted/ICBC Reported Crashes.twb"
)


def tag(element: ET.Element) -> str:
    """Return an XML tag without a namespace."""
    return element.tag.rsplit("}", 1)[-1]


def children(element: ET.Element, name: str):
    return [child for child in element if tag(child) == name]


def first_child(element: ET.Element, name: str):
    for child in element:
        if tag(child) == name:
            return child
    return None


def formula(element: ET.Element) -> str | None:
    calc = first_child(element, "calculation")
    if calc is None:
        return None
    return calc.attrib.get("formula")


def print_parameter(column: ET.Element) -> None:
    print()
    print(f"  Caption:          {column.attrib.get('caption')}")
    print(f"  Name:             {column.attrib.get('name')}")
    print(f"  Datatype:         {column.attrib.get('datatype')}")
    print(f"  Role:             {column.attrib.get('role')}")
    print(f"  Type:              {column.attrib.get('type')}")
    print(f"  Domain:            {column.attrib.get('param-domain-type')}")
    print(f"  Current value:     {column.attrib.get('value')}")

    f = formula(column)
    if f:
        print(f"  Formula:           {f}")

    members = first_child(column, "members")

    if members is not None:
        print("  Allowed values:")

        for member in members:
            if tag(member) != "member":
                continue

            print(
                f"    {member.attrib.get('value')}"
                + (
                    f"  alias={member.attrib.get('alias')}"
                    if member.attrib.get("alias")
                    else ""
                )
            )


def print_calculated_field(column: ET.Element) -> None:
    f = formula(column)

    if not f:
        return

    print()
    print(f"Caption:  {column.attrib.get('caption')}")
    print(f"Name:     {column.attrib.get('name')}")
    print(f"Datatype: {column.attrib.get('datatype')}")
    print(f"Role:     {column.attrib.get('role')}")
    print(f"Type:     {column.attrib.get('type')}")
    print("Formula:")
    print(f)


def main() -> int:
    if not WORKBOOK.exists():
        print(f"Workbook not found: {WORKBOOK}", file=sys.stderr)
        return 1

    print(f"Opening: {WORKBOOK}")
    print(f"Size: {WORKBOOK.stat().st_size:,} bytes")

    tree = ET.parse(WORKBOOK)
    root = tree.getroot()

    print()
    print("=== WORKBOOK ===")
    print(f"Source build:   {root.attrib.get('source-build')}")
    print(f"Source platform: {root.attrib.get('source-platform')}")
    print(f"Version:        {root.attrib.get('version')}")

    repository = first_child(root, "repository-location")

    if repository is not None:
        print(f"Repository ID:  {repository.attrib.get('id')}")
        print(f"Revision:       {repository.attrib.get('revision')}")

    # ------------------------------------------------------------------
    # DATASOURCES
    # ------------------------------------------------------------------

    datasources_container = first_child(root, "datasources")

    if datasources_container is None:
        print("No datasources section.")
        return 1

    datasources = children(datasources_container, "datasource")

    print()
    print("=== DATASOURCES ===")

    for datasource in datasources:
        print()
        print(f"Datasource: {datasource.attrib.get('name')}")
        print(f"Caption:    {datasource.attrib.get('caption')}")
        print(f"Inline:     {datasource.attrib.get('inline')}")
        print(f"Connection: {datasource.attrib.get('hasconnection')}")

        columns = children(datasource, "column")

        print(f"Columns:    {len(columns)}")

        for column in columns:
            print(
                f"  {column.attrib.get('name')}"
                f"  caption={column.attrib.get('caption')!r}"
                f"  datatype={column.attrib.get('datatype')}"
                f"  role={column.attrib.get('role')}"
                f"  type={column.attrib.get('type')}"
            )

    # ------------------------------------------------------------------
    # PARAMETERS
    # ------------------------------------------------------------------

    print()
    print("=== PARAMETERS ===")

    parameter_count = 0

    for datasource in datasources:
        for column in children(datasource, "column"):
            if "param-domain-type" not in column.attrib:
                continue

            parameter_count += 1

            print()
            print_parameter(column)

    print()
    print(f"Parameter count: {parameter_count}")

    # ------------------------------------------------------------------
    # CALCULATED FIELDS
    # ------------------------------------------------------------------

    print()
    print("=== CALCULATED FIELDS ===")

    calculated_count = 0

    for datasource in datasources:
        for column in children(datasource, "column"):
            f = formula(column)

            if not f:
                continue

            # Parameters are printed separately.
            if "param-domain-type" in column.attrib:
                continue

            calculated_count += 1
            print_calculated_field(column)

    print()
    print(f"Calculated field count: {calculated_count}")

    # ------------------------------------------------------------------
    # TARGET SEARCH
    # ------------------------------------------------------------------

    targets = {
        "Crash Breakdown 2",
        "Metric Selector",
        "Municipality Name (ifnull)",
        "Street Full Name (ifnull)",
        "[Crash Breakdown (copy)]",
    }

    print()
    print("=== TARGET FIELDS ===")

    found = set()

    for datasource in datasources:
        for column in children(datasource, "column"):
            name = column.attrib.get("name")
            caption = column.attrib.get("caption")

            if name in targets or caption in targets:
                found.add(name or caption)

                print()
                print(f"Datasource: {datasource.attrib.get('name')}")
                print(f"Name:       {name}")
                print(f"Caption:    {caption}")
                print(f"Datatype:   {column.attrib.get('datatype')}")
                print(f"Role:       {column.attrib.get('role')}")
                print(f"Type:       {column.attrib.get('type')}")

                if "param-domain-type" in column.attrib:
                    print_parameter(column)
                else:
                    f = formula(column)
                    if f:
                        print("Formula:")
                        print(f)

    print()
    print("Found:")
    for item in sorted(found):
        print(f"  {item}")

    missing = targets - found

    if missing:
        print()
        print("Not found:")
        for item in sorted(missing):
            print(f"  {item}")

    # ------------------------------------------------------------------
    # WORKSHEETS
    # ------------------------------------------------------------------

    print()
    print("=== WORKSHEETS ===")

    worksheets = []

    for element in root.iter():
        if tag(element) == "worksheet":
            worksheets.append(element)

    for worksheet in worksheets:
        print(f"  {worksheet.attrib.get('name')}")

    print()
    print(f"Worksheet count: {len(worksheets)}")

    # ------------------------------------------------------------------
    # DASHBOARDS
    # ------------------------------------------------------------------

    print()
    print("=== DASHBOARDS ===")

    dashboards = []

    for element in root.iter():
        if tag(element) == "dashboard":
            dashboards.append(element)

    for dashboard in dashboards:
        print(f"  {dashboard.attrib.get('name')}")

    print()
    print(f"Dashboard count: {len(dashboards)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
