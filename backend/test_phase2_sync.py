#!/usr/bin/env python3
"""
Test script sincrónico para verificar que el endpoint de crear tareas funciona.
Este script usa la BD actual (sincrónico) sin problemas de async drivers.
"""

import sys
sys.path.insert(0, '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend')

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import settings
from src.schemas.academic.tarea_schemas import TareaCreateRequest
from src.services.academic.tarea_service import tarea_service


def test_create_task_in_database():
    """Test: Crear tarea en la BD y verificar que se persiste"""
    print("\n" + "="*80)
    print("TEST 1: Crear Tarea en Base de Datos")
    print("="*80)
    
    try:
        # Conectar a BD (sincrónico)
        db_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        print(f"🔌 Conectando a BD: {db_url.split('@')[1] if '@' in db_url else '...'}")
        
        engine = create_engine(db_url, echo=False)
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Crear usuario de prueba (docente)
        usuario_id = str(uuid4())
        email_test = f"docente_test_{uuid4()}@example.com"
        username_test = f"docente_test_{uuid4().hex[:8]}"
        
        print(f"\n👤 Creando usuario docente de prueba...")
        insert_usuario = text("""
            INSERT INTO "Usuario" (usuario_id, correo_institucional, username, nombres, apellidos, 
                                   tipo_documento, numero_documento, password_hash, rol)
            VALUES (:id, :correo, :username, :nombres, :apellidos, :tipo_doc, :num_doc, :password, :rol)
            ON CONFLICT(correo_institucional) DO NOTHING
            RETURNING usuario_id
        """)
        
        result = db.execute(insert_usuario, {
            "id": usuario_id,
            "correo": email_test,
            "username": username_test,
            "nombres": "Test",
            "apellidos": "Docente",
            "tipo_doc": "cc",  # Valores válidos: cc, ti, ce
            "num_doc": "12345678",
            "password": "hashed_pw",
            "rol": "docente"
        })
        
        docente = result.fetchone()
        if not docente:
            print("   ⚠️  Usuario ya existe o error al crear")
            docente_id = usuario_id
        else:
            docente_id = docente[0]
        
        print(f"   ✅ Usuario: {docente_id}")
        
        # Crear curso de prueba
        curso_id = str(uuid4())
        print(f"\n📚 Creando curso de prueba...")
        
        insert_curso = text("""
            INSERT INTO cursos (curso_id, nombre, docente_id)
            VALUES (:id, :nombre, :docente_id)
            ON CONFLICT(curso_id) DO NOTHING
            RETURNING curso_id
        """)
        
        result = db.execute(insert_curso, {
            "id": curso_id,
            "nombre": "Test Course",
            "docente_id": docente_id
        })
        
        curso = result.fetchone()
        if not curso:
            print("   ⚠️  Curso ya existe o error al crear")
        else:
            curso_id = curso[0]
        
        print(f"   ✅ Curso: {curso_id}")
        
        # Preparar datos de tarea
        titulo = f"Test Tarea {uuid4().hex[:8]}"
        descripcion = "Realizar los ejercicios del capítulo 3"
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
        
        # Crear usuario simulado
        usuario = type('Usuario', (), {
            'usuario_id': docente_id,
            'email': email_test,
            'rol': 'docente'
        })()
        
        # Invocar service
        print(f"\n🔄 Invocando tarea_service.crear_tarea()...")
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
        
        print(f"   ✅ Respuesta del service:")
        print(f"      Success: {resultado.get('success')}")
        print(f"      Message: {resultado.get('message')}")
        tarea_id = resultado.get('data', {}).get('tarea_id')
        print(f"      Tarea ID: {tarea_id}")
        
        # Verificar en BD
        print(f"\n🔍 Verificando en base de datos...")
        verify_query = text("""
            SELECT tarea_id, titulo, puntos_max, tipo, prioridad, descripcion
            FROM tareas
            WHERE curso_id = :curso_id AND titulo = :titulo
            ORDER BY fecha_creacion DESC
            LIMIT 1
        """)
        
        result = db.execute(verify_query, {
            "curso_id": curso_id,
            "titulo": titulo
        })
        
        tarea = result.fetchone()
        if tarea:
            tarea_id_bd, tit, pts, tip, prior, desc = tarea
            print(f"   ✅ Tarea encontrada en BD:")
            print(f"      ID: {tarea_id_bd}")
            print(f"      Título: {tit}")
            print(f"      Puntos: {pts}")
            print(f"      Tipo: {tip}")
            print(f"      Prioridad: {prior}")
            print(f"      Descripción: {desc[:50]}...")
            
            # Validar valores
            if pts == puntos_max and tip == tipo and prior == prioridad:
                print("\n✅ TEST 1 PASSED: Tarea creada y persistida correctamente")
                return True
            else:
                print("\n❌ TEST 1 FAILED: Valores no coinciden")
                print(f"   Esperado: pts={puntos_max}, tip={tipo}, prior={prioridad}")
                print(f"   Obtuve:  pts={pts}, tip={tip}, prior={prior}")
                return False
        else:
            print("   ❌ Tarea no encontrada en BD")
            return False
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_puntos_max_validation():
    """Test: Validar rango de puntos_max"""
    print("\n" + "="*80)
    print("TEST 2: Validación - Rango de Puntos")
    print("="*80)
    
    try:
        # Valores válidos
        print("🔍 Probando valores válidos...")
        values_ok = [1, 50, 100, 500, 1000]
        for val in values_ok:
            try:
                tarea = TareaCreateRequest(
                    titulo="Test",
                    fecha_limite=datetime.now(timezone.utc) + timedelta(days=1),
                    puntos_max=val
                )
                print(f"   ✅ {val} puntos: aceptado")
            except:
                print(f"   ❌ {val} puntos: rechazado (debe ser válido)")
                return False
        
        # Valores inválidos
        print("\n🔍 Probando valores inválidos...")
        values_bad = [0, -10, 1001, 5000]
        for val in values_bad:
            try:
                tarea = TareaCreateRequest(
                    titulo="Test",
                    fecha_limite=datetime.now(timezone.utc) + timedelta(days=1),
                    puntos_max=val
                )
                print(f"   ❌ {val} puntos: aceptado (debe ser rechazado)")
                return False
            except Exception as e:
                print(f"   ✅ {val} puntos: rechazado correctamente")
        
        print("\n✅ TEST 2 PASSED: Validación de puntos correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_schema_fields():
    """Test: Verificar que esquema tiene todos los campos correctos"""
    print("\n" + "="*80)
    print("TEST 3: Esquema TareaCreateRequest")
    print("="*80)
    
    try:
        print("🔍 Analizando esquema...")
        
        # Obtener información del schema
        from pydantic import Field
        
        schema_info = TareaCreateRequest.model_json_schema()
        required = schema_info.get('required', [])
        properties = schema_info.get('properties', {})
        
        print(f"\n   Campos requeridos: {required}")
        print(f"\n   Propiedades:")
        for name, prop in properties.items():
            tipo = prop.get('type', 'unknown')
            default = prop.get('default', 'N/A')
            print(f"      - {name}: {tipo} (default: {default})")
        
        # Validaciones esperadas
        expected_required = ['titulo', 'fecha_limite']
        expected_optional = ['descripcion', 'puntos_max', 'tipo', 'prioridad']
        
        if set(required) == set(expected_required):
            print(f"\n   ✅ Campos requeridos correctos")
        else:
            print(f"   ❌ Campos requeridos incorrectos")
            print(f"      Esperado: {expected_required}")
            print(f"      Obtuve: {required}")
            return False
        
        for field in expected_optional:
            if field in properties:
                print(f"   ✅ Campo opcional '{field}' presente")
            else:
                print(f"   ❌ Campo opcional '{field}' falta")
                return False
        
        print("\n✅ TEST 3 PASSED: Esquema correcto")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_enum_values():
    """Test: Verificar valores de enums"""
    print("\n" + "="*80)
    print("TEST 4: Valores de Enums")
    print("="*80)
    
    try:
        from src.enums.academic.tareas import PrioridadTarea, TipoTarea
        
        print("🔍 Validando PrioridadTarea...")
        prioridades = list(PrioridadTarea)
        print(f"   Valores: {[p.value for p in prioridades]}")
        
        print("\n🔍 Validando TipoTarea...")
        tipos = list(TipoTarea)
        print(f"   Valores: {[t.value for t in tipos]}")
        
        # Probar crear schema con diferentes valores
        for prior in prioridades:
            try:
                tarea = TareaCreateRequest(
                    titulo="Test",
                    fecha_limite=datetime.now(timezone.utc) + timedelta(days=1),
                    prioridad=prior
                )
                print(f"   ✅ Prioridad '{prior.value}' aceptada")
            except Exception as e:
                print(f"   ❌ Prioridad '{prior.value}' rechazada: {e}")
                return False
        
        print("\n✅ TEST 4 PASSED: Enums correctos")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪 "*40)
    print("TESTS FASE 2 - BACKEND VERIFICATION")
    print("🧪 "*40)
    
    results = []
    
    # Test 1: Create in database
    results.append(("Test 1: Crear tarea en BD", test_create_task_in_database()))
    
    # Test 2: Puntos validation
    results.append(("Test 2: Validación de puntos", test_puntos_max_validation()))
    
    # Test 3: Schema fields
    results.append(("Test 3: Esquema correcto", test_schema_fields()))
    
    # Test 4: Enum values
    results.append(("Test 4: Valores de enums", test_enum_values()))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS FASE 2")
    print("="*80)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests pasaron")
    
    if passed == len(results):
        print("\n🎉 TODOS LOS TESTS PASARON - PHASE 2 VERIFICACIÓN COMPLETA")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
