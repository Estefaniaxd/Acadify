#!/usr/bin/env python3
"""Helper to produce psql \copy commands (or run them) to snapshot rows affected by mapping.

Usage (dry-run, prints commands):
  python backend/scripts/create_snapshots_for_mapping.py --mapping backend/scripts/avatar_normalize_output/avatar_normalize_mapping.csv

To execute (needs psql in PATH and a reachable DB):
  python backend/scripts/create_snapshots_for_mapping.py --mapping ... --db-url postgresql://user:pass@host:5432/dbname --exec

Outputs (in backend/scripts/avatar_normalize_output/):
  - preapply_avatar_asset_snapshot.csv  (id,filename)
  - preapply_user_avatar_snapshot.csv  (id,layers)

Note: Runs SELECTs using psql \copy to CSV. When --exec is not provided, the script only prints the psql commands for manual review.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import shlex
import subprocess
import sys


def read_sources(mapping: Path) -> list[str]:
    sources = []
    with mapping.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            sources.append(r.get("source", "").strip())
    return sorted(set(sources))


def make_psql_copy_commands(sources: list[str], out_dir: Path) -> tuple[str, str]:
    # prepare IN list for SQL
    quoted = ",".join([f"'{s}'" for s in sources])
    avatar_asset_out = out_dir / "preapply_avatar_asset_snapshot.csv"
    user_avatar_out = out_dir / "preapply_user_avatar_snapshot.csv"

    cmd_asset = (
        f"\\copy (SELECT id, filename FROM avatar_asset WHERE filename IN ({quoted})) TO '{avatar_asset_out}' CSV HEADER;"
    )

    cmd_user = (
        "\\copy (SELECT id, layers FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' IN ("
        + quoted
        + ")) ) TO '"
        + str(user_avatar_out)
        + "' CSV HEADER;"
    )

    return cmd_asset, cmd_user


def run_psql(db_url: str, cmd: str) -> int:
    # run psql -c "<cmd>"
    full = ["psql", db_url, "-c", cmd]
    print("Running:", " ".join(shlex.quote(p) for p in full))
    res = subprocess.run(full)
    return res.returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", required=True, help="CSV mapping produced for SQL (avatar_normalize_mapping.csv)")
    parser.add_argument("--db-url", help="postgresql connection string (optional). If omitted, commands are printed only.")
    parser.add_argument("--exec", action="store_true", help="Execute the psql commands (requires --db-url and psql in PATH)")
    args = parser.parse_args()

    mapping = Path(args.mapping)
    if not mapping.exists():
        print("Mapping CSV not found:", mapping)
        return 2

    out_dir = Path("backend/scripts/avatar_normalize_output")
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = read_sources(mapping)
    if not sources:
        print("No sources found in mapping; aborting.")
        return 0

    cmd_asset, cmd_user = make_psql_copy_commands(sources, out_dir)

    print("-- psql copy command for avatar_asset snapshot:")
    print(cmd_asset)
    print()
    print("-- psql copy command for user_avatar snapshot:")
    print(cmd_user)
    print()

    if args.exec:
        if not args.db_url:
            print("--exec requires --db-url")
            return 3
        ec = run_psql(args.db_url, cmd_asset)
        if ec != 0:
            print("psql returned", ec)
            return ec
        ec = run_psql(args.db_url, cmd_user)
        if ec != 0:
            print("psql returned", ec)
            return ec

    print("Snapshot commands printed (or executed). Check backend/scripts/avatar_normalize_output for CSVs if executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
