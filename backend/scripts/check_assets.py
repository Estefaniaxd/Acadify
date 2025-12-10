#!/usr/bin/env python3
from pathlib import Path
from PIL import Image
import sys

ASSETS_DIR = Path(__file__).resolve().parents[1] / 'static' / 'assets'
if not ASSETS_DIR.exists():
    print('Assets dir not found:', ASSETS_DIR)
    sys.exit(1)

print('Assets dir:', ASSETS_DIR)

# Count files per top-level category
for d in sorted([p for p in ASSETS_DIR.iterdir() if p.is_dir()]):
    cnt = sum(1 for _ in d.rglob('*') if _.is_file())
    print(f'{d.name}: {cnt} files')

# Total files
total = sum(1 for _ in ASSETS_DIR.rglob('*') if _.is_file())
print('Total files:', total)

# Sample first 40 image files and print sizes
print('\nSample image sizes (up to 40 PNGs):')
files = list(ASSETS_DIR.rglob('*.png'))[:40]
if not files:
    print('No PNG files found')
else:
    for f in files:
        try:
            with Image.open(f) as im:
                print(f.relative_to(ASSETS_DIR), im.size, 'mode='+im.mode)
        except Exception as e:
            print('ERR', f, e)

# Check normalized_preview_aspect exists and sizes
NP = Path(__file__).resolve().parents[1] / 'static' / 'normalized_preview_aspect'
print('\nNormalized preview aspect dir:', NP)
if NP.exists():
    samples = list(NP.rglob('*.png'))[:40]
    print('Normalized preview files count:', sum(1 for _ in NP.rglob('*') if _.is_file()))
    for f in samples:
        try:
            with Image.open(f) as im:
                print('NP', f.relative_to(NP), im.size, 'mode='+im.mode)
        except Exception as e:
            print('ERR NP', f, e)
else:
    print('Normalized preview aspect dir not found')
