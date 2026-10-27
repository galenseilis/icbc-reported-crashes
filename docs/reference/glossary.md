# Glossary

Terms are defined as they are used in this project and documentation.

## Aggregated record

One row of the exported dataset. A record is a distinct combination of the
non-measure dimensions, with `TOTAL_CRASHES` and `TOTAL_VICTIMS` as measures. A
record can represent more than one crash. See
[Grain](dataset-schema.md#grain).

## BC Data Catalogue

The provincial open-data catalogue at
<https://catalogue.data.gov.bc.ca/>. It hosts the ICBC Reported Crashes record and
its licence and caveats.

## Calculated field

A field whose value is computed rather than stored as a physical source column.
The export materializes two row-level calculated fields and documents two
Tableau-only fields that depend on dashboard parameters.

## Capture date

The date as of which ICBC captured the data. The documented workbook reports
`31-Mar-2026`. The capture date is not the same as the catalogue record's
`metadata_modified` date or the date you downloaded the workbook.

## Casualty crash

A crash resulting in injury or fatality. The other `CRASH_SEVERITY` value is
`PROPERTY DAMAGE ONLY`.

## CKAN

The open-data platform API used by the BC Data Catalogue. `catalogue.py` calls its
`package_show` action.

## Crash

A reported crash represented in the source data. Because rows are aggregates, the
number of crashes is `SUM(TOTAL_CRASHES)`, not the number of rows. See
[Crashes versus records](../explanation/data-limitations.md#rows-are-not-crashes).

## Crash configuration

The reported or derived manner of collision, such as rear end, side impact, or
single vehicle. The public dataset uses `DERIVED_CRASH_CONFIGURATION`, which is
derived from claim reports.

## Deterministic export

An export whose column order, row order, null representation, and formatting are
fixed for a given source and code version. See
[Deterministic exports](../explanation/deterministic-exports.md).

## Dimension

A field used to group or describe records, such as region, municipality, month,
or crash severity. In this dataset, the non-measure columns are dimensions.

## Extract

A data file produced by Tableau, often with a `.hyper` extension. The main extract
in this project is `2021-2025 public data set.hyper`.

## Full refresh

A run that replaces the processed artifacts with a fresh copy of the source. This
project does not perform incremental updates.

## Geocode

Latitude, longitude, and related location information. ICBC assigns geocode fields
only when it has enough location information; otherwise they are missing.

## Grain

The meaning of one row. Here, one row is a distinct combination of non-measure
dimensions, not one crash. See [Grain](dataset-schema.md#grain).

## Hyper

Tableau's columnar data engine and file format. The `.hyper` files are read through
the Tableau Hyper API.

## Hyper API

The `tableauhyperapi` Python package used to open Hyper files, inspect their
catalog, and run SQL queries locally.

## Measure

A numeric field that can be summed or averaged. Here, `TOTAL_CRASHES` and
`TOTAL_VICTIMS` are measures.

## Municipality with boundary

A municipality field that includes every municipality touched by a border crash,
joined with `&`, for example `DELTA & SURREY`.

## Null sentinel

The literal two-character sequence `\N` used in the CSV to represent a missing
value. It is not an empty field. See
[Nulls and missing values](dataset-schema.md#nulls-and-missing-values).

## Partition

One CSV in `data/processed/records/`, corresponding to one year, month, weekday,
and time bucket. See [Records layout](records-layout.md).

## Physical column

A column that exists in the Hyper source table, as opposed to a calculated or
derived column. The documented snapshot has 25 physical columns.

## Property damage only

A crash with material damage but no injury or fatality. In this dataset, these
records have zero victims.

## Region

One of ICBC's geographic regions: Lower Mainland, Southern Interior, Vancouver
Island, North Central, or Unknown.

## Snapshot

The state of the source and generated artifacts at a particular capture and run.
Counts in this documentation describe the 2021–2025 snapshot.

## Tableau Public

The public Tableau platform that hosts the ICBC workbook. The pipeline downloads a
workbook from `public.tableau.com`.

## TWB

A Tableau workbook file. The downloaded `ICBCReportedCrashes.twb` is a ZIP
container; the extracted `ICBC Reported Crashes.twb` is XML. See
[Tableau workbook anatomy](../explanation/tableau-workbook-anatomy.md).

## Victim

A person injured or killed in a crash, as counted by `TOTAL_VICTIMS`. The field is
an aggregate; the dataset does not contain person-level records.

## Workbook

The Tableau file that contains the data connection, calculated fields, parameters,
worksheets, and dashboards. In this project, "workbook" usually means the
downloaded ZIP or the extracted XML inside it.
