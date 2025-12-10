#!/usr/bin/env python3
"""Simple synchronous normalizer to create normalized preview images without async deps.

Creates backend/static/normalized_preview/<category>/*.png with STANDARD_RESOLUTION.
"""
from PIL import Image
import os
from pathlib import Path

STANDARD = (512, 512)
ASSETS_DIR = Path(__file__).parents[1] / "static" / "assets"
OUT_DIR = Path(__file__).parents[1] / "static" / "normalized_preview"

os.makedirs(OUT_DIR, exist_ok=True)

report = {"processed": 0, "normalized": 0, "skipped": 0, "errors": []}

for category_path in ASSETS_DIR.iterdir():
    if not category_path.is_dir() or category_path.name == "normalized":
        continue
    cat = category_path.name
    out_cat = OUT_DIR / cat
    out_cat.mkdir(parents=True, exist_ok=True)

    for p in category_path.glob("*.png"):
        report["processed"] += 1
        try:
            with Image.open(p) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                if img.size == STANDARD:
                    report["skipped"] += 1
                    # Copy original to preview folder to keep structure
                    img.save(out_cat / p.name, "PNG", optimize=True)
                    continue
                # Resize preserving aspect ratio
                # Fit into STANDARD while keeping aspect ratio, then paste centered
                img_ratio = img.width / img.height
                target_ratio = STANDARD[0] / STANDARD[1]

                # Resize to STANDARD directly using LANCZOS
                resized = img.resize(STANDARD, Image.Resampling.LANCZOS)
                # Create transparent canvas and paste centered
                canvas = Image.new("RGBA", STANDARD, (0, 0, 0, 0))
                paste_x = (STANDARD[0] - resized.width) // 2
                paste_y = (STANDARD[1] - resized.height) // 2
                canvas.paste(resized, (paste_x, paste_y), resized)
                canvas.save(out_cat / p.name, "PNG", optimize=True)
                report["normalized"] += 1
        except Exception as e:
            report["errors"].append(f"{p}: {e}")

print(report)
print(f"Normalized preview images written to: {OUT_DIR}")
