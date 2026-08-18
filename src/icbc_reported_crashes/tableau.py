from __future__ import annotations

from pathlib import Path
from urllib.request import Request, urlopen


WORKBOOK_URL = (
    "https://public.tableau.com/workbooks/ICBCReportedCrashes.twb"
)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "tableau"


def download(url: str, output: Path) -> None:
    request = Request(
        url,
        headers={
            "User-Agent": "icbc-reported-crashes-research/0.1",
            "Accept": "*/*",
        },
    )

    with urlopen(request, timeout=60) as response:
        data = response.read()

        print("HTTP status:", response.status)
        print("Content-Type:", response.headers.get("Content-Type"))
        print("Content-Length:", response.headers.get("Content-Length"))
        print("Final URL:", response.url)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(data)

    print(f"Saved: {output}")
    print(f"Bytes: {len(data):,}")


def main() -> None:
    output = RAW_DIR / "ICBCReportedCrashes.twb"
    download(WORKBOOK_URL, output)


if __name__ == "__main__":
    main()
