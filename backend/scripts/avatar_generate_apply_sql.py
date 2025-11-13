#!/usr/bin/env python3
"""Genera SQL aplicable (por lotes) a partir de avatar_normalize_mapping.csv.

Este script toma el CSV generado por el dry-run (`avatar_normalize_mapping.csv`) y
produce dos archivos SQL:
- avatar_normalize_apply_avatar_asset.sql -> UPDATEs para tabla avatar_asset
- avatar_normalize_apply_user_avatar.sql -> UPDATEs para tabla user_avatar (JSON replacement)

El SQL resultante mantiene comentarios y recomendaciones. No ejecuta nada por sí mismo.

Uso:
  python backend/scripts/avatar_generate_apply_sql.py --in backend/scripts/avatar_normalize_output/avatar_normalize_mapping.csv --out-dir backend/scripts/avatar_normalize_output

Requiere revisión manual antes de aplicar. Siempre crear backup: pg_dump -Fc -f /tmp/backup.dump acadify_db
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def q(s: str) -> str:
    """Escape single quotes for SQL literals."""
    return s.replace("'", "''")


def generate_sql(in_csv: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    avatar_asset_sql = out_dir / "avatar_normalize_apply_avatar_asset.sql"
    user_avatar_sql = out_dir / "avatar_normalize_apply_user_avatar.sql"

    rows = []
    with in_csv.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)

    with avatar_asset_sql.open("w", encoding="utf-8") as a_fh, user_avatar_sql.open("w", encoding="utf-8") as u_fh:
        a_fh.write("-- avatar_asset updates generated from mapping CSV\n")
        a_fh.write("-- Review carefully and run in a transaction or in small batches.\n\n")

        u_fh.write("-- user_avatar updates generated from mapping CSV\n")
        u_fh.write("-- These updates rebuild the `layers` JSON replacing basenames with canonical paths.\n")
        u_fh.write("-- Review and test in staging before applying to production.\n\n")

        for r in rows:
            source = r.get("source", "").strip()
            target = r.get("candidate_rel", "").strip()
            typ = r.get("type", "").strip()
            if not source or not target:
                continue

            if typ == "avatar_asset":
                # Simple update for avatar_asset
                a_fh.write("BEGIN;\n")
                a_fh.write(
                    "UPDATE avatar_asset SET filename = '{t}' WHERE filename = '{s}' AND filename NOT LIKE '%/%';\n".format(t=q(target), s=q(source))
                )
                a_fh.write("-- Verify the update: SELECT * FROM avatar_asset WHERE filename = '{t}';\n".format(t=q(target)))
                a_fh.write("COMMIT;\n\n")
            elif typ == "user_avatar":
                # JSON replace for user_avatar.layers
                # For each mapping we generate an UPDATE that replaces occurrences of the basename in layers->file
                u_fh.write("BEGIN;\n")
                u_fh.write(
                    "UPDATE user_avatar\nSET layers = (\n  SELECT jsonb_agg(\n    CASE WHEN elem->>'file' = '{s}' THEN jsonb_set(elem, '{{file}}', to_jsonb('{t}'::text)) ELSE elem END\n  )\n  FROM jsonb_array_elements(layers::jsonb) elem\n)\nWHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '{s}');\n".format(s=q(source), t=q(target))
                )
                u_fh.write("-- Verify rows affected: SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '{s}');\n".format(s=q(source)))
                u_fh.write("COMMIT;\n\n")

    print(f"Wrote: {avatar_asset_sql}")
    print(f"Wrote: {user_avatar_sql}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_csv", required=True)
    parser.add_argument("--out-dir", dest="out_dir", required=True)
    args = parser.parse_args()

    in_csv = Path(args.in_csv)
    out_dir = Path(args.out_dir)
    if not in_csv.exists():
        raise SystemExit(f"Input CSV not found: {in_csv}")

    generate_sql(in_csv, out_dir)


if __name__ == "__main__":
    main()
