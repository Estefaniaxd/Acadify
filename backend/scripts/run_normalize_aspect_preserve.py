#!/usr/bin/env python3
"""Normalize images preserving aspect ratio and centering on transparent 512x512 canvas.
Writes to backend/static/normalized_preview_aspect/<category>/<file>.png
"""
from PIL import Image
from pathlib import Path

STANDARD = (512,512)
ROOT = Path('/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify')
ASSETS = ROOT / 'backend' / 'static' / 'assets'
OUT = ROOT / 'backend' / 'static' / 'normalized_preview_aspect'
OUT.mkdir(parents=True, exist_ok=True)

report = {'processed':0,'normalized':0,'skipped':0,'errors':[]}

for category_path in ASSETS.iterdir():
    if not category_path.is_dir() or category_path.name=='normalized':
        continue
    cat = category_path.name
    out_cat = OUT / cat
    out_cat.mkdir(parents=True, exist_ok=True)
    for p in category_path.glob('*.png'):
        report['processed'] += 1
        try:
            with Image.open(p) as img:
                img = img.convert('RGBA')
                if img.size == STANDARD:
                    report['skipped'] += 1
                    img.save(out_cat / p.name, 'PNG', optimize=True)
                    continue
                # compute scale preserving aspect ratio
                w,h = img.size
                tw,th = STANDARD
                scale = min(tw/w, th/h)
                new_w = max(1, int(w*scale))
                new_h = max(1, int(h*scale))
                resized = img.resize((new_w,new_h), Image.Resampling.LANCZOS)
                canvas = Image.new('RGBA', STANDARD, (0,0,0,0))
                paste_x = (tw - new_w)//2
                paste_y = (th - new_h)//2
                canvas.paste(resized, (paste_x,paste_y), resized)
                canvas.save(out_cat / p.name, 'PNG', optimize=True)
                report['normalized'] += 1
        except Exception as e:
            report['errors'].append(f"{p}: {e}")

print(report)
print('Wrote normalized to', OUT)
