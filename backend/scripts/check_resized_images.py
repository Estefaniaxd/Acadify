#!/usr/bin/env python3
from pathlib import Path
import csv
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'scripts' / 'reports' / 'reports' / 'resize_report_apply.csv'
ASSETS = ROOT / 'static' / 'assets'

found = 0
mismatch = []
missing = []
with REPORT.open(encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    for r in reader:
        fname = (r.get('filename') or '').strip()
        if not fname:
            continue
        path = ASSETS / Path(fname)
        if not path.exists():
            missing.append(fname)
            continue
        try:
            with Image.open(path) as im:
                if im.size != (512,512):
                    mismatch.append((fname, im.size))
                else:
                    found += 1
        except Exception as e:
            mismatch.append((fname, f'open_error:{e}'))

print('Checked:', sum(1 for _ in open(REPORT)))
print('Resized OK count:', found)
print('Missing count:', len(missing))
print('Mismatches count:', len(mismatch))
if missing:
    print('\nMissing files:')
    for m in missing[:50]:
        print('-', m)
if mismatch:
    print('\nMismatched files (should be 512x512):')
    for m in mismatch[:100]:
        print('-', m)

# exit code
import sys
if mismatch or missing:
    sys.exit(2)
else:
    sys.exit(0)
