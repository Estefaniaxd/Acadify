#!/usr/bin/env python3
"""Genera un plan de normalización para avatar filenames y layers.

Modo seguro (dry-run): analiza el árbol de assets y las entradas en la BD
(usando psql) y genera un archivo SQL con UPDATEs sugeridos.

No aplica cambios por defecto. Para aplicar, ejecutar con --apply (requiere confirmación).

Uso:
  python backend/scripts/avatar_normalize_dryrun.py --assets-dir ../static/assets --out plan_dir

Requisitos:
  - psql en PATH con acceso a la BD (o ajustar PG env vars)
  - permisos de lectura del repo
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


def inventory_assets(assets_dir: Path) -> dict[str, list[Path]]:
    """Return a mapping from basename -> list[Path] for files under assets_dir.

    Only image files (.png, .jpg, .jpeg) are included.
    """
    mapping: dict[str, list[Path]] = {}
    for p in assets_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            name = p.name
            mapping.setdefault(name, []).append(p)
    return mapping


def run_psql(query: str, psql_cmd: str = "psql") -> list[str]:
    """Run a psql command and return non-empty output lines.

    psql_cmd may be a full command (e.g. "psql" or "/usr/bin/psql").
    If the call fails and the default "psql" was used, the function will
    attempt a fallback using `sudo -u postgres psql`.
    """
    parts = [*shlex.split(psql_cmd), "-At", "-c", query]
    try:
        out = subprocess.check_output(parts, stderr=subprocess.DEVNULL, text=True)
        return [ln for ln in out.splitlines() if ln.strip()]
    except subprocess.CalledProcessError:
        # Try fallback if the simple psql failed
        if psql_cmd == "psql":
            try:
                fallback = ["sudo", "-u", "postgres", "psql", "-At", "-c", query]
                out = subprocess.check_output(fallback, stderr=subprocess.DEVNULL, text=True)
                return [ln for ln in out.splitlines() if ln.strip()]
            except subprocess.CalledProcessError:
                print("Error: cannot run psql. Ensure psql is available or run this script with appropriate DB access.", file=sys.stderr)
                return []
        print("Error: cannot run psql. Ensure psql is available or run this script with appropriate DB access.", file=sys.stderr)
        return []


def collect_db_filenames(psql_cmd: str = "psql") -> list[str]:
    """Return list of filenames from table avatar_asset."""
    return run_psql("SELECT filename FROM avatar_asset;", psql_cmd)


def collect_user_layer_files(psql_cmd: str = "psql") -> list[str]:
    """Return list of layer file names extracted from user_avatar.layers JSON."""
    return run_psql("SELECT elem->>'file' FROM user_avatar ua, jsonb_array_elements(layers::jsonb) elem;", psql_cmd)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-dir", default=str(Path(__file__).parents[1] / "static" / "assets"))
    parser.add_argument("--out", default=str(Path(__file__).parents[1] / "scripts" / "avatar_normalize_output"))
    parser.add_argument("--psql-cmd", default="psql", help="Command to invoke psql (default: psql). Can be a full path.")
    parser.add_argument("--apply", action="store_true", help="Apply changes (WARNING: destructive)")
    args = parser.parse_args()

    assets_dir = Path(args.assets_dir).resolve()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scanning assets at: {assets_dir}")
    inventory = inventory_assets(assets_dir)
    total_files = sum(len(v) for v in inventory.values())
    print(f"Found {total_files} files (by basename: {len(inventory)})")

    print("Collecting DB filenames (avatar_asset)...")
    db_files = collect_db_filenames(args.psql_cmd)
    print(f"avatar_asset rows: {len(db_files)}")

    print("Collecting user_avatar layer files...")
    user_files = collect_user_layer_files(args.psql_cmd)
    print(f"user_avatar layer entries: {len(user_files)}")

    # Build plan
    mappings: list[tuple[str, str, str]] = []  # tuples (source, candidate_rel, type)
    ambiguous: list[tuple[str, list[str], str]] = []

    def pick_candidate(name: str):
        if name in inventory:
            cand = inventory[name]
            if len(cand) == 1:
                return cand[0]
            return cand
        return None

    # Check avatar_asset rows
    for src_name in db_files:
        fname = src_name.strip()
        if not fname:
            continue
        # Try to resolve either bare basenames or filenames that include a path.
        # Use the inventory of files by basename to find a filesystem candidate.
        base = os.path.basename(fname)
        cand = pick_candidate(base)
        if isinstance(cand, Path):
            rel = str(cand.relative_to(assets_dir)).replace(os.path.sep, "/")
            # Only add mapping if the target differs from the current DB value
            if rel != fname:
                mappings.append((fname, rel, "avatar_asset"))
        elif isinstance(cand, list):
            ambiguous.append((fname, [str(p.relative_to(assets_dir)).replace(os.path.sep, "/") for p in cand], "avatar_asset"))

    # Check user layer files
    for src_name in user_files:
        fname = src_name.strip()
        if not fname:
            continue
        base = os.path.basename(fname)
        cand = pick_candidate(base)
        if isinstance(cand, Path):
            rel = str(cand.relative_to(assets_dir)).replace(os.path.sep, "/")
            if rel != fname:
                mappings.append((fname, rel, "user_avatar"))
        elif isinstance(cand, list):
            ambiguous.append((fname, [str(p.relative_to(assets_dir)).replace(os.path.sep, "/") for p in cand], "user_avatar"))

    # Write outputs
    map_csv = out_dir / "avatar_normalize_mapping.csv"
    with map_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["source", "candidate_rel", "type"])
        for m in mappings:
            writer.writerow(m)

    amb_txt = out_dir / "avatar_normalize_ambiguous.txt"
    with amb_txt.open("w", encoding="utf-8") as fh:
        for a in ambiguous:
            fh.write(json.dumps(a, ensure_ascii=False) + "\n")

    sql_plan = out_dir / "avatar_normalize_plan.sql"
    with sql_plan.open("w", encoding="utf-8") as fh:
        fh.write("-- Dry-run SQL plan to normalize filenames. Review before applying.\n")
        fh.write("-- Backup DB before applying: pg_dump -Fc -f /path/to/backup.dump acadify_db\n")
        for src, tgt, typ in mappings:
            if typ == "avatar_asset":
                fh.write("-- Update avatar_asset filename exact match (dry-run)\n")
                fh.write(
                    "-- UPDATE avatar_asset SET filename = '{tgt}' WHERE filename = '{src}' AND filename NOT LIKE '%/%';\n".format(
                        tgt=tgt.replace("'", "''"), src=src.replace("'", "''"),
                    )
                )
            else:
                fh.write("-- Update user_avatar layers replacing basename with category path (dry-run)\n")
                fh.write(
                    "-- SELECT id FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = '{src}');\n".format(src=src.replace("'", "''"))
                )
                fh.write(
                    "-- -- For each id, you can run an UPDATE that rebuilds the layers JSON replacing occurrences of '{src}' with '{tgt}'\n".format(src=src.replace("'", "''"), tgt=tgt.replace("'", "''"))
                )

    print("Outputs written to:")
    print(f" - mapping CSV: {map_csv}")
    print(f" - ambiguous: {amb_txt}")
    print(f" - SQL plan (dry-run): {sql_plan}")

    if ambiguous:
        print("\nWARNING: Ambiguous candidates found for some basenames. Review the ambiguous file to resolve manually.")

    if args.apply:
        print("--apply requested but this script DOES NOT automatically execute SQL updates. Use the generated SQL after review.")


if __name__ == "__main__":
    main()
