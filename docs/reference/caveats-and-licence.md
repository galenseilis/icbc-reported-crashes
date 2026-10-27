# Caveats and licence

This page records the official caveats and licence terms that apply to the ICBC
Reported Crashes data. They are facts about the source, not opinions about how to
analyze it. For the analytical consequences, see
[Data limitations](../explanation/data-limitations.md).

## Official data caveats

The workbook includes a caveats table for multiple ICBC datasets. The rows below
are the ones explicitly attached to **ICBC Reported Crashes** in the documented
2021–2025 workbook. Quoted text is from the source.

| ID | Category | Caveat |
|---|---|---|
| 0 | Data captured as of | `31-Mar-2026` in the inspected workbook |
| 1 | Data collection and processing | ICBC crash data is gathered from reports made to ICBC by insured registered vehicle owners, drivers, pedestrians and cyclists. |
| 2 | Data collection and processing | ICBC’s cyclist related crash and injury data was improved in early 2023. As a result, counts from 2014 onward may be higher than previously reported. Overall data trends remain consistent. |
| 3 | Availability of the data | Counts may differ from previous editions due to further development of data, rounding, late reporting or corrections. |
| 4 | Data parameters | Geocode information, sourced from GeoBC Digital Road Atlas, containing Road Location Description, Latitude, and Longitude, is approximate and is only assigned to crashes where sufficient location information was available. Crashes with insufficient location information have blank values for the associated geocode information. |
| 5 | Data parameters | Data includes incidents that occurred in parking lots or involved parked vehicles. |
| 6 | Data parameters | Crashes that occurred outside of B.C. have been excluded. |
| 7 | Availability of the data | ICBC data is available by late spring/early summer of the following year (i.e., spring 2024 for 2023 data). The source is ICBC’s Analytical Data Store. |
| 8 | Data collection and processing | Crash data and trends from 2021 may be impacted by the COVID-19 pandemic. |
| 9 | Data collection and processing | Pedestrian and cyclist related crash data include crashes where pedestrians or cyclists did not report an injury or claim to ICBC. |
| 40 | Data collection and processing | ICBC crash data is significantly higher than police reported crash data as basic insurance coverage through ICBC is mandatory so crash occurrences are reported to ICBC. Since 2008, there have been several legislative changes regarding the reporting of motor vehicle crashes to/by a police officer which has led to a marked decrease in the number of police-attended crash reports submitted to ICBC, particularly for crashes that do not involve fatalities. The number of reports submitted by individuals to police is also very low, as it’s not mandatory that a crash be reported to police. Therefore, ICBC crash data is a more comprehensive view on crashes and injuries in B.C. |

The capture date describes the copy inspected while writing these docs. Always
read the current value from the downloaded workbook rather than assuming it is
still 31 March 2026.

### Region definitions

The workbook also defines the regions used in `REGION`:

| Region | Definition |
|---|---|
| Lower Mainland | Includes the entire south-west corner of mainland B.C., from Pemberton to Boston Bar. It includes the Fraser Valley, Greater Vancouver and the southern Sunshine Coast. |
| Vancouver Island | Also encompasses the Gulf Islands and the mainland coastal community of Powell River. |
| Southern Interior | Includes the southern third of the province, including the Kamloops area, Okanagan and Kootenay regions, as far west as Boston Bar and Lillooet. |
| North Central | Includes the central Interior as far south as 100 Mile House, the Peace River district, Prince Rupert and Haida Gwaii, and all points north. |
| Unknown | In some reports, insufficient location details were available or gathered when the incidents were reported and these are listed as “Unknown”. |

## ICBC Open Data Licence

The data is published under the
[ICBC Open Data Licence](https://www.icbc.com/policies/Pages/open-data-licence.aspx).
The licence grants a worldwide, royalty-free, perpetual, non-exclusive licence to
use the information, including for commercial purposes, subject to its terms.

### Required attribution

Include this statement when you use the information:

> Contains information licensed under ICBC’s Open Data Licence.

### Non-endorsement

The licence does not grant the right to suggest official ICBC status or
endorsement. It also requires that you do not attribute results to ICBC. The
source licence provides this statement:

> All analysis, inferences, opinions, and conclusions drawn in this
> [_________________] are those of the authors, and do not reflect the opinions,
> position or policies of ICBC.

Fill in the blank with the name of your publication or analysis.

### Other terms

The licence also covers acceptable uses, exemptions (personal information,
third-party rights, official marks, and similar), and a no-warranty/no-liability
clause. Read the
[full licence](https://www.icbc.com/policies/Pages/open-data-licence.aspx) before
redistributing the data. This page summarizes the terms for convenience and is not
legal advice.

## Suggested citation

There is no single required citation format, but this captures the source,
catalogue record, access date, and licence:

> Insurance Corporation of British Columbia. *ICBC Reported Crashes* [data set].
> BC Data Catalogue. https://catalogue.data.gov.bc.ca/dataset/icbc-reported-crashes
> (accessed YYYY-MM-DD). Licensed under the ICBC Open Data Licence.

Replace the access date with the date you retrieved the data. If you used a
particular workbook capture date, state it as well.

## Code licence

The repository does not contain a `LICENSE` file. The ICBC Open Data Licence
applies to the data; it does not automatically license the source code in this
repository. Treat the code's licensing status as unspecified until a code licence
is added.

## Related pages

- [Data provenance](../explanation/data-provenance.md)
- [Data limitations](../explanation/data-limitations.md)
- [Dataset schema](dataset-schema.md)
- [Fetch dataset metadata](../how-to-guides/fetch-dataset-metadata.md)
