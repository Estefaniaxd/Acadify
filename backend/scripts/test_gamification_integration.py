"""
Script de prueba para la integración de gamificación con tareas

Este script simula el flujo completo de:
1. Crear una tarea
2. Estudiante entrega la tarea
3. Docente califica
4. Sistema otorga puntos automáticamente
5. Sistema verifica racha
6. Sistema detecta milestones

Uso:
    python scripts/test_gamification_integration.py
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.services.academic.tarea_service import TareaService
from src.models.users.usuario import Usuario
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# CONFIGURACIÓN
# ============================================

DATABASE_URL = "postgresql://postgres:password@localhost:5432/acadify"

# IDs de prueba (ajustar según tu BD)
CURSO_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
DOCENTE_ID = "d1d2d3d4-e5f6-7890-abcd-ef1234567891"
ESTUDIANTE_ID = "e1e2e3e4-e5f6-7890-abcd-ef1234567892"


# ============================================
# FUNCIONES DE SETUP
# ============================================

def crear_session():
    """Crea una sesión de base de datos"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


def crear_usuario_mock(usuario_id: str, rol: str) -> Usuario:
    """Crea un objeto Usuario mock para testing"""
    class UsuarioMock:
        def __init__(self, usuario_id, rol):
            self.usuario_id = usuario_id
            self.rol = rol
            self.nombres = "Usuario"
            self.apellidos = "Prueba"
            self.email = f"{rol}@test.com"
    
    return UsuarioMock(usuario_id, rol)


async def setup_datos_prueba(db):
    """Crea datos de prueba necesarios"""
    logger.info("🔧 Configurando datos de prueba...")
    
    # Crear tarea de prueba
    tarea_id = str(uuid4())
    
    query_tarea = text("""
        INSERT INTO tareas (
            tarea_id, clase_id, docente_id, titulo, descripcion,
            fecha_asignacion, fecha_limite, tipo, estado,
            puntos_base, puntos_bonificacion,
            habilitar_retroalimentacion_ia,
            fecha_creacion
        ) VALUES (
            :tarea_id, :clase_id, :docente_id, :titulo, :descripcion,
            :fecha_asignacion, :fecha_limite, :tipo, :estado,
            :puntos_base, :puntos_bonificacion,
            :habilitar_ia,
            :fecha_creacion
        )
        ON CONFLICT (tarea_id) DO NOTHING
        RETURNING tarea_id
    """)
    
    try:
        result = db.execute(query_tarea, {
            "tarea_id": tarea_id,
            "clase_id": CURSO_ID,
            "docente_id": DOCENTE_ID,
            "titulo": "Tarea de Prueba - Gamificación",
            "descripcion": "Esta es una tarea de prueba para verificar la integración de gamificación",
            "fecha_asignacion": datetime.now(timezone.utc) - timedelta(days=5),
            "fecha_limite": datetime.now(timezone.utc) + timedelta(days=5),
            "tipo": "ejercicios",
            "estado": "asignada",
            "puntos_base": 50,
            "puntos_bonificacion": 20,
            "habilitar_ia": False,
            "fecha_creacion": datetime.now(timezone.utc)
        })
        
        if result.rowcount > 0:
            logger.info(f"✅ Tarea creada: {tarea_id}")
        else:
            logger.info(f"ℹ️  Tarea ya existía: {tarea_id}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creando tarea: {e}")
        db.rollback()
        raise
    
    # Crear entrega de prueba
    entrega_id = str(uuid4())
    
    query_entrega = text("""
        INSERT INTO entregas_tareas (
            entrega_id, tarea_id, estudiante_id,
            archivo, estado, fecha_envio, es_tardia, intentos,
            fecha_creacion
        ) VALUES (
            :entrega_id, :tarea_id, :estudiante_id,
            :archivo, :estado, :fecha_envio, :es_tardia, :intentos,
            :fecha_creacion
        )
        ON CONFLICT (tarea_id, estudiante_id) DO UPDATE
        SET entrega_id = :entrega_id,
            estado = 'entregada',
            fecha_envio = :fecha_envio
        RETURNING entrega_id
    """)
    
    # Entrega 2 días después de asignación (40% del tiempo = bono rapidez)
    fecha_envio = datetime.now(timezone.utc) - timedelta(days=3)
    
    try:
        result = db.execute(query_entrega, {
            "entrega_id": entrega_id,
            "tarea_id": tarea_id,
            "estudiante_id": ESTUDIANTE_ID,
            "archivo": "https://storage.acadify.com/tareas/prueba.pdf",
            "estado": "entregada",
            "fecha_envio": fecha_envio,
            "es_tardia": False,
            "intentos": 1,
            "fecha_creacion": fecha_envio
        })
        
        if result.rowcount > 0:
            logger.info(f"✅ Entrega creada: {entrega_id}")
        else:
            logger.info(f"ℹ️  Entrega actualizada: {entrega_id}")
        
        db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error creando entrega: {e}")
        db.rollback()
        raise
    
    return tarea_id, entrega_id


# ============================================
# TESTS
# ============================================

