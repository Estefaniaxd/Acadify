import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE '%invitation%';"))
tablas = [row[0] for row in result]
print(f"Tablas con 'invitation': {tablas}")

# También verificar todas las tablas
result2 = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"))
todas = [row[0] for row in result2]
print(f"\nTotal de tablas: {len(todas)}")
print(f"Primeras 10: {todas[:10]}")

db.close()
