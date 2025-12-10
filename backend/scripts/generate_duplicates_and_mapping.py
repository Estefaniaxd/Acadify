"""Scan assets, group duplicates by hash and produce a provisional mapping CSV.

This script walks the assets directory (backend/static/assets), computes a
SHA256 digest for each image file (ignoring any normalized outputs) and
groups files that are byte-identical.

Outputs:
 - backend/scripts/reports/duplicates_all.txt
 - backend/scripts/reports/mapping_all_provisional.csv (original,canonical)

Rule for canonical selection (provisional): prefer paths containing
"/unisex/", then "/female/", then "/male/". Falls back to the first
path found.
"""

from __future__ import annotations

import csv
import hashlib
import os
from collections import defaultdict
from pathlib import Path


ASSETS_DIR = Path("backend/static/assets")
REPORT_DIR = Path("backend/scripts/reports")


def sha256_of_file(p: Path) -> str:
    """Return the SHA256 hex digest of file at path p.

    Reads the file in chunks to avoid high memory usage.
    """
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def choose_canonical(paths: list[Path]) -> Path:
    """Choose a canonical path from paths using a preference order.

    Preference: unisex > female > male > first found.
    """
    normalized = [str(p).replace(os.path.sep, "/") for p in paths]
    for pref in ["/unisex/", "/female/", "/male/"]:
        for p in normalized:
            if pref in p:
                return Path(p)
    return Path(normalized[0])


def main() -> int:
    """Run the scan and write reports. Returns exit code."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    groups: dict[str, list[Path]] = defaultdict(list)

    if not ASSETS_DIR.exists():
        print("Assets dir not found:", ASSETS_DIR)
        return 2

    # Walk categories for PNG files
    for p in ASSETS_DIR.rglob("*.png"):
        if "normalized" in p.parts:
            # ignore normalized outputs
            continue
        digest = sha256_of_file(p)
        groups[digest].append(p)

    dup_path = REPORT_DIR / "duplicates_all.txt"
    map_path = REPORT_DIR / "mapping_all_provisional.csv"

    with dup_path.open("w", encoding="utf-8") as fdup, map_path.open("w", encoding="utf-8", newline="") as fmap:
        writer = csv.writer(fmap)
        writer.writerow(["original", "canonical"])

        for digest, items in groups.items():
            if len(items) <= 1:
                continue

            fdup.write(f"sha256 {digest}\n")
            for it in items:
                fdup.write(f"  {it}\n")

            canonical = choose_canonical(items)

            # write mapping for all non-canonical -> canonical
            for it in items:
                if Path(it) == canonical:
                    continue
                writer.writerow([str(it), str(canonical)])

    print("Wrote duplicates to:", dup_path)
    print("Wrote provisional mapping to:", map_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
