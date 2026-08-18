from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://catalogue.data.gov.bc.ca/api/3/action"
DATASET_ID = "icbc-reported-crashes"

ROOT = Path(__file__).resolve().parents[2]
METADATA_DIR = ROOT / "data" / "metadata"


def package_show(dataset_id: str) -> dict:
    params = urlencode({"id": dataset_id})
    url = f"{API_BASE}/package_show?{params}"

    request = Request(
        url,
        headers={
            "User-Agent": "icbc-reported-crashes-research/0.1",
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=30) as response:
        payload = json.load(response)

    if not payload.get("success"):
        raise RuntimeError(f"Catalogue API returned failure: {payload}")

    return payload["result"]


def main() -> None:
    dataset = package_show(DATASET_ID)

    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    output = METADATA_DIR / "catalogue.json"
    output.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Dataset:   {dataset['title']}")
    print(f"ID:        {dataset['id']}")
    print(f"Name:      {dataset['name']}")
    print(f"Resources: {len(dataset.get('resources', []))}")
    print()

    for resource in dataset.get("resources", []):
        print(f"Resource: {resource.get('name')}")
        print(f"  ID:     {resource.get('id')}")
        print(f"  Format: {resource.get('format')}")
        print(f"  URL:    {resource.get('url')}")
        print()


if __name__ == "__main__":
    main()
