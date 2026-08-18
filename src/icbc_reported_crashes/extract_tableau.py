from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[2]
WORKBOOK = ROOT / "data" / "raw" / "tableau" / "ICBCReportedCrashes.twb"
EXTRACTED = ROOT / "data" / "raw" / "tableau" / "extracted"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def main() -> None:
    EXTRACTED.mkdir(parents=True, exist_ok=True)

    with ZipFile(WORKBOOK) as archive:
        hyper_files = [
            info
            for info in archive.infolist()
            if info.filename.lower().endswith(".hyper")
        ]

        twb_files = [
            info
            for info in archive.infolist()
            if info.filename.lower().endswith(".twb")
        ]

        print(f"Hyper files: {len(hyper_files)}")
        print(f"TWB files:   {len(twb_files)}")
        print()

        for info in hyper_files:
            print(f"{info.file_size:>12,} bytes  {info.filename}")

            output = EXTRACTED / Path(info.filename).name
            output.write_bytes(archive.read(info))

            print(f"  -> {output}")
            print(f"  SHA256: {sha256(output)}")
            print()

        for info in twb_files:
            print(f"TWB: {info.filename}")

            output = EXTRACTED / Path(info.filename).name
            output.write_bytes(archive.read(info))

            print(f"  -> {output}")
            print(f"  SHA256: {sha256(output)}")
            print()


if __name__ == "__main__":
    main()
