#!/usr/bin/env python3
"""
Script para probar el flujo completo de comentarios con archivos adjuntos.

Simula:
1. Subir un archivo
2. Crear un comentario con el archivo
3. Recargar comentarios y verificar que el archivo está ahí
"""

import sys
import json
from uuid import uuid4
from datetime import datetime, UTC

# Setup path
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from src.services.academic.comentario_service import ComentarioService
from src.services.academic.archivo_service import ArchivoService
from src.models.users.usuario import Usuario
from src.models.communication.comentario import Comentario
from src.db.session import SessionLocal
from sqlalchemy.orm import Session

def test_attachment_persistence():
    """Test completo de persistencia de archivos adjuntos."""
    db = SessionLocal()
    
    try:
        # 1. Crear usuario de prueba
        print("\n" + "="*60)
        print("1️⃣  CREANDO USUARIO DE PRUEBA")
        print("="*60)
        
        usuario = Usuario(
            usuario_id=uuid4(),
            nombres="Juan",
            apellidos="Pérez",
            correo_institucional="juan@test.com",
            rol="estudiante"
        )
        db.add(usuario)
        db.commit()
        print(f"✅ Usuario creado: {usuario.usuario_id}")
        
        # 2. Crear curso de prueba
        print("\n" + "="*60)
        print("2️⃣  CREANDO CURSO DE PRUEBA")
        print("="*60)
        
        from src.models.academic.curso import Curso
        curso_id = uuid4()
        curso = Curso(
            curso_id=curso_id,
            nombre="Test Course",
            codigo="TEST101",
            docente_id=usuario.usuario_id,
            institucion_id=uuid4()
        )
        db.add(curso)
        db.commit()
        print(f"✅ Curso creado: {curso_id}")
        
        # 3. Crear un archivo simulado
        print("\n" + "="*60)
        print("3️⃣  SUBIENDO ARCHIVO SIMULADO")
        print("="*60)
        
        # Simular archivo
        archivo_id = str(uuid4())
        print(f"📎 Archivo ID: {archivo_id}")
        print(f"📎 Archivo: documento-test.pdf")
        
        # Crear registro en archivos_curso
        from src.models.academic.archivo import ArchivoCurso
        archivo = ArchivoCurso(
            archivo_id=archivo_id,
            curso_id=curso_id,
            nombre_original="documento-test.pdf",
            url=f"/uploads/cursos/{curso_id}/documento-test.pdf",
            tipo="application/pdf",
            tamaño=2048,
            subido_por=usuario.usuario_id
        )
        db.add(archivo)
        db.commit()
        print(f"✅ Archivo registrado en BD")
        
        # 4. Crear comentario con archivo adjunto
        print("\n" + "="*60)
        print("4️⃣  CREANDO COMENTARIO CON ARCHIVO")
        print("="*60)
        
        archivos_adjuntos_json = json.dumps([{"archivo_id": archivo_id}])
        print(f"📝 Payload archivos_adjuntos: {archivos_adjuntos_json}")
        
        resultado_crear = ComentarioService.crear_comentario(
            db=db,
            curso_id=str(curso_id),
            contenido="Comentario de prueba con archivo",
            usuario=usuario,
            archivos_adjuntos=[{"archivo_id": archivo_id}]
        )
        
        if resultado_crear["success"]:
            comentario_id = resultado_crear["data"]["comentario_id"]
            print(f"✅ Comentario creado: {comentario_id}")
            print(f"📎 Archivos adjuntos devueltos: {json.dumps(resultado_crear['data'].get('archivos_adjuntos', []), indent=2)}")
        else:
            print(f"❌ Error creando comentario: {resultado_crear}")
            return False
        
        # 5. Recargar comentarios (simular recarga de página)
        print("\n" + "="*60)
        print("5️⃣  RECARGANDO COMENTARIOS (SIMULAR RECARGA DE PÁGINA)")
        print("="*60)
        
        resultado_cargar = ComentarioService.obtener_comentarios_curso(
            db=db,
            curso_id=str(curso_id),
            usuario=usuario
        )
        
        if resultado_cargar["success"]:
            comentarios = resultado_cargar["data"]
            print(f"✅ Comentarios cargados: {len(comentarios)}")
            
            # Buscar nuestro comentario
            mi_comentario = None
            for c in comentarios:
                if c.get("comentario_id") == comentario_id:
                    mi_comentario = c
                    break
            
            if mi_comentario:
                print(f"\n✅ ENCONTRADO EL COMENTARIO")
                print(f"   Contenido: {mi_comentario.get('contenido')}")
                archivos = mi_comentario.get('archivos_adjuntos', [])
                print(f"   Archivos adjuntos: {len(archivos)}")
                
                if archivos:
                    print(f"\n📎 ARCHIVOS ADJUNTOS:")
                    for arch in archivos:
                        print(f"   - ID: {arch.get('archivo_id')}")
                        print(f"   - Nombre: {arch.get('nombre')}")
                        print(f"   - URL: {arch.get('url')}")
                        print(f"   - Tamaño: {arch.get('tamaño')}")
                    print(f"\n✅ ÉXITO: Los archivos adjuntos PERSISTEN después de recargar")
                    return True
                else:
                    print(f"\n❌ PROBLEMA: No hay archivos adjuntos después de recargar")
                    print(f"   Raw archivos_adjuntos en BD: {mi_comentario.get('archivos_adjuntos')}")
                    return False
            else:
                print(f"\n❌ No se encontró el comentario {comentario_id}")
                print(f"   Comentarios en BD: {[c.get('comentario_id') for c in comentarios]}")
                return False
        else:
            print(f"❌ Error cargando comentarios: {resultado_cargar}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🧪 TEST DE PERSISTENCIA DE ARCHIVOS ADJUNTOS")
    success = test_attachment_persistence()
    sys.exit(0 if success else 1)
