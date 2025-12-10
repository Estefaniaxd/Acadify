#!/usr/bin/env python3
"""Copy all PNGs from reports/backups/resize_backups/* into backend/static/assets preserving relative structure.

This will only copy if destination does not already exist.
"""
import os
from pathlib import Path
import shutil

BACKUPS_ROOT = Path(__file__).resolve().parent / 'reports' / 'backups' / 'resize_backups'
ASSETS_ROOT = Path(__file__).resolve().parent.parent / 'static' / 'assets'

copied=0
if not BACKUPS_ROOT.exists():
    print('No backups root:', BACKUPS_ROOT)
    raise SystemExit(1)

for tsdir in BACKUPS_ROOT.iterdir():
    if not tsdir.is_dir():
        continue
    for p in tsdir.rglob('*.png'):
        # compute relative path inside tsdir
        rel = p.relative_to(tsdir)
        dest = ASSETS_ROOT / rel
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        copied += 1
        print('COPIED', rel)

print('DONE copied', copied)
