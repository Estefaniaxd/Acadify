#!/usr/bin/env python3
"""Normaliza y reporta assets de 'hair' (u otras categorías) para corregir problemas de escala/posicionamiento.

Genera:
 - report CSV con bbox/md5/dimensiones
 - carpeta de assets normalizados (canvas 512x512) centrando el contenido
 - archivo duplicates.txt con grupos por md5

Uso:
  python3 backend/scripts/fix_hair_assets_normalization.py --assets-dir backend/static/assets --out-dir backend/static/normalized --category hair --report out/report_hair.csv

Notas:
 - Esto centra el recorte no-transparente en un canvas 512x512 y escala para que ocupe hasta --target-box (por defecto 360px).
 - Algunos assets con offsets intencionales pueden necesitar ajuste manual; el reporte marca los que están muy descentrados.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from PIL import Image


@dataclass
class AssetInfo:
    path: Path
    md5: str
    width: int
    height: int
    bbox: Optional[Tuple[int, int, int, int]]  # left, upper, right, lower


def md5_of_file(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def analyze_asset(p: Path) -> AssetInfo:
    with Image.open(p) as img:
        img = img.convert("RGBA")
        alpha = img.split()[-1]
        bbox = alpha.getbbox()
        return AssetInfo(path=p, md5=md5_of_file(p), width=img.width, height=img.height, bbox=bbox)


def center_and_scale_asset(info: AssetInfo, out_path: Path, target_canvas: int = 512, target_box: int = 360) -> None:
    """Crea una versión normalizada: escala el bbox content a target_box y la centra en canvas target_canvas."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(info.path) as img:
        img = img.convert("RGBA")

        if info.bbox is None:
            # Nothing visible; copy as is into center
            canvas = Image.new("RGBA", (target_canvas, target_canvas), (0, 0, 0, 0))
            # place original scaled down if larger than target_box
            src_w, src_h = img.size
            scale = min(1.0, target_box / max(src_w, src_h))
            new_w = max(1, int(src_w * scale))
            new_h = max(1, int(src_h * scale))
            resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            paste_x = (target_canvas - new_w) // 2
            paste_y = (target_canvas - new_h) // 2
            canvas.paste(resized, (paste_x, paste_y), resized)
            canvas.save(out_path, "PNG", optimize=True)
            return

        left, upper, right, lower = info.bbox
        crop = img.crop((left, upper, right, lower))

        crop_w, crop_h = crop.size
        if crop_w == 0 or crop_h == 0:
            # fallback: copy centered
            center_and_scale_asset(AssetInfo(info.path, info.md5, info.width, info.height, None), out_path, target_canvas, target_box)
            return

        scale = min(target_box / crop_w, target_box / crop_h)
        new_w = max(1, int(crop_w * scale))
        new_h = max(1, int(crop_h * scale))

        resized = crop.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (target_canvas, target_canvas), (0, 0, 0, 0))
        paste_x = (target_canvas - new_w) // 2
        paste_y = (target_canvas - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y), resized)
        canvas.save(out_path, "PNG", optimize=True)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assets-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--category", default="hair")
    parser.add_argument("--report", required=True)
    parser.add_argument("--target-canvas", type=int, default=512)
    parser.add_argument("--target-box", type=int, default=360)
    args = parser.parse_args(argv)

    assets_dir = Path(args.assets_dir)
    out_dir = Path(args.out_dir)
    category = args.category
    report_file = Path(args.report)

    files = list(assets_dir.joinpath(category).rglob("*.png"))
    infos: List[AssetInfo] = []
    for p in files:
        try:
            info = analyze_asset(p)
            infos.append(info)
        except Exception as e:
            print(f"Error analyzing {p}: {e}")

    # Group duplicates by md5
    groups = defaultdict(list)
    for info in infos:
        groups[info.md5].append(info)

    # Ensure report directory exists before writing duplicates/report
    report_file.parent.mkdir(parents=True, exist_ok=True)
    duplicates_path = report_file.parent / "duplicates.txt"
    with duplicates_path.open("w") as fdup:
        for md5, items in groups.items():
            if len(items) > 1:
                fdup.write(md5 + "\n")
                for it in items:
                    fdup.write("  " + str(it.path) + "\n")
                fdup.write("\n")

    # Compute stats and median center offset to flag mis-centered
    rows = []
    for info in infos:
        w, h = info.width, info.height
        bbox = info.bbox
        if bbox:
            left, upper, right, lower = bbox
            bw = right - left
            bh = lower - upper
            bbox_cx = left + bw / 2.0
            bbox_cy = upper + bh / 2.0
            img_cx = w / 2.0
            img_cy = h / 2.0
            offset_x_pct = (bbox_cx - img_cx) / w * 100.0
            offset_y_pct = (bbox_cy - img_cy) / h * 100.0
        else:
            bw = bh = 0
            offset_x_pct = offset_y_pct = 0.0

        needs_manual = abs(offset_x_pct) > 10.0 or abs(offset_y_pct) > 10.0 or (bw == 0 and bh == 0)

        rows.append(
            {
                "path": str(info.path),
                "md5": info.md5,
                "width": w,
                "height": h,
                "bbox": str(info.bbox),
                "bbox_w": bw,
                "bbox_h": bh,
                "offset_x_pct": f"{offset_x_pct:.2f}",
                "offset_y_pct": f"{offset_y_pct:.2f}",
                "needs_manual": str(needs_manual),
            }
        )

    report_file.parent.mkdir(parents=True, exist_ok=True)
    with report_file.open("w", newline="") as csvfile:
        fieldnames = [
            "path",
            "md5",
            "width",
            "height",
            "bbox",
            "bbox_w",
            "bbox_h",
            "offset_x_pct",
            "offset_y_pct",
            "needs_manual",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Create normalized assets for non-manual or all (here we create for all but keep manual flag)
    for info in infos:
        rel = info.path.relative_to(assets_dir)
        out_path = out_dir.joinpath(rel)
        try:
            center_and_scale_asset(info, out_path, target_canvas=args.target_canvas, target_box=args.target_box)
        except Exception as e:
            print(f"Error normalizing {info.path}: {e}")

    print("Report written to:", report_file)
    print("Duplicates written to:", duplicates_path)
    print("Normalized assets written under:", out_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
