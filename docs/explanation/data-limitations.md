# Data limitations

The dataset is useful for describing reported crashes at an aggregate level. It is
not a complete crash census, a person-level injury dataset, or a real-time feed.
This page explains the limits that matter most for analysis.

## Summary

| Limitation | Consequence |
|---|---|
| Rows are aggregates | `COUNT(*)` is not a crash count; use `SUM(TOTAL_CRASHES)`. |
| Only crashes reported to ICBC | Undercounts relative to all crashes; not directly comparable to police data. |
| No unique crash ID | Cannot deduplicate or link records to individual crashes. |
| No person-level or vehicle-level detail | Cannot analyze age, injury type, vehicle type, or contributing factors. |
| No exact date | Cannot reconstruct calendar dates, holidays, or exact time of day. |
| Aggressive location missingness | About 18% of records lack coordinates; about 56% lack a cross street. |
| Approximate geocodes | Coordinates and road descriptions are approximate. |
| Revisions and methodology changes | Counts can change between editions; 2021 has pandemic effects. |
| No exposure denominator | Cannot compute crash rates without joining external population, vehicle, or travel data. |
| Derived fields are not ground truth | Crash configuration and `(ifnull)` fields are derived, not observed. |

## Rows are not crashes

A row is one distinct combination of the non-measure dimensions. `TOTAL_CRASHES`
says how many crashes that combination represents. On the documented snapshot:

- 1,453,136 records;
- 1,465,435 crashes;
- 1,441,897 records represent exactly one crash;
- 11,239 records represent two or more crashes;
- the largest record represents 11 crashes.

So these are different questions:

| Question | Expression |
|---|---|
| How many records? | `COUNT(*)` or `len(df)` |
| How many crashes? | `SUM(TOTAL_CRASHES)` |
| How many victims? | `SUM(TOTAL_VICTIMS)` |
| Average victims per crash? | `SUM(TOTAL_VICTIMS) / SUM(TOTAL_CRASHES)` |

`AVG(TOTAL_CRASHES)` is the average number of crashes per **record**, not per
crash. It answers a question about the aggregation, not about crash frequency.

The same caution applies to victims. A record with `TOTAL_VICTIMS = 5` may
represent one crash with five victims or several crashes whose victims sum to
five. The data does not distinguish those cases.

## Not a census of all crashes

The source is built from reports made to ICBC. ICBC's own caveat notes that its
crash data is significantly higher than police-reported data because basic
insurance coverage is mandatory, but that does not make it a complete count of
every crash. Crashes that were not reported to ICBC are absent.

The data also excludes crashes outside British Columbia and includes incidents in
parking lots or involving parked vehicles. If your question is about public-road
traffic crashes, decide explicitly whether parking-lot and parked-vehicle records
belong in your analysis.

## No individual-level detail

The public extract is aggregated. It does not contain:

- a crash identifier;
- a person identifier;
- driver or pedestrian age;
- sex or gender;
- injury type (fatal, serious, non-serious, none);
- vehicle type or model;
- contributing factors such as speed, impairment, or distraction;
- road, weather, or lighting conditions.

`CRASH_SEVERITY` only distinguishes casualty crashes from property-damage-only
crashes. It does not let you count fatalities or serious injuries separately, and
`TOTAL_VICTIMS` does not distinguish injury severity. Person-level questions need a
different dataset.

## No exact date or time

The temporal fields are:

- `DATE_OF_LOSS_YEAR`;
- `MONTH_OF_YEAR`;
- `DAY_OF_WEEK`;
- `TIME_CATEGORY` (three-hour bucket).

There is no day of month, full date, or exact timestamp. A year/month/weekday
combination can correspond to several actual dates. You cannot reliably identify
holidays, long weekends, specific events, or within-bucket timing.

The time bucket is broad: `15:00-17:59` covers three hours, not the afternoon peak
minute by minute.

## Location is incomplete and approximate

In the documented snapshot:

| Field | Missing | Share |
|---|---:|---:|
| `LATITUDE` | 261,968 | 18.0% |
| `LONGITUDE` | 261,968 | 18.0% |
| `MUNICIPALITY_WITH_BOUNDARY` | 261,968 | 18.0% |
| `CROSS_STREET_FULL_NAME` | 815,517 | 56.1% |
| `STREET_FULL_NAME` | 451 | 0.03% |

ICBC states that geocode information is approximate and is assigned only when
there was enough location information. Crashes without enough information have
blank geocode fields. Mapping or spatial analysis therefore undercounts crashes,
and the missingness is not random: it is tied to whether the report contained
enough location detail.

`CROSS_STREET_FULL_NAME` applies to intersection crashes only, which explains most
of its missingness. Do not treat it as a general street field.
`MUNICIPALITY_WITH_BOUNDARY` can contain multiple municipalities joined with `&`
for border crashes (`DELTA & SURREY`). Grouping by the raw string will separate
those records from the individual municipality names.

## Revisions and methodology changes

ICBC revises counts because of late reporting, corrections, rounding, and data
development. The workbook warns that cyclist-related data was improved in early
2023, so counts from 2014 onward may be higher than previously reported. It also
warns that 2021 data may be affected by the COVID-19 pandemic.

Treat the most recent year as provisional. A changed total after a refresh is not
automatically a bug; compare the capture date and document the revision.

## No exposure denominator

The dataset contains crash counts, not exposure. It has no population, registered
vehicle count, distance travelled, or traffic volume. You cannot compute a crash
rate per capita or per vehicle-kilometre from this dataset alone. Joining external
denominators is possible, but the join and its assumptions become part of your
analysis and must be documented.

## Derived fields are not observations

`DERIVED_CRASH_CONFIGURATION` is based on claim reports, not a police collision
diagram. It includes `UNDETERMINED` and `CONFLICTED` categories, which account for a
substantial share of records. Treat it as a reported/derived classification, not a
definitive cause.

The two `(ifnull)` fields replace missing values with `Unknown`. That is convenient
for grouping, but it hides missingness. Use `MUNICIPALITY_NAME` and
`STREET_FULL_NAME` when you need to distinguish "missing" from a literal
`UNKNOWN` value.

The involvement flags (`CYCLIST_FLAG`, `PEDESTRIAN_FLAG`, `ANIMAL_FLAG`,
`HEAVY_VEH_FLAG`, `MOTORCYCLE_FLAG`, `PARKED_VEHICLE_FLAG`) indicate involvement,
not causation. A `Y` does not mean the involved party caused the crash.

## What the data can support

With appropriate caution, the dataset can support:

- counts of reported crashes and victims by year, month, weekday, and time bucket;
- comparisons by region, municipality, severity, and crash configuration;
- involvement-flag summaries;
- approximate spatial patterns where coordinates are present;
- descriptive trend analysis with explicit caveats about revisions.

## What the data cannot support

Without additional data and assumptions, it cannot support:

- exact-date or exact-time analysis;
- fatality or serious-injury rates;
- person-level or vehicle-level risk analysis;
- causal claims about speed, impairment, distraction, or road design;
- crash rates without an exposure denominator;
- real-time monitoring;
- a claim that every crash in British Columbia is represented.

## Related pages

- [Data provenance](data-provenance.md)
- [Caveats and licence](../reference/caveats-and-licence.md)
- [Dataset schema](../reference/dataset-schema.md)
- [Query the export](../how-to-guides/query-the-export.md)