async def test_calificacion_basica(db, entrega_id):
    """Test 1: Calificación básica con puntos"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Calificación Básica")
    logger.info("="*60)
    
    docente = crear_usuario_mock(DOCENTE_ID, "docente")
    
    resultado = await TareaService.calificar_entrega(
        db=db,
        entrega_id=entrega_id,
        calificacion=85,  # Buena calificación
        retroalimentacion="Buen trabajo! Muy bien estructurado.",
        usuario=docente
    )
    
    logger.info(f"\n📊 Resultado de Calificación:")
    logger.info(f"   Calificación: {resultado['data']['entrega']['calificacion']}/100")
    logger.info(f"   Estado: {resultado['data']['entrega']['estado']}")
    
    logger.info(f"\n💰 Puntos Otorgados:")
    puntos = resultado['data']['puntos']
    logger.info(f"   Total: {puntos['puntos_totales']} pts")
    logger.info(f"   Desglose:")
    logger.info(f"      - Calidad: {puntos['desglose']['puntos_calidad']} pts ({puntos['desglose']['nivel_calidad']})")
    logger.info(f"      - Rapidez: {puntos['desglose']['puntos_rapidez']} pts ({puntos['desglose']['nivel_rapidez']})")
    logger.info(f"      - Penalización tardía: {puntos['desglose']['penalizacion_tardia']} pts")
    logger.info(f"      - Penalización intentos: {puntos['desglose']['penalizacion_intentos']} pts")
    logger.info(f"   Puntos acumulados: {puntos['puntos_acumulados']} pts")
    logger.info(f"   Nivel: {puntos['nivel_usuario']}")
    
    logger.info(f"\n🔥 Racha:")
    racha = resultado['data']['racha']
    logger.info(f"   Racha actual: {racha['racha_actual']} días")
    logger.info(f"   Mejor racha: {racha['mejor_racha']} días")
    logger.info(f"   Puntos racha hoy: {racha['puntos_racha_hoy']} pts")
    
    if racha.get('milestone_alcanzado'):
        milestone = racha['milestone_alcanzado']
        logger.info(f"\n🏆 ¡MILESTONE ALCANZADO!")
        logger.info(f"   Tipo: {milestone.get('tipo', 'N/A')}")
        logger.info(f"   Nombre: {milestone.get('nombre', 'N/A')}")
        logger.info(f"   Puntos bonus: {milestone.get('puntos_otorgados', 0)} pts")
        if milestone.get('insignia_nombre'):
            logger.info(f"   Insignia: {milestone['insignia_nombre']}")
    
    logger.info(f"\n   Mensaje: {racha['mensaje']}")
    
    logger.info("\n✅ TEST 1 COMPLETADO")
    
    return resultado


async def test_calificacion_excelente(db, entrega_id):
    """Test 2: Calificación excelente (>= 90) para bono completo"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Calificación Excelente (Bono Completo)")
    logger.info("="*60)
    
    # Crear nueva entrega
    nueva_entrega_id = str(uuid4())
    tarea_id_query = text("""
        SELECT tarea_id FROM entregas_tareas WHERE entrega_id = :entrega_id
    """)
    tarea_id = db.execute(tarea_id_query, {"entrega_id": entrega_id}).scalar()
    
    query = text("""
        INSERT INTO entregas_tareas (
            entrega_id, tarea_id, estudiante_id,
            archivo, estado, fecha_envio, es_tardia, intentos,
            fecha_creacion
        ) VALUES (
            :entrega_id, :tarea_id, :estudiante_id,
            :archivo, :estado, :fecha_envio, :es_tardia, :intentos,
            :fecha_creacion
        )
    """)
    
    db.execute(query, {
        "entrega_id": nueva_entrega_id,
        "tarea_id": tarea_id,
        "estudiante_id": str(uuid4()),  # Otro estudiante
        "archivo": "https://storage.acadify.com/tareas/excelente.pdf",
        "estado": "entregada",
        "fecha_envio": datetime.now(timezone.utc) - timedelta(days=4),
        "es_tardia": False,
        "intentos": 1,
        "fecha_creacion": datetime.now(timezone.utc) - timedelta(days=4)
    })
    db.commit()
    
    docente = crear_usuario_mock(DOCENTE_ID, "docente")
    
    resultado = await TareaService.calificar_entrega(
        db=db,
        entrega_id=nueva_entrega_id,
        calificacion=95,  # Excelente!
        retroalimentacion="¡Excepcional! Supera todas las expectativas.",
        usuario=docente
    )
    
    puntos = resultado['data']['puntos']
    logger.info(f"\n💰 Calificación: 95/100")
    logger.info(f"   Nivel: {puntos['desglose']['nivel_calidad']}")
    logger.info(f"   Puntos totales: {puntos['puntos_totales']} pts")
    logger.info(f"   (Incluye bono de excelencia completo)")
    
    logger.info("\n✅ TEST 2 COMPLETADO")
    
    return resultado


