# Tableau workbook anatomy

The pipeline starts from a file called `ICBCReportedCrashes.twb`. Despite the
extension, the download is a ZIP container. It holds the workbook XML, the main
Hyper data extract, several smaller metadata extracts, and a help image. This page
explains what is inside and why the export flattens only part of it.

## The download is a container

`tableau.py` saves the response as `data/raw/tableau/ICBCReportedCrashes.twb`. The
inspection script can list it because it is a ZIP archive:

```text
46,858,240 bytes   Data/ICBC Reported Crashes.twb Files/2021-2025 public data set.hyper
   65,536 bytes   Data/Extracts/federated_0bn82t81yj94ap1fr622a1.hyper
  131,072 bytes   Data/Extracts/federated_1oll1kn0e530bn1d8o3ar0.hyper
   65,536 bytes   Data/Extracts/federated_1p7tlca06yuz791brgeig0.hyper
   65,536 bytes   Data/ICBC Reported Crashes 1.twb files/Caveats (Public data sets - Metadata) (2).hyper
  174,748 bytes   Image/Public Dataset - Job Aid for Tableau Public (PNG) - ICBC Crash v2.PNG
  873,244 bytes   ICBC Reported Crashes.twb
```

`extract_tableau.py` extracts only the `.hyper` and `.twb` entries, flattening
their archive paths:

```text
data/raw/tableau/extracted/
├── 2021-2025 public data set.hyper
├── Caveats (Public data sets - Metadata) (2).hyper
├── federated_0bn82t81yj94ap1fr622a1.hyper
├── federated_1oll1kn0e530bn1d8o3ar0.hyper
├── federated_1p7tlca06yuz791brgeig0.hyper
└── ICBC Reported Crashes.twb
```

The image is not extracted because the pipeline does not need it.

## Main extract

`2021-2025 public data set.hyper` is the data source for the export. It contains one
schema and one table:

```text
"Extract"."Extract"
```

with the 25 physical crash columns documented in the
[dataset schema](../reference/dataset-schema.md). The downloaded name is
hardcoded in the export, profile, and inspection scripts.

The export discovers the table by its column set rather than requiring the exact
name. That is deliberate: Tableau's internal table names can change, but the
physical columns are the contract the export needs.

## Workbook XML

`ICBC Reported Crashes.twb` is XML. The inspected copy reports:

| Property | Value |
|---|---|
| Source build | `2025.1.10 (20251.25.1121.1650)` |
| Source platform | `win` |
| Version | `18.1` |
| Repository ID | `ICBCReportedCrashes` |
| Revision | `3.3` |

The XML defines datasources, parameters, calculated fields, worksheets, and
dashboards. `inspect_workbook.py` prints a summary.

### Datasources

The main datasource is `federated.06k05501veeus410zxlyb01uqepc`, captioned
`2021-2025 public data set`. It contains the 25 physical columns, the two
`(ifnull)` calculated fields, the `Metric Selector` calculation, and the
`Crash Breakdown 2` calculation.

There are also metadata datasources for:

- regions and their definitions;
- the data dictionary;
- caveats;
- the open-data licence.

The `Parameters` datasource holds the dashboard parameters. This is why the
workbook can contain more than the crash table: it is a self-contained public
reporting application, not just a data export.

### Parameters

The inspected workbook has three parameters:

| Caption | Internal name | Allowed values | Current value |
|---|---|---|---|
| `Crash Breakdown` | `[Parameter 1]` | Crash Severity, Crash Configuration, Region, Month, Day of Week, Time Category | Day of Week |
| `Crash Breakdown 2` | `[Crash Breakdown (copy)]` | Crash Severity, Crash Configuration, Region, Municipality, Street Name, Road Location Description | Municipality |
| `Metric Selector` | `[Parameter 2]` | Crash Count, Victim Count | Crash Count |

`Crash Breakdown 2` and `Metric Selector` are the ones documented in the export
schema. The older `Crash Breakdown` parameter is part of the workbook but is not a
column in the CSV.

### Calculated fields

The row-level calculated fields used by the export are:

```tableau
IFNULL([MUNICIPALITY_NAME], "Unknown")
```

```tableau
ifnull([STREET_FULL_NAME], "Unknown")
```

The export materializes these as `Municipality Name (ifnull)` and
`Street Full Name (ifnull)`.

The parameter-driven fields are:

```tableau
if [Parameters].[Parameter 2] = "Crash Count" then sum([TOTAL_CRASHES])
elseif [Parameters].[Parameter 2] = "Victim Count" then sum([TOTAL_VICTIMS])
END
```

```tableau
if [Parameters].[Crash Breakdown (copy)] = "Crash Configuration"
    then [DERIVED_CRASH_CONFIGURATION]
elseif [Parameters].[Crash Breakdown (copy)] = "Region"
    then [REGION]
elseif [Parameters].[Crash Breakdown (copy)] = "Municipality"
    then [Calculation_2389159665885708288]
elseif [Parameters].[Crash Breakdown (copy)] = "Street Name"
    then [Calculation_2389159665886253057]
elseif [Parameters].[Crash Breakdown (copy)] = "Road Location Description"
    then [ROAD_LOCATION_DESCRIPTION]
elseif [Parameters].[Crash Breakdown (copy)] = "Crash Severity"
    then [CRASH_SEVERITY]
END
```

These cannot be represented as one fixed row-level value. The export records their
choices in `calculated_fields` and `parameters` instead of inventing a value.

### Worksheets and dashboards

The inspected workbook has 33 worksheets and 18 dashboards. The main dashboard is
`ICBC Reported Crashes`, with regional and topic-specific views such as Lower
Mainland, Vancouver Island, Southern Interior, North Central, cyclists, pedestrians,
motorcycles, heavy vehicles, animal impact, and parking lots. There are also data
dictionary, caveats, and licence dashboards.

These counts and names are snapshot-specific. They matter only if you are
inspecting the workbook itself; the CSV export does not depend on the dashboard
layout.

## Metadata extracts

The smaller `.hyper` files support the workbook's explanatory dashboards:

| File | Contents |
|---|---|
| `Caveats (Public data sets - Metadata) (2).hyper` | Caveats for multiple ICBC datasets |
| `federated_0bn...hyper` | Region names and definitions |
| `federated_1oll...hyper` | Data dictionary entries for ICBC datasets |
| `federated_1p7...hyper` | Open-data licence text |

The data dictionary is useful for understanding field meanings, but its labels do
not always match the public column names. For example, the dictionary uses
`CYCLIST INCLUDED` and `HEAVY VEHICLE INCLUDED`, while the extract uses
`CYCLIST_FLAG` and `HEAVY_VEH_FLAG`.

## Why the export does not use the workbook's dashboards

The workbook is an interactive reporting application. Its visible numbers depend
on dashboard filters and parameter selections. The pipeline's job is to produce a
portable, row-level dataset, so it exports the physical rows plus the two
unconditional row-level calculations.

It deliberately does not:

- choose a `Metric Selector` value for every row;
- choose a `Crash Breakdown 2` dimension for every row;
- reproduce dashboard filters;
- apply workbook aggregations.

If you need a dashboard-equivalent number, compute it from the CSV with an explicit
filter and aggregation, and document the choice.

## Related pages

- [Data provenance](data-provenance.md)
- [Dataset schema](../reference/dataset-schema.md)
- [Inspect the Tableau and Hyper assets](../how-to-guides/inspect-tableau-assets.md)
- [Metadata files](../reference/metadata-files.md)
