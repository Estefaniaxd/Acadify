"""Test directo del constraint SQL"""
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

# Probar el constraint con SQL directo
sql = """
SELECT 
    (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) 
    OR (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL) as valido,
    rol,
    username,
    correo_institucional
FROM (
    SELECT 
        'coordinador'::text as rol,
        NULL::text as username,
        'test@test.com'::text as correo_institucional
) as test_data;
"""

result = db.execute(text(sql))
for row in result:
    print(f"Válido: {row[0]}, rol: {row[1]}, username: {row[2]}, correo: {row[3]}")

db.close()
