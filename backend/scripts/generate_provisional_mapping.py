#!/usr/bin/env python3
from pathlib import Path

def main():
    rep = Path('backend/scripts/reports')
    dup = rep / 'duplicates.txt'
    out = rep / 'mapping_hair_provisional.csv'
    if not dup.exists():
        print('duplicates.txt not found at', dup)
        return 1

    lines = dup.read_text().splitlines()
    i = 0
    mappings = []
    while i < len(lines):
        md5 = lines[i].strip()
        i += 1
        paths = []
        while i < len(lines) and lines[i].startswith('  '):
            paths.append(lines[i].strip())
            i += 1
        if not paths:
            continue

        # preference: unisex > female > male > first
        def pick(paths):
            for pref in ('/unisex/', '/female/', '/male/'):
                for p in paths:
                    if pref in p:
                        return p
            return paths[0]

        canonical = pick(paths)
        for p in paths:
            if p != canonical:
                mappings.append((p, canonical))

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w') as fh:
        fh.write('original,canonical\n')
        for o, c in mappings:
            fh.write(f'{o},{c}\n')

    print('Wrote provisional mapping to', out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
