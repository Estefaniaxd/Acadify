#!/usr/bin/env python3
"""Generate rollback SQL from snapshot CSVs.

Expect files in backend/scripts/avatar_normalize_output/:
 - preapply_avatar_asset_snapshot.csv  (id,filename)
 - preapply_user_avatar_snapshot.csv  (id,layers)

This script produces `backend/scripts/avatar_normalize_output/rollback.sql` which contains
UPDATE statements to restore the previous values by primary key (id).
"""
from __future__ import annotations

import csv
from pathlib import Path


def write_avatar_asset_rollback(rows, out_fh):
    for r in rows:
        id_ = r["id"].strip()
        filename = r["filename"].replace("'", "''")
        out_fh.write("BEGIN;\n")
        out_fh.write(f"UPDATE avatar_asset SET filename = '{filename}' WHERE id = {id_};\n")
        out_fh.write(f"-- Verify: SELECT id, filename FROM avatar_asset WHERE id = {id_};\n")
        out_fh.write("COMMIT;\n\n")


def write_user_avatar_rollback(rows, out_fh):
    for r in rows:
        id_ = r["id"].strip()
        layers = r["layers"].replace("'", "''")
        out_fh.write("BEGIN;\n")
        out_fh.write(f"UPDATE user_avatar SET layers = '{layers}'::jsonb WHERE id = {id_};\n")
        out_fh.write(f"-- Verify: SELECT id FROM user_avatar WHERE id = {id_};\n")
        out_fh.write("COMMIT;\n\n")


def main() -> int:
    out_dir = Path("backend/scripts/avatar_normalize_output")
    avatar_csv = out_dir / "preapply_avatar_asset_snapshot.csv"
    user_csv = out_dir / "preapply_user_avatar_snapshot.csv"
    out_sql = out_dir / "rollback.sql"

    with out_sql.open("w", encoding="utf-8") as out_fh:
        if avatar_csv.exists():
            with avatar_csv.open("r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
                write_avatar_asset_rollback(rows, out_fh)

        if user_csv.exists():
            with user_csv.open("r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
                write_user_avatar_rollback(rows, out_fh)

    print("Wrote rollback SQL to:", out_sql)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
