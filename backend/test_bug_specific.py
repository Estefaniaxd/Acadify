#!/usr/bin/env python3
"""
Test específico para verificar el bug de archivos y replies
"""
import sys
import os
from sqlalchemy import text

# Ajustar sys.path para poder importar package 'src' cuando se ejecuta desde backend/
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add backend/src to sys.path (when running from backend/)
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

import asyncio
import logging
from services.academic.comentario_service import comentario_service
from src.api.deps import get_db
from src.models.usuario import Usuario
from src.models.curso import Curso
from sqlalchemy.orm import Session

# Configurar logging para ver los debug logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bug_files_and_replies():
    print("🔍 Iniciando test específico del bug...")

    try:
        db: Session = next(get_db())

        # Buscar un usuario de prueba
        usuario = db.query(Usuario).first()
        if not usuario:
            print('❌ No hay usuarios en la base de datos')
            return

        print(f'✅ Usuario encontrado: {usuario.usuario_id} - {usuario.nombres}')

        # Buscar un curso con comentarios
        curso = db.query(Curso).first()
        if not curso:
            print('❌ No hay cursos en la base de datos')
            return

        print(f'✅ Curso encontrado: {curso.curso_id} - {curso.nombre}')

        # Verificar datos en la base de datos directamente
        print("\n📊 VERIFICACIÓN DIRECTA EN BASE DE DATOS:")

        from sqlalchemy import text
        query = text("""
            SELECT
                c.comentario_id,
                c.contenido,
                c.comentario_padre_id,
                c.archivos_adjuntos,
                c.fecha_creacion,
                u.nombres || ' ' || u.apellidos as autor
            FROM "Comentario" c
            JOIN "Usuario" u ON c.autor_id = u.usuario_id
            WHERE c.curso_id = :curso_id
            ORDER BY c.fecha_creacion DESC
            LIMIT 10
        """)

        result = db.execute(query, {"curso_id": str(curso.curso_id)}).fetchall()

        print(f"📋 Comentarios encontrados en DB: {len(result)}")
        for i, row in enumerate(result):
            rdict = dict(row._mapping)
            print(f"  {i+1}. ID: {rdict['comentario_id']}")
            print(f"     Contenido: {rdict['contenido'][:50]}...")
            print(f"     Padre: {rdict['comentario_padre_id']}")
            print(f"     Archivos raw: {rdict['archivos_adjuntos']}")
            print(f"     Autor: {rdict['autor']}")
            print()

        # Ahora probar la función del servicio
        print("🔄 PROBANDO FUNCIÓN DEL SERVICIO:")

        result = comentario_service.obtener_comentarios_curso(
            db=db,
            curso_id=str(curso.curso_id),
            usuario=usuario,
            limit=10,
            offset=0
        )

        if result['success']:
            comentarios = result['data']
            print(f'✅ Servicio retornó {len(comentarios)} comentarios')

            for i, comentario in enumerate(comentarios):
                print(f'  {i+1}. Comentario {comentario["id"]}: "{comentario["contenido"][:50]}..."')
                print(f'     📎 Archivos adjuntos: {len(comentario.get("archivos_adjuntos", []))}')
                for j, archivo in enumerate(comentario.get("archivos_adjuntos", [])):
                    print(f'       📄 {j+1}. {archivo.get("nombre", "Sin nombre")} ({archivo.get("id", "?")})')

                respuestas = comentario.get('respuestas', [])
                print(f'     💬 Respuestas: {len(respuestas)}')

                for j, respuesta in enumerate(respuestas):
                    print(f'       💭 {j+1}. Respuesta {respuesta["id"]}: "{respuesta["contenido"][:30]}..."')
                    print(f'          📎 Archivos: {len(respuesta.get("archivos_adjuntos", []))}')

                print()

            # Verificar si hay replies que aparecen como comentarios raíz
            replies_como_raiz = [c for c in comentarios if c.get('comentario_padre_id')]
            if replies_como_raiz:
                print(f"🚨 ERROR: {len(replies_como_raiz)} replies aparecen como comentarios raíz!")
                for reply in replies_como_raiz:
                    print(f"   - Reply {reply['id']} con padre {reply.get('comentario_padre_id')} aparece como raíz")
            else:
                print("✅ OK: No hay replies apareciendo como comentarios raíz")

        else:
            print(f'❌ Error en servicio: {result}')

    except Exception as e:
        print(f'❌ Error en test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bug_files_and_replies())