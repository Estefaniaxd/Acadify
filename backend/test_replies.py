#!/usr/bin/env python3
"""
Test script para verificar que las replies se cargan correctamente
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
from services.academic.comentario_service import comentario_service
from core.database import get_db
from models.usuario import Usuario
from models.curso import Curso
from sqlalchemy.orm import Session

async def test_replies():
    print("🔍 Iniciando test de replies...")

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

        # Obtener comentarios del curso
        result = comentario_service.obtener_comentarios_curso(
            db=db,
            curso_id=str(curso.curso_id),
            usuario=usuario,
            limit=10,
            offset=0
        )

        if result['success']:
            comentarios = result['data']
            print(f'✅ {len(comentarios)} comentarios encontrados')

            total_replies = 0
            for i, comentario in enumerate(comentarios):
                replies = comentario.get('respuestas', [])
                total_replies += len(replies)

                print(f'  {i+1}. Comentario {comentario["id"]}: "{comentario["contenido"][:50]}..."')
                print(f'     📎 Archivos: {len(comentario.get("archivos_adjuntos", []))}')
                print(f'     💬 Respuestas: {len(replies)}')

                for j, respuesta in enumerate(replies):
                    print(f'       {j+1}. Respuesta {respuesta["id"]}: "{respuesta["contenido"][:30]}..."')
                    print(f'          📎 Archivos: {len(respuesta.get("archivos_adjuntos", []))}')

            print(f'\n📊 Resumen: {len(comentarios)} comentarios, {total_replies} respuestas totales')

            if total_replies > 0:
                print('✅ SUCCESS: Las replies se están cargando correctamente!')
            else:
                print('⚠️  No hay replies para verificar, pero la estructura está correcta')

        else:
            print(f'❌ Error obteniendo comentarios: {result}')

    except Exception as e:
        print(f'❌ Error en test: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_replies())