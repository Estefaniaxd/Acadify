#!/usr/bin/env python3
"""Script de mantenimiento: valida y limpia archivos adjuntos en comentarios.

Reemplaza referencias a archivos que no existen en la tabla `archivos_curso`.
"""
import sys
import json
import os
from sqlalchemy import text

# Ajustar sys.path para poder importar package 'src' cuando se ejecuta desde backend/
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add backend/src to sys.path (when running from backend/)
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from src.api.deps import get_db


def main():
    db = next(get_db())
    try:
        rows = db.execute(text("SELECT comentario_id, archivos_adjuntos FROM \"Comentario\" WHERE archivos_adjuntos IS NOT NULL")).fetchall()
        print(f"Encontrados {len(rows)} comentarios con archivos_adjuntos no nulos")
        total_fixed = 0
        for row in rows:
            comentario_id = row[0]
            raw = row[1]
            try:
                archivos = raw if isinstance(raw, list) else json.loads(raw)
            except Exception:
                print(f"  - Comentario {comentario_id}: error parseando JSON, limpiando")
                archivos = []

            if not archivos:
                continue

            archivos_validos = []
            for a in archivos:
                archivo_id = None
                try:
                    archivo_id = a.get('archivo_id') or a.get('id')
                except Exception:
                    archivo_id = None
                if archivo_id:
                    res = db.execute(text("SELECT archivo_id FROM archivos_curso WHERE archivo_id = :archivo_id"), {"archivo_id": archivo_id}).fetchone()
                    if res:
                        archivos_validos.append({"archivo_id": str(res[0])})

            if len(archivos_validos) != len(archivos):
                # actualizar
                db.execute(text("UPDATE \"Comentario\" SET archivos_adjuntos = :json WHERE comentario_id = :cid"), {"json": json.dumps(archivos_validos), "cid": comentario_id})
                total_fixed += 1
                print(f"  - Comentario {comentario_id}: actualizado ({len(archivos)} -> {len(archivos_validos)})")

        db.commit()
        print(f"Terminado. Comentarios actualizados: {total_fixed}")
    except Exception as e:
        print('Error:', e)
    finally:
        db.close()


if __name__ == '__main__':
    main()
