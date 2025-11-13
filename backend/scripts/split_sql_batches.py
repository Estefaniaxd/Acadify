#!/usr/bin/env python3
"""Dividir un SQL con múltiples transacciones (BEGIN...COMMIT) en lotes.

Útil para aplicar updates en batches pequeños y seguros.

Uso:
  python backend/scripts/split_sql_batches.py --in backend/scripts/avatar_normalize_output/avatar_normalize_apply_avatar_asset.sql --out-dir backend/scripts/avatar_normalize_output/batches --size 50

El script crea archivos batch_001.sql, batch_002.sql, ... cada uno conteniendo hasta `size` transacciones.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import textwrap


def split_into_batches(src: Path, out_dir: Path, size: int) -> int:
    content = src.read_text(encoding="utf-8")

    # Split by '\n\n' boundaries between transactions (we generated BEGIN; ... COMMIT;\n\n)
    parts = [p.strip() for p in content.split('\n\n') if p.strip()]

    # Rebuild transactions: keep parts that start with BEGIN or comments
    txs = []
    current = []
    for p in parts:
        if p.upper().startswith("BEGIN;"):
            if current:
                txs.append('\n\n'.join(current).strip())
            current = [p]
        else:
            current.append(p)
    if current:
        txs.append('\n\n'.join(current).strip())

    out_dir.mkdir(parents=True, exist_ok=True)
    batch_count = 0
    for i in range(0, len(txs), size):
        batch_count += 1
        chunk = txs[i : i + size]
        out_file = out_dir / f"batch_{batch_count:03d}.sql"
        out_file.write_text('\n\n'.join(chunk) + '\n', encoding="utf-8")

    return batch_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_sql", required=True)
    parser.add_argument("--out-dir", dest="out_dir", required=True)
    parser.add_argument("--size", type=int, default=50, help="Number of transactions per batch")
    args = parser.parse_args()

    src = Path(args.in_sql)
    out = Path(args.out_dir)
    if not src.exists():
        raise SystemExit(f"Input SQL not found: {src}")

    n = split_into_batches(src, out, args.size)
    print(f"Wrote {n} batch files to {out}")


if __name__ == "__main__":
    main()
