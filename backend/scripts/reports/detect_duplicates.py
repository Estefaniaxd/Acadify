#!/usr/bin/env python3
"""Detecta archivos duplicados en backend/static/assets por SHA256 y genera reportes.

Salida:
 - reports/duplicates_by_hash.csv (hash,count,canonical,paths...)
 - reports/duplicate_groups.json (list of groups with metadata)
 - reports/delete_plan.csv (hash,keep_path,delete_path,reason)  <- PROPOSAL, no elimina

No se realizan cambios en disco; es solo análisis.
"""
import hashlib
import json
from pathlib import Path
from collections import defaultdict
import csv

ROOT = Path(__file__).resolve().parents[2] / "static" / "assets"
OUTDIR = Path(__file__).resolve().parents[0] / "reports"
OUTDIR.mkdir(parents=True, exist_ok=True)


def iter_files(root: Path):
    for p in sorted(root.rglob("*.png")):
        yield p


def sha256_of(path: Path, chunk_size=8192):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def choose_canonical(paths):
    # Prefer paths containing /unisex/ then /female/ then /male/
    pref = ["/unisex/", "/female/", "/male/"]
    paths = list(paths)
    for p in pref:
        for x in paths:
            if p in str(x):
                return x
    # fallback: shortest path string
    return min(paths, key=lambda x: len(str(x)))


def main():
    files = list(iter_files(ROOT))
    print(f"Found {len(files)} png files under {ROOT}")

    hash_map = defaultdict(list)
    for p in files:
        try:
            h = sha256_of(p)
        except Exception as e:
            print(f"Error hashing {p}: {e}")
            continue
        hash_map[h].append(p)

    dup_groups = []
    csv_path = OUTDIR / "duplicates_by_hash.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sha256", "count", "canonical", "paths"])
        for h, paths in sorted(hash_map.items(), key=lambda x: (-len(x[1]), x[0])):
            if len(paths) > 1:
                canonical = choose_canonical(paths)
                writer.writerow([h, len(paths), str(canonical), ";".join(map(str, paths))])
                dup_groups.append({
                    "sha256": h,
                    "count": len(paths),
                    "canonical": str(canonical),
                    "paths": [str(p) for p in paths],
                })

    # write json
    json_path = OUTDIR / "duplicate_groups.json"
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(dup_groups, fh, indent=2, ensure_ascii=False)

    # generate delete plan (proposal only)
    plan_path = OUTDIR / "delete_plan.csv"
    with plan_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sha256", "keep_path", "delete_path", "reason"])
        for g in dup_groups:
            keep = Path(g["canonical"])
            for p in g["paths"]:
                pth = Path(p)
                if pth == keep:
                    continue
                reason = "duplicate_of_canonical"
                writer.writerow([g["sha256"], str(keep), str(pth), reason])

    print(f"Wrote reports to {OUTDIR}")


if __name__ == "__main__":
    main()
