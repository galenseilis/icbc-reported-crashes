# Data provenance

This page explains where the data comes from and what the pipeline does and does
not record about a particular copy.

## Lineage

```text
Crash reports to ICBC
        │
        │  ICBC data development, geocoding, and aggregation
        ▼
ICBC Reported Crashes public data set
        │
        ├── BC Data Catalogue record (metadata, licence, caveats)
        └── Tableau Public workbook (data, dashboards, dictionary)
                    │
                    │  this repository
                    ▼
        downloaded workbook → Hyper extract → CSV → partitions
```

The source is ICBC's public reporting of crashes gathered from reports made to
ICBC by insured registered vehicle owners, drivers, pedestrians, and cyclists. It
is not a census of every crash and it is not police-reported crash data. ICBC's
own caveat says its data is significantly higher than police-reported data because
basic insurance coverage through ICBC is mandatory, so crash occurrences are
reported to ICBC.

## Source records

| Item | Value |
|---|---|
| Dataset title | ICBC Reported Crashes |
| Publisher | Insurance Corporation of British Columbia |
| Catalogue record | <https://catalogue.data.gov.bc.ca/dataset/icbc-reported-crashes> |
| Catalogue dataset ID | `2640963c-eb1e-46ea-8ca7-867754b69b2d` |
| Resource | Tableau Public view, linked from the catalogue |
| Workbook URL used by the pipeline | <https://public.tableau.com/workbooks/ICBCReportedCrashes.twb> |
| Licence | [ICBC Open Data Licence](https://www.icbc.com/policies/Pages/open-data-licence.aspx) |

The catalogue record's `metadata_modified` value (2021-03-08 in the record
inspected for these docs) describes the catalogue entry, not the data capture. The
workbook is the better source for the current data capture date and revision.

## What the documented snapshot contains

The 2021–2025 extract inspected for this documentation reports:

| Property | Value |
|---|---|
| Workbook repository ID | `ICBCReportedCrashes` |
| Workbook revision | `3.3` |
| Workbook source build | `2025.1.10 (20251.25.1121.1650)` |
| Data capture date | 31 March 2026 |
| Years | 2021–2025 |
| Records | 1,453,136 |
| Crashes | 1,465,435 |
| Victims | 347,413 |

The workbook contains the main crash extract plus smaller metadata extracts for
the data dictionary, caveats, region definitions, and open-data licence. It also
contains 33 worksheets and 18 dashboards in the inspected copy. These are
snapshot-specific observations; check the current workbook before quoting them.

## Publication cadence and revisions

ICBC states that data is available by late spring or early summer of the following
year, sourced from its Analytical Data Store. The public workbook is an annual
snapshot that ICBC can revise.

Counts can change because of:

- late reporting;
- corrections;
- rounding;
- further development of the data;
- changes in how cyclist and pedestrian crashes are recorded.

The workbook also notes that cyclist-related crash and injury data was improved in
early 2023, so counts from 2014 onward may be higher than previously reported. The
2021 data may be affected by the COVID-19 pandemic. See
[Caveats and licence](../reference/caveats-and-licence.md) for the exact source
wording.

## What the pipeline records

The processed artifacts record:

- the source table name and row count in the export schema;
- the physical column types and nullability;
- the calculated-field and parameter definitions as summaries;
- the export conventions (alphabetical columns, `\N` nulls, deterministic order).

They do **not** record:

- the download timestamp;
- the workbook's HTTP headers, ETag, or checksum;
- the workbook revision or data capture date;
- the Git commit that produced the artifacts;
- a checksum of the CSV or partition tree.

This is enough to reproduce the transformation from a fixed Hyper file, but not
enough to prove that two runs used the same source. If provenance matters for your
use case, record those details yourself alongside the analysis.

## Reproducible provenance checklist

For a published analysis, record at least:

1. the repository commit (`git rev-parse HEAD`);
2. the date you downloaded the workbook;
3. the workbook revision and data capture date from the caveats;
4. the export schema's `source.row_count`;
5. the total crashes and victims from the CSV;
6. the exact query or script used for the analysis.

A small provenance block could look like this:

```text
Source: ICBC Reported Crashes, BC Data Catalogue
Workbook: ICBCReportedCrashes.twb, revision 3.3
Data captured: 2026-03-31
Downloaded: 2026-10-26
Commit: <git sha>
Rows: 1,453,136
Crashes: 1,465,435
Victims: 347,413
Licence: ICBC Open Data Licence
```

## What this project is not

This repository is an independent pipeline over a public data set. It is not
affiliated with or endorsed by ICBC. It does not add data from insurance claims,
police reports, or other sources, and it does not correct or impute the source. Any
analysis, inference, or conclusion belongs to the analyst, not to ICBC.

## Related pages

- [Data limitations](data-limitations.md)
- [Caveats and licence](../reference/caveats-and-licence.md)
- [Tableau workbook anatomy](tableau-workbook-anatomy.md)
- [Architecture](architecture.md)
