from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = ROOT / "data" / "raw" / "tableau" / "ICBCReportedCrashes.twb"


def main() -> None:
    with ZipFile(WORKBOOK) as zf:
        entries = zf.infolist()

        print(f"Archive: {WORKBOOK}")
        print(f"Files:   {len(entries)}")
        print()

        for entry in entries:
            print(
                f"{entry.file_size:>12,} bytes  "
                f"{entry.compress_size:>12,} compressed  "
                f"{entry.filename}"
            )


if __name__ == "__main__":
    main()
