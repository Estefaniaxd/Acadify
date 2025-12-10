#!/usr/bin/env python3
"""
Test script para verificar que el endpoint POST /api/cursos/tareas/{curso_id}/tareas funciona correctamente.

Este script simula lo que hace el formulario frontend:
1. Conecta a la BD
2. Crea datos de prueba (usuario, curso)
3. Invoca el endpoint de crear tarea
4. Verifica que la tarea se creó en la BD
5. Prueba casos de error
"""

import sys
import asyncio
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Agregar el backend al path
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.schemas.academic.tarea_schemas import TareaCreateRequest
from src.services.academic.tarea_service import tarea_service
from src.models.users.usuario import Usuario


async def test_crear_tarea():
    """Test 1: Crear tarea exitosamente"""
    print("\n" + "="*80)
    print("TEST 1: Crear Tarea Exitosamente")
    print("="*80)
    
    try:
        # Crear engine para testing
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True
        )
        
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_fetch=False)
        
        async with async_session() as db:
            # Crear usuario de prueba (docente)
            usuario_id = str(uuid4())
            docente_query = text("""
                INSERT INTO "Usuario" (usuario_id, email, nombres, apellidos, password_hash, rol)
                VALUES (:id, :email, :nombres, :apellidos, :password, :rol)
                ON CONFLICT(email) DO NOTHING
                RETURNING usuario_id
            """)
            
            result = await db.execute(docente_query, {
                "id": usuario_id,
                "email": f"docente_test_{uuid4()}@example.com",
                "nombres": "Docente",
                "apellidos": "Test",
                "password": "hashed_password",
                "rol": "docente"
            })
            
            docente = await result.fetchone()
            if not docente:
                print("❌ No se pudo crear usuario docente")
                return False
            
            docente_id = docente[0]
            print(f"✅ Usuario docente creado: {docente_id}")
            
            # Crear curso de prueba
            curso_id = str(uuid4())
            curso_query = text("""
                INSERT INTO cursos (curso_id, nombre, docente_id)
                VALUES (:id, :nombre, :docente_id)
                ON CONFLICT(curso_id) DO NOTHING
                RETURNING curso_id
            """)
            
            result = await db.execute(curso_query, {
                "id": curso_id,
                "nombre": "Curso Test",
                "docente_id": docente_id
            })
            
            curso = await result.fetchone()
            if not curso:
                print("❌ No se pudo crear curso")
                return False
            
            print(f"✅ Curso creado: {curso_id}")
            
            # Crear usuario simulado para el service
            usuario = type('Usuario', (), {
                'usuario_id': docente_id,
                'email': f'docente_test_{uuid4()}@example.com',
                'rol': 'docente'
            })()
            
            # Preparar datos de tarea
            titulo = "Test Tarea 1: Operaciones Matemáticas"
            descripcion = "Realiza los ejercicios del capítulo 3"
            fecha_limite = datetime.now(timezone.utc) + timedelta(days=7)
            puntos_max = 50.0
            tipo = "ejercicios"
            prioridad = "media"
            
            print(f"\n📝 Datos de la tarea:")
            print(f"   Título: {titulo}")
            print(f"   Descripción: {descripcion}")
            print(f"   Fecha Límite: {fecha_limite}")
            print(f"   Puntos Máx: {puntos_max}")
            print(f"   Tipo: {tipo}")
            print(f"   Prioridad: {prioridad}")
            
            # Invocar service
            print(f"\n🔄 Invocando tarea_service.crear_tarea()...")
            try:
                resultado = tarea_service.crear_tarea(
                    db=db,
                    curso_id=curso_id,
                    titulo=titulo,
                    descripcion=descripcion,
                    fecha_limite=fecha_limite,
                    puntos_max=puntos_max,
                    usuario=usuario,
                    tipo=tipo,
                    prioridad=prioridad
                )
                
                print(f"✅ Service retornó:")
                print(f"   Success: {resultado.get('success')}")
                print(f"   Message: {resultado.get('message')}")
                print(f"   Tarea ID: {resultado.get('data', {}).get('tarea_id')}")
                
                # Verificar en BD
                print(f"\n🔍 Verificando en base de datos...")
                verify_query = text("""
                    SELECT tarea_id, titulo, puntos_max, tipo, prioridad, descripcion
                    FROM tareas
                    WHERE curso_id = :curso_id AND titulo = :titulo
                    ORDER BY fecha_creacion DESC
                    LIMIT 1
                """)
                
                result = await db.execute(verify_query, {
                    "curso_id": curso_id,
                    "titulo": titulo
                })
                
                tarea = await result.fetchone()
                if tarea:
                    tarea_id, tit, pts, tip, prior, desc = tarea
                    print(f"✅ Tarea encontrada en BD:")
                    print(f"   ID: {tarea_id}")
                    print(f"   Título: {tit}")
                    print(f"   Puntos: {pts}")
                    print(f"   Tipo: {tip}")
                    print(f"   Prioridad: {prior}")
                    print(f"   Descripción: {desc}")
                    
                    # Validar valores
                    if pts == puntos_max and tip == tipo and prior == prioridad:
                        print("\n✅ TEST 1 PASSED: Tarea creada correctamente")
                        return True
                    else:
                        print("\n❌ TEST 1 FAILED: Valores no coinciden")
                        return False
                else:
                    print("❌ Tarea no encontrada en BD")
                    return False
                    
            except Exception as e:
                print(f"❌ Error en service: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_validacion_titulo_requerido():
    """Test 2: Validar que título es requerido"""
    print("\n" + "="*80)
    print("TEST 2: Validación - Título Requerido")
    print("="*80)
    
    try:
        # Verificar schema Pydantic
        from src.schemas.academic.tarea_schemas import TareaCreateRequest
        
        print("🔍 Intentando crear TareaCreateRequest sin título...")
        try:
            tarea = TareaCreateRequest(
                titulo="",  # Vacío - debe fallar
                fecha_limite=datetime.now(timezone.utc) + timedelta(days=1)
            )
            print("❌ TEST 2 FAILED: Se aceptó título vacío")
            return False
        except Exception as e:
            print(f"✅ Validación rechazó título vacío: {str(e)}")
            print("✅ TEST 2 PASSED: Título es requerido")
            return True
            
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return False


async def test_validacion_fecha():
    """Test 3: Validar que fecha_limite es requerida"""
    print("\n" + "="*80)
    print("TEST 3: Validación - Fecha Límite Requerida")
    print("="*80)
    
    try:
        print("🔍 Intentando crear TareaCreateRequest sin fecha_limite...")
        try:
            tarea = TareaCreateRequest(
                titulo="Test Tarea"
                # falta fecha_limite
            )
            print("❌ TEST 3 FAILED: Se aceptó sin fecha_limite")
            return False
        except Exception as e:
            print(f"✅ Validación rechazó sin fecha_limite: {str(e)}")
            print("✅ TEST 3 PASSED: Fecha límite es requerida")
            return True
            
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        return False


async def test_defaults():
    """Test 4: Verificar defaults de opcional fields"""
    print("\n" + "="*80)
    print("TEST 4: Valores Por Defecto")
    print("="*80)
    
    try:
        print("🔍 Creando TareaCreateRequest con mínimos campos...")
        tarea = TareaCreateRequest(
            titulo="Tarea Mínima",
            fecha_limite=datetime.now(timezone.utc) + timedelta(days=1)
        )
        
        print(f"✅ Tarea creada con defaults:")
        print(f"   Descripción: '{tarea.descripcion}' (default: '')")
        print(f"   Puntos Max: {tarea.puntos_max} (default: 100)")
        print(f"   Tipo: {tarea.tipo} (default: 'ejercicios')")
        print(f"   Prioridad: {tarea.prioridad} (default: 'media')")
        
        if (tarea.descripcion == "" and 
            tarea.puntos_max == 100 and 
            tarea.tipo == "ejercicios" and 
            tarea.prioridad == "media"):
            print("\n✅ TEST 4 PASSED: Defaults correctos")
            return True
        else:
            print("\n❌ TEST 4 FAILED: Defaults incorrectos")
            return False
            
    except Exception as e:
        print(f"❌ Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪 "*40)
    print("TESTS BACKEND - CREACIÓN DE TAREAS")
    print("🧪 "*40)
    
    results = []
    
    # Test 1: Happy path
    results.append(("Test 1: Crear tarea exitosamente", await test_crear_tarea()))
    
    # Test 2: Validación título
    results.append(("Test 2: Título requerido", await test_validacion_titulo_requerido()))
    
    # Test 3: Validación fecha
    results.append(("Test 3: Fecha límite requerida", await test_validacion_fecha()))
    
    # Test 4: Defaults
    results.append(("Test 4: Valores por defecto", await test_defaults()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests pasaron")
    
    if passed == len(results):
        print("\n🎉 TODOS LOS TESTS PASARON - PHASE 2 APROBADO")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
