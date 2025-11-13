#!/usr/bin/env python3
"""Prepare mapping CSV for SQL generator.

Reads: backend/scripts/reports/mapping_hair_provisional.csv with headers (original,canonical)
Writes: backend/scripts/avatar_normalize_output/avatar_normalize_mapping.csv with headers (source,candidate_rel,type)

For each mapping pair we emit two rows by default:
 - type=avatar_asset (updates avatar_asset.filename when it's a basename)
 - type=user_avatar (updates user_avatar JSON layers)

Candidate_rel is made relative to the assets root (e.g., 'hair/female/hair_4.png').
"""
from pathlib import Path
import csv


def rel_candidate(path: str) -> str:
    # Expect path like backend/static/assets/hair/female/hair_4.png
    parts = path.split("backend/static/assets/")
    if len(parts) == 2:
        return parts[1].lstrip("/")
    # fallback: return basename
    return Path(path).name


def main() -> int:
    src = Path("backend/scripts/reports/mapping_hair_provisional.csv")
    out_dir = Path("backend/scripts/avatar_normalize_output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "avatar_normalize_mapping.csv"

    if not src.exists():
        print("Source mapping not found:", src)
        return 1

    with src.open("r", encoding="utf-8") as fh_in, out.open("w", encoding="utf-8", newline="") as fh_out:
        reader = csv.DictReader(fh_in)
        writer = csv.DictWriter(fh_out, fieldnames=["source", "candidate_rel", "type"])
        writer.writeheader()
        for r in reader:
            original = r.get("original") or r.get("source")
            canonical = r.get("canonical") or r.get("candidate_rel")
            if not original or not canonical:
                continue
            source_basename = Path(original).name
            candidate_rel = rel_candidate(canonical)
            # emit avatar_asset row
            writer.writerow({"source": source_basename, "candidate_rel": candidate_rel, "type": "avatar_asset"})
            # emit user_avatar row
            writer.writerow({"source": source_basename, "candidate_rel": candidate_rel, "type": "user_avatar"})

    print("Wrote mapping for SQL to:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
