#!/usr/bin/env python3
"""Backfill avatar_asset.canonical_path and sha256 from delete_plan.csv

This script:
 - reads delete_plan.csv (keep_path, delete_path, sha256)
 - computes relative paths as stored in DB (strip assets root)
 - generates SQL UPDATE statements to set canonical_path and sha256 for rows
 - writes a rollback SQL to unset those fields
 - by default runs in dry-run; use --apply to execute against DB (uses .env DATABASE_URL)

Usage:
  backfill_avatar_asset.py --delete-plan PATH [--apply]
"""
import argparse
import csv
import os
import subprocess
from pathlib import Path


ASSETS_ROOT = Path('backend/static/assets').resolve()


def relpath_in_db(abs_path: str) -> str:
    # Convert absolute or workspace-relative path to DB filename (relative under assets root)
    p = Path(abs_path)
    try:
        rel = p.resolve().relative_to(ASSETS_ROOT)
        return str(rel).replace(os.path.sep, '/')
    except Exception:
        # maybe already relative
        s = str(abs_path)
        if s.startswith('/'):
            # remove leading parts up to assets
            parts = s.split(str(ASSETS_ROOT))
            if len(parts) >= 2:
                return parts[-1].lstrip(os.sep)
        return s


def load_plan(path: str):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def gen_sql(rows):
    stmts = []
    rollback = []
    for r in rows:
        keep = r.get('keep_path')
        delete = r.get('delete_path')
        sha = r.get('sha256') or r.get('sha') or r.get('sha256')
        if not keep or not delete:
            continue
        rel_keep = relpath_in_db(keep)
        rel_delete = relpath_in_db(delete)
        # SET canonical_path to rel_keep and sha256
        stmts.append("UPDATE avatar_asset SET canonical_path = '{k}', sha256 = '{s}' WHERE filename = '{d}';".format(k=rel_keep.replace("'","''"), s=(sha or '').replace("'","''"), d=rel_delete.replace("'","''")))
        rollback.append("UPDATE avatar_asset SET canonical_path = NULL, sha256 = NULL WHERE filename = '{d}';".format(d=rel_delete.replace("'","''")))
    return stmts, rollback


def write_file(path: Path, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def run_sql_file(dburl: str, path: Path):
    cmd = ['psql', dburl, '-v', 'ON_ERROR_STOP=1', '-f', str(path)]
    print('Running:', ' '.join(cmd))
    subprocess.check_call(cmd)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--delete-plan', required=True)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()

    rows = load_plan(args.delete_plan)
    if not rows:
        print('No rows in delete plan')
        return 1

    stmts, rollback = gen_sql(rows)
    out_dir = Path('scripts/reports/reports')
    sql_file = out_dir / 'backfill_avatar_asset.sql'
    rb_file = out_dir / 'backfill_avatar_asset_rollback.sql'
    write_file(sql_file, ['BEGIN;'] + stmts + ['COMMIT;'])
    write_file(rb_file, ['BEGIN;'] + rollback + ['COMMIT;'])

    print('Wrote SQL:', sql_file)
    print('Wrote rollback:', rb_file)
    print('Sample UPDATEs:')
    for s in stmts[:10]:
        print(' ', s)

    if not args.apply:
        print('\nDry-run mode. Use --apply to execute the SQL against DB (uses DATABASE_URL from .env).')
        return 0

    # load DB URL from .env
    dburl = None
    if Path('.env').exists():
        for line in Path('.env').read_text().splitlines():
            if line.startswith('DATABASE_URL='):
                dburl = line.split('=',1)[1].strip().strip('"')
                break
    if not dburl:
        raise RuntimeError('DATABASE_URL not found in .env')

    # execute SQL file
    run_sql_file(dburl, sql_file)
    print('Backfill applied')


if __name__ == '__main__':
    main()
