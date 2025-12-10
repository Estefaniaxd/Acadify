#!/usr/bin/env python3
"""Restore missing assets from resize_report_apply.csv backups and re-create 512x512 normalized images.

Usage: python3 restore_from_resize_backups.py
"""
import csv
import os
import shutil
from pathlib import Path
from PIL import Image

REPORT = Path(__file__).resolve().parent / "reports" / "reports" / "resize_report_apply.csv"
ASSETS_ROOT = Path(__file__).resolve().parent.parent / "static" / "assets"

restored = 0
if not REPORT.exists():
    print('REPORT_MISSING', REPORT)
    raise SystemExit(1)

print('Using report:', REPORT)
print('Assets root:', ASSETS_ROOT)

with REPORT.open(newline='') as fh:
    reader = csv.reader(fh)
    for row in reader:
        if not row:
            continue
        filename = row[0]
        backup_path = row[4] if len(row) > 4 else ''
        if not backup_path:
            # Nothing to restore from
            continue
        dest = ASSETS_ROOT / filename
        if dest.exists():
            continue
        if not Path(backup_path).exists():
            print('NO_BACKUP_FOR', filename, 'backup', backup_path)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup_path, dest)
        try:
            im = Image.open(dest).convert('RGBA')
            im.thumbnail((512, 512), Image.LANCZOS)
            w, h = im.size
            bg = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            bg.paste(im, ((512 - w) // 2, (512 - h) // 2), im)
            bg.save(dest, optimize=True)
            restored += 1
            print('RESTORED', filename)
        except Exception as e:
            print('ERROR_PROCESS', filename, e)

print('DONE restored', restored)
