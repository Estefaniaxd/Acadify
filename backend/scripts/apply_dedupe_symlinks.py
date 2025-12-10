#!/usr/bin/env python3
"""Apply deduplication by moving duplicate files to a backup and replacing them with symlinks to the canonical file.

Usage:
  python3 scripts/apply_dedupe_symlinks.py --mapping backend/scripts/reports/mapping_all_provisional.csv [--dry-run] [--apply]

By default runs a dry-run. Use --apply to perform changes.

The script is reversible: moved files are stored under backend/static/backups/dedupe.<timestamp>/moved/
A log file with operations is written to backend/scripts/reports/dedupe_ops_<timestamp>.log
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "static" / "assets"
REPORT_DIR = ROOT / "scripts" / "reports"


def make_timestamp():
    return time.strftime("%Y%m%d%H%M%S")


def load_mapping(mapping_path: Path) -> list[tuple[Path, Path]]:
    pairs = []
    with mapping_path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            orig = Path(row["original"])
            canon = Path(row["canonical"])
            pairs.append((orig, canon))
    return pairs


def ensure_report_dir():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def plan_ops(pairs: list[tuple[Path, Path]]) -> list[dict]:
    ops = []
    for orig, canon in pairs:
        # Normalize to project-root relative if necessary.
        # Some mapping CSVs include the leading 'backend/' path; handle both cases.
        def abs_from_mapping(p: Path) -> Path:
            if p.is_absolute():
                return p
            parts = list(p.parts)
            if parts and parts[0] == "backend":
                # strip leading 'backend' which duplicates ROOT
                return ROOT / Path(*parts[1:])
            return ROOT / p

        orig_abs = abs_from_mapping(orig)
        canon_abs = abs_from_mapping(canon)

        ops.append({
            "original": orig_abs,
            "canonical": canon_abs,
            "original_exists": orig_abs.exists(),
            "canonical_exists": canon_abs.exists(),
        })
    return ops


def execute_ops(ops: list[dict], apply: bool, backup_root: Path, log_path: Path) -> None:
    moved_dir = backup_root / "moved"
    moved_dir.mkdir(parents=True, exist_ok=True)

    with log_path.open("w", encoding="utf-8") as logf:
        for op in ops:
            orig = op["original"]
            canon = op["canonical"]
            logf.write(f"OP: orig={orig} canon={canon} orig_exists={op['original_exists']} canon_exists={op['canonical_exists']}\n")

            if not op["original_exists"]:
                logf.write("  SKIP: original not found\n")
                continue
            if not op["canonical_exists"]:
                logf.write("  SKIP: canonical not found\n")
                continue
            # Resolve to absolute canonical target
            try:
                canon_real = canon.resolve()
            except Exception:
                canon_real = canon

            # If both paths are same file, skip
            try:
                if orig.resolve() == canon_real:
                    logf.write("  SKIP: already canonical\n")
                    continue
            except Exception:
                pass

            # Prepare backup path
            rel_orig = orig.relative_to(ROOT)
            backup_target = moved_dir / rel_orig
            backup_target.parent.mkdir(parents=True, exist_ok=True)

            # Compute symlink target (relative) from orig location to canonical
            # We'll use relative symlink so moving the whole assets dir preserves links
            try:
                rel_target = os.path.relpath(canon_real, start=orig.parent)
            except Exception:
                rel_target = str(canon_real)

            logf.write(f"  ACTION: move {orig} -> {backup_target}; symlink -> {rel_target}\n")

            if not apply:
                continue

            # Move original to backup and create symlink
            try:
                shutil.move(str(orig), str(backup_target))
                os.symlink(rel_target, orig)
                logf.write("  DONE\n")
            except Exception as e:
                logf.write(f"  ERROR: {e}\n")


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", required=True, help="CSV mapping original->canonical")
    parser.add_argument("--apply", action="store_true", help="Apply changes instead of dry-run")
    args = parser.parse_args(argv)

    mapping_path = Path(args.mapping)
    if not mapping_path.exists():
        print("Mapping file not found:", mapping_path)
        return 2

    ensure_report_dir()
    pairs = load_mapping(mapping_path)
    ops = plan_ops(pairs)

    ts = make_timestamp()
    backup_root = ROOT / "static" / "backups" / f"dedupe.{ts}"
    log_path = REPORT_DIR / f"dedupe_ops_{ts}.log"

    # Summary
    total = len(ops)
    orig_exists = sum(1 for o in ops if o["original_exists"])
    canon_exists = sum(1 for o in ops if o["canonical_exists"])
    print(f"Planned ops: {total}, originals found: {orig_exists}, canonicals found: {canon_exists}")
    print("Log will be written to:", log_path)
    print("Backup root:", backup_root)

    execute_ops(ops, args.apply, backup_root, log_path)

    if args.apply:
        print("Apply completed. Backup and symlinks created.")
    else:
        print("Dry-run completed. No changes made.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
