"""Ver usuarios que violan el constraint"""
import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

result = db.execute(text('SELECT usuario_id, rol, username, correo_institucional FROM "Usuario" LIMIT 20'))
print('\nUsuarios en la BD:')
print(f"{'Rol':<15} {'Username':<20} {'Correo':<40}")
print("-" * 80)
for r in result:
    print(f"{str(r[1]):<15} {str(r[2]):<20} {str(r[3]):<40}")

# Ver específicamente los que violan
print("\n\nUsuarios que VIOLAN el constraint:")
sql_violacion = """
SELECT usuario_id, rol, username, correo_institucional
FROM "Usuario"
WHERE NOT (
    (rol = 'administrador' AND username IS NOT NULL AND correo_institucional IS NULL) 
    OR 
    (rol <> 'administrador' AND correo_institucional IS NOT NULL AND username IS NULL)
)
"""
result2 = db.execute(text(sql_violacion))
count = 0
for r in result2:
    count += 1
    print(f"  Rol: {r[1]}, username: {r[2]}, correo: {r[3]}")

print(f"\nTotal de usuarios que violan: {count}")

db.close()