async def test_calificacion_tardia(db, entrega_id):
    """Test 3: Calificación de entrega tardía (penalización)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Calificación con Penalización por Tardía")
    logger.info("="*60)
    
    # Crear entrega tardía
    tardia_entrega_id = str(uuid4())
    tarea_id_query = text("""
        SELECT tarea_id FROM entregas_tareas WHERE entrega_id = :entrega_id
    """)
    tarea_id = db.execute(tarea_id_query, {"entrega_id": entrega_id}).scalar()
    
    query = text("""
        INSERT INTO entregas_tareas (
            entrega_id, tarea_id, estudiante_id,
            archivo, estado, fecha_envio, es_tardia, intentos,
            fecha_creacion
        ) VALUES (
            :entrega_id, :tarea_id, :estudiante_id,
            :archivo, :estado, :fecha_envio, :es_tardia, :intentos,
            :fecha_creacion
        )
    """)
    
    db.execute(query, {
        "entrega_id": tardia_entrega_id,
        "tarea_id": tarea_id,
        "estudiante_id": str(uuid4()),  # Otro estudiante
        "archivo": "https://storage.acadify.com/tareas/tardia.pdf",
        "estado": "entregada",
        "fecha_envio": datetime.now(timezone.utc) + timedelta(days=2),  # Tardía!
        "es_tardia": True,
        "intentos": 1,
        "fecha_creacion": datetime.now(timezone.utc)
    })
    db.commit()
    
    docente = crear_usuario_mock(DOCENTE_ID, "docente")
    
    resultado = await TareaService.calificar_entrega(
        db=db,
        entrega_id=tardia_entrega_id,
        calificacion=80,  # Buena calificación pero tardía
        retroalimentacion="Buen trabajo, pero entregado tarde.",
        usuario=docente
    )
    
    puntos = resultado['data']['puntos']
    logger.info(f"\n💰 Calificación: 80/100")
    logger.info(f"   Puntos base: {puntos['desglose']['puntos_calidad']} pts")
    logger.info(f"   Penalización tardía: {puntos['desglose']['penalizacion_tardia']} pts ⚠️")
    logger.info(f"   Puntos totales: {puntos['puntos_totales']} pts")
    logger.info(f"   (Penalizado por entrega tardía)")
    
    logger.info("\n✅ TEST 3 COMPLETADO")
    
    return resultado


async def verificar_estado_gamificacion(db):
    """Verifica el estado actual de gamificación del estudiante"""
    logger.info("\n" + "="*60)
    logger.info("ESTADO DE GAMIFICACIÓN DEL ESTUDIANTE")
    logger.info("="*60)
    
    # Puntos totales
    query_puntos = text("""
        SELECT COALESCE(SUM(cantidad), 0) as total_puntos
        FROM historial_puntos
        WHERE usuario_id = :usuario_id
    """)
    
    puntos = db.execute(query_puntos, {"usuario_id": ESTUDIANTE_ID}).scalar()
    logger.info(f"\n💰 Puntos Totales: {puntos} pts")
    
    # Racha actual
    query_racha = text("""
        SELECT racha_actual, mejor_racha, fecha_ultimo_dia
        FROM "RachaUsuario"
        WHERE usuario_id = :usuario_id
    """)
    
    racha_row = db.execute(query_racha, {"usuario_id": ESTUDIANTE_ID}).fetchone()
    
    if racha_row:
        logger.info(f"\n🔥 Racha:")
        logger.info(f"   Actual: {racha_row[0]} días")
        logger.info(f"   Mejor: {racha_row[1]} días")
        logger.info(f"   Última actividad: {racha_row[2]}")
    else:
        logger.info(f"\n🔥 Sin racha activa")
    
    # Historial reciente
    query_historial = text("""
        SELECT tipo_evento, cantidad, razon, fecha_creacion
        FROM historial_puntos
        WHERE usuario_id = :usuario_id
        ORDER BY fecha_creacion DESC
        LIMIT 5
    """)
    
    historial = db.execute(query_historial, {"usuario_id": ESTUDIANTE_ID}).fetchall()
    
    if historial:
        logger.info(f"\n📜 Historial Reciente:")
        for row in historial:
            logger.info(f"   - {row[0]}: +{row[1]} pts - {row[2]} ({row[3]})")
    
    logger.info("\n" + "="*60)


# ============================================
# MAIN
# ============================================

async def main():
    """Función principal"""
    logger.info("\n" + "🎮"*30)
    logger.info("TEST DE INTEGRACIÓN: GAMIFICACIÓN + TAREAS")
    logger.info("🎮"*30 + "\n")
    
    db = crear_session()
    
    try:
        # Setup
        tarea_id, entrega_id = await setup_datos_prueba(db)
        
        # Test 1: Calificación básica
        await test_calificacion_basica(db, entrega_id)
        
        await asyncio.sleep(1)
        
        # Test 2: Calificación excelente
        await test_calificacion_excelente(db, entrega_id)
        
        await asyncio.sleep(1)
        
        # Test 3: Calificación tardía
        await test_calificacion_tardia(db, entrega_id)
        
        # Verificar estado final
        await verificar_estado_gamificacion(db)
        
        logger.info("\n" + "✅"*30)
        logger.info("TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        logger.info("✅"*30 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Error durante los tests: {e}", exc_info=True)
        
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
