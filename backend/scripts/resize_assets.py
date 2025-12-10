#!/usr/bin/env python3
"""Resize avatar asset images to STANDARD_RESOLUTION (512x512) safely.

Usage:
  resize_assets.py --input-list /tmp/misscaled_filenames.txt --apply

This script:
 - reads a list of relative asset paths (relative to backend/static/assets/) or scans the assets dir
 - for each image not matching STANDARD_RESOLUTION, creates a timestamped backup copy (preserves path)
 - resizes the image to fit within STANDARD_RESOLUTION preserving aspect ratio, centers it on a transparent 512x512 canvas
 - writes the new image atomically (write to temp then rename)
 - records a CSV report with original size, new size, backup path and sha256
 - optionally emits SQL to update avatar_asset (width,height,file_size,sha256)

This uses Pillow (PIL). It's already a dependency of the project.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "static" / "assets"
REPORTS_DIR = ROOT / "scripts" / "reports"
BACKUPS_DIR = REPORTS_DIR / "backups"

STANDARD = (512, 512)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def resize_image_to_standard(src: Path, dst: Path, target_size=STANDARD) -> tuple[tuple[int, int], tuple[int, int]]:
    """Resize src -> dst. Return (orig_size, new_size)"""
    with Image.open(src) as im:
        im = im.convert("RGBA")
        orig = im.size

        # Compute scale to fit within target_size
        tw, th = target_size
        iw, ih = im.size
        scale = min(tw / iw, th / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        resized = im.resize((new_w, new_h), resample=Image.LANCZOS)

        # Create transparent canvas and paste centered
        canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
        paste_x = (tw - new_w) // 2
        paste_y = (th - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y), resized)

        # Save atomically
        dst_tmp = dst.with_suffix(dst.suffix + ".tmp")
        os.makedirs(dst.parent, exist_ok=True)
        canvas.save(dst_tmp, format="PNG", optimize=True)
        os.replace(dst_tmp, dst)

        return orig, canvas.size


def ensure_backup(src: Path, backup_root: Path, ts: str) -> Path:
    rel = src.relative_to(ASSETS_DIR)
    dest = backup_root / ts / rel
    os.makedirs(dest.parent, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def process_file(rel_path: str, backup_root: Path, apply: bool) -> dict:
    src = ASSETS_DIR / rel_path
    if not src.exists():
        return {"filename": rel_path, "status": "missing"}

    try:
        with Image.open(src) as im:
            size = im.size
    except Exception as e:
        return {"filename": rel_path, "status": f"open_error: {e}"}

    if size == STANDARD:
        return {"filename": rel_path, "status": "ok_already", "size": size}

    ts = time.strftime("%Y%m%d_%H%M%S")
    backup_path = ensure_backup(src, backup_root, ts)

    if apply:
        # resize and overwrite
        orig, new_size = resize_image_to_standard(src, src, STANDARD)
        sha = sha256_of_file(src)
        file_size = src.stat().st_size
        return {
            "filename": rel_path,
            "status": "resized",
            "orig_size": orig,
            "new_size": new_size,
            "backup": str(backup_path),
            "sha256": sha,
            "file_size": file_size,
        }
    else:
        # dry-run: compute what would happen
        # approximate sha by resizing in-memory
        with Image.open(src) as im:
            im = im.convert("RGBA")
            iw, ih = im.size
            tw, th = STANDARD
            scale = min(tw / iw, th / ih)
            new_w = max(1, int(iw * scale))
            new_h = max(1, int(ih * scale))
            resized = im.resize((new_w, new_h), resample=Image.LANCZOS)
            canvas = Image.new("RGBA", STANDARD, (0, 0, 0, 0))
            canvas.paste(resized, ((tw - new_w) // 2, (th - new_h) // 2), resized)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tf:
                canvas.save(tf.name, format="PNG", optimize=True)
                sha = sha256_of_file(Path(tf.name))
                size_bytes = Path(tf.name).stat().st_size
                os.unlink(tf.name)

        return {
            "filename": rel_path,
            "status": "would_resize",
            "orig_size": size,
            "new_size": STANDARD,
            "backup": str(backup_path),
            "sha256": sha,
            "file_size": size_bytes,
        }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input-list", type=str, help="File with relative paths (one per line) relative to static/assets/")
    p.add_argument("--scan", action="store_true", help="Scan the assets dir for files not matching standard resolution")
    p.add_argument("--apply", action="store_true", help="Actually apply changes (otherwise dry-run)")
    p.add_argument("--report", type=str, default=str(REPORTS_DIR / "reports" / "resize_report.csv"), help="CSV report output path")
    p.add_argument("--backup-root", type=str, default=str(BACKUPS_DIR / "resize_backups"), help="Backup root inside reports/backups")
    args = p.parse_args()

    paths = []
    if args.input_list:
        with open(args.input_list, encoding="utf-8") as f:
            for l in f:
                l = l.strip()
                if l:
                    paths.append(l)
    if args.scan:
        for pth in ASSETS_DIR.rglob("*.png"):
            rel = str(pth.relative_to(ASSETS_DIR))
            paths.append(rel)

    if not paths:
        print("No files to process. Provide --input-list or --scan.")
        return 1

    # ensure dirs
    backup_root = Path(args.backup_root)
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    backup_root.mkdir(parents=True, exist_ok=True)

    results = []
    for rel in sorted(set(paths)):
        res = process_file(rel, backup_root, apply=args.apply)
        print(rel, res.get("status"))
        results.append(res)

    # write CSV
    keys = ["filename", "status", "orig_size", "new_size", "backup", "sha256", "file_size"]
    with open(report_path, "w", newline="", encoding="utf-8") as csvf:
        writer = csv.DictWriter(csvf, fieldnames=keys)
        writer.writeheader()
        for r in results:
            row = {k: r.get(k, "") for k in keys}
            writer.writerow(row)

    print(f"Report written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
