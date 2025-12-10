#!/usr/bin/env python3
"""Generate dry-run SQL to:
1) map avatar_asset rows that start with female/ male/ unisex/ to clothes/<same>
2) detect duplicate images by sha256 on disk and propose canonical_path updates

Writes outputs to backend/scripts/reports/reports/
"""
from pathlib import Path
import csv
import hashlib
import psycopg2

ROOT=Path(__file__).resolve().parents[3]
ASSETS=ROOT/'backend/static/assets'
REPORTS=ROOT/'backend/scripts/reports/reports'
REPORTS.mkdir(parents=True,exist_ok=True)
ENV=ROOT/'backend/.env'
DBURL=None
if ENV.exists():
    for line in ENV.read_text().splitlines():
        if line.startswith('DATABASE_URL='):
            DBURL=line.split('=',1)[1].strip().strip('"')
            break
if not DBURL:
    raise SystemExit('DATABASE_URL not found in backend/.env')

conn=psycopg2.connect(DBURL)
cur=conn.cursor()

# 1) Prefix clothes mapping
cur.execute("SELECT id, filename FROM avatar_asset WHERE filename ~ '^(female|male|unisex)/' ORDER BY filename;")
rows=cur.fetchall()
map_rows=[]
for id_,fn in rows:
    candidate='clothes/'+fn
    if (ASSETS/candidate).exists():
        map_rows.append((id_,fn,candidate))

# write snapshot
snap=REPORTS/'preapply_prefix_clothes_snapshot.csv'
with snap.open('w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['id','filename'])
    for r in map_rows:
        w.writerow([r[0],r[1]])

# write SQL
sql_apply=REPORTS/'prefix_clothes_apply.sql'
sql_rb=REPORTS/'prefix_clothes_rollback.sql'
with sql_apply.open('w') as f:
    f.write('BEGIN;\n')
    for id_,old,new in map_rows:
        f.write("UPDATE avatar_asset SET filename = '{new}' WHERE id = '{id}';\n".format(new=new.replace("'","''"), id=id_))
    f.write('COMMIT;\n')
with sql_rb.open('w') as f:
    f.write('BEGIN;\n')
    for id_,old,new in map_rows:
        f.write("UPDATE avatar_asset SET filename = '{old}' WHERE id = '{id}';\n".format(old=old.replace("'","''"), id=id_))
    f.write('COMMIT;\n')

# 2) Detect duplicates by sha256 on disk
sha_map={}
for p in ASSETS.rglob('*.png'):
    try:
        h=hashlib.sha256(p.read_bytes()).hexdigest()
    except Exception:
        continue
    sha_map.setdefault(h,[]).append(p.relative_to(ASSETS).as_posix())

# query DB rows by filename to get ids and db sha
cur.execute("SELECT id, filename, sha256 FROM avatar_asset;")
db_rows=cur.fetchall()
sha_to_db={}
for id_,fn,sha in db_rows:
    if sha:
        sha_to_db.setdefault(sha,[]).append((id_,fn))

# find groups where disk sha has multiple paths or db has multiple rows
dup_groups=[]
for sha,paths in sha_map.items():
    if len(paths)>1 or (sha in sha_to_db and len(sha_to_db[sha])>1):
        dup_groups.append((sha,paths,sha_to_db.get(sha,[])))

# Prepare canonicalization plan: pick canonical path preferentially 'clothes/', then 'unisex', then 'female', then 'male', then lexicographic
canon_actions=[]
def rank(p):
    if p.startswith('clothes/'): return 0
    if p.startswith('unisex/'): return 1
    if p.startswith('female/'): return 2
    if p.startswith('male/'): return 3
    return 4

for sha, paths, dbrows in dup_groups:
    canon=sorted(paths, key=lambda x:(rank(x), x))[0]
    for id_,fn in dbrows:
        if fn!=canon:
            canon_actions.append((sha,canon,id_,fn))

# write dup plan
dup_plan=REPORTS/'duplicate_canonicalize_plan.csv'
with dup_plan.open('w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['sha256','canonical_path','id','filename'])
    for a in canon_actions:
        w.writerow(a)

# write SQL to set canonical_path
dup_sql=REPORTS/'duplicate_set_canonical_apply.sql'
dup_rb=REPORTS/'duplicate_set_canonical_rollback.sql'
with dup_sql.open('w') as f:
    f.write('BEGIN;\n')
    for sha,canon,id_,fn in canon_actions:
        f.write("UPDATE avatar_asset SET canonical_path = '{c}', sha256 = '{s}' WHERE id = '{id}';\n".format(c=canon.replace("'","''"), s=sha, id=id_))
    f.write('COMMIT;\n')
with dup_rb.open('w') as f:
    f.write('BEGIN;\n')
    for sha,canon,id_,fn in canon_actions:
        f.write("UPDATE avatar_asset SET canonical_path = NULL WHERE id = '{id}';\n".format(id=id_))
    f.write('COMMIT;\n')

print('WROTE snapshot:',snap)
print('WROTE apply SQL:',sql_apply)
print('WROTE rollback SQL:',sql_rb)
print('MAPPING_ROWS',len(map_rows))
print('DUP_GROUPS',len(dup_groups),'CANON_ACTIONS',len(canon_actions))

cur.close(); conn.close()
