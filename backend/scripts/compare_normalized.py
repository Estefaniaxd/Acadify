#!/usr/bin/env python3
from PIL import Image
from pathlib import Path

assets=Path('/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/static/assets')
norm=Path('/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/static/normalized_preview')

changes=[]
for cat in norm.iterdir():
    if not cat.is_dir():
        continue
    for p in cat.glob('*.png'):
        orig=assets/ cat.name / p.name
        if not orig.exists():
            changes.append((str(orig), 'MISSING_ORIG', p.stat().st_size))
            continue
        with Image.open(orig) as o, Image.open(p) as n:
            if o.size!=n.size:
                changes.append((str(orig), o.size, n.size))

print(f'Total candidates: {len(changes)}')
for i,c in enumerate(changes[:200],1):
    print(i,c)
