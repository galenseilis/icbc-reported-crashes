# Fetch dataset metadata

Use this guide to save the BC Data Catalogue record for the ICBC Reported Crashes
dataset. The record contains the official description, licence, lineage, caveats,
contacts, and the resource link to the public Tableau workbook.

This metadata is **not** downloaded by `./run`. Fetch it separately when you need
provenance or citation material.

## Steps

### 1. Run the catalogue script

From the repository root:

```bash
uv run src/icbc_reported_crashes/catalogue.py
```

The script calls the BC Data Catalogue's CKAN API:

```text
https://catalogue.data.gov.bc.ca/api/3/action/package_show?id=icbc-reported-crashes
```

No API key is required. The request has a 30-second timeout and identifies itself
with a project user agent.

### 2. Read the terminal summary

The script prints the dataset title, ID, name, number of resources, and the
details of each resource:

```text
Dataset:   ICBC Reported Crashes
ID:        2640963c-eb1e-46ea-8ca7-867754b69b2d
Name:      icbc-reported-crashes
Resources: 1

Resource: ICBC Reported Crashes
  ID:     ...
  Format: txt
  URL:    https://public.tableau.com/profile/icbc#!/vizhome/ICBCReportedCrashes/ICBCReportedCrashes
```

The resource is an indirect link to the Tableau Public view, not a direct CSV
download. The pipeline gets its data from the workbook URL in
`tableau.py`, not from this resource URL.

### 3. Check the saved payload

The full API response is written to `data/metadata/catalogue.json`:

```bash
ls -lh data/metadata/catalogue.json
uv run python -m json.tool data/metadata/catalogue.json | head -n 40
```

The file is the raw `result` object from `package_show`. Useful fields include:

| Field | Use |
|---|---|
| `title`, `notes` | Dataset name and description |
| `license_title`, `license_url` | Data licence and link |
| `data_quality` | Official caveats about counts and geocoding |
| `lineage_statement` | Source and capture context |
| `organization` | Publishing organization |
| `contacts` | Point of contact |
| `resources` | Distribution link and field list |
| `metadata_modified`, `record_last_modified` | Catalogue record timestamps |

### 4. Decide whether to commit the file

`data/metadata/` is not covered by the existing ignore rules. After fetching,
`git status` will show the new JSON file. Commit it only if you want to pin the
catalogue record alongside the data snapshot; otherwise leave it untracked.

The catalogue record can lag the workbook. For the current data capture date,
check the workbook's caveats table or the value reported by
`inspect_workbook.py`; the catalogue's `metadata_modified` date describes the
catalogue record, not the data.

## What can go wrong

- **Network timeout or connection error** — retry later, or check access to
  `catalogue.data.gov.bc.ca`.
- **`Catalogue API returned failure`** — the dataset ID may have changed, or the
  API returned an error payload. Inspect the printed payload.
- **HTTP 403 or 404** — the API endpoint or dataset identifier is unavailable.
  Confirm the record still exists at
  <https://catalogue.data.gov.bc.ca/dataset/icbc-reported-crashes>.

## Related pages

- [Data provenance](../explanation/data-provenance.md)
- [Caveats and licence](../reference/caveats-and-licence.md)
- [Metadata files](../reference/metadata-files.md)
- [Pipeline script reference](../reference/pipeline-scripts.md#catalogue)
