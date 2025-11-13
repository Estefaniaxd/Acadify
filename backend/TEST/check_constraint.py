"""Verificar el constraint"""
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

result = db.execute(text("SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = 'chk_login'"))
for r in result:
    print(f"Constraint: {r[0]}")
    print(f"Definition: {r[1]}")

db.close()
