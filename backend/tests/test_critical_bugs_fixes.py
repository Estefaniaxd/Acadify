"""
Tests para verificar que los dos bugs críticos están arreglados:
1. Archivos desaparecen después de recargar página
2. Respuestas aparecen como mensajes nuevos (no anidados)
"""

import pytest
import json
from uuid import uuid4
from datetime import UTC, datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.models.base import Base
from src.models.users.usuario import Usuario, RolUsuario, EstadoUsuario
from src.models.academico.curso import Curso
from src.models.academico.institucion import Institucion
from src.models.communication.comentario import Comentario, TipoComentario
from src.models.academico.archivo_curso import ArchivoCurso
from src.services.academic.comentario_service import ComentarioService


@pytest.fixture
def db() -> Session:
    """Crea una base de datos SQLite en memoria para tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def setup_data(db: Session):
    """Crea datos base: institución, curso, usuario."""
    # Crear institución
    institucion = Institucion(
        institucion_id="inst-001",
        nombre="Universidad Test",
        email="test@univ.edu",
        ciudad="Bogotá",
        pais="Colombia",
        estado=EstadoUsuario.activo,
        fecha_creacion=datetime.now(UTC),
    )
    db.add(institucion)

    # Crear usuario
    usuario = Usuario(
        usuario_id="usr-001",
        email="docente@test.com",
        nombres="Juan",
        apellidos="Pérez",
        rol=RolUsuario.docente,
        estado=EstadoUsuario.activo,
        fecha_creacion=datetime.now(UTC),
        institucion_id="inst-001",
    )
    db.add(usuario)

    # Crear curso
    curso = Curso(
        curso_id="cur-001",
        nombre="Matemáticas 101",
        descripcion="Curso de matemáticas básicas",
        docente_id="usr-001",
        institucion_id="inst-001",
        estado=EstadoUsuario.activo,
        fecha_creacion=datetime.now(UTC),
    )
    db.add(curso)

    db.commit()
    return {"institucion": institucion, "usuario": usuario, "curso": curso}


def test_archivos_persisten_despues_de_recargar(db: Session, setup_data):
    """
    BUG #1: Archivos desaparecen después de recargar página.
    
    Test: 
    1. Crear archivo en archivos_curso table
    2. Crear comentario con ese archivo
    3. Simular "recargar" obteniendo el comentario nuevamente
    4. Verificar que el archivo sigue ahí
    """
    print("\n" + "="*80)
    print("TEST 1: Archivos persisten después de recargar")
    print("="*80)

    usuario = setup_data["usuario"]
    curso_id = setup_data["curso"].curso_id

    # PASO 1: Crear archivo en DB (simular upload)
    archivo_id = str(uuid4())
    archivo = ArchivoCurso(
        archivo_id=archivo_id,
        nombre="documento.pdf",
        url="/uploads/documento.pdf",
        tamaño=102400,
        tipo="application/pdf",
        curso_id=curso_id,
        usuario_id=usuario.usuario_id,
        fecha_subida=datetime.now(UTC),
    )
    db.add(archivo)
    db.commit()
    print(f"✅ Archivo creado: {archivo_id}")

    # PASO 2: Crear comentario CON ese archivo
    archivos_adjuntos = [{"archivo_id": archivo_id}]
    comentario = ComentarioService.crear_comentario(
        db=db,
        curso_id=str(curso_id),
        contenido="Este es un comentario con archivo",
        usuario=usuario,
        tipo=TipoComentario.comentario,
        archivos_adjuntos=archivos_adjuntos,
    )
    print(f"✅ Comentario creado: {comentario['id']}")
    print(f"   Archivos en comentario (al crear): {comentario.get('archivos_adjuntos', [])}")

    # PASO 3: Simular "recargar página" - obtener comentarios del curso
    comentarios_recarados = ComentarioService.obtener_comentarios_curso(
        db=db,
        curso_id=str(curso_id),
        usuario=usuario,
    )
    print(f"✅ Comentarios recargados: {len(comentarios_recarados['data'])} comentarios")

    # PASO 4: Verificar que el archivo sigue ahí
    assert len(comentarios_recarados["data"]) > 0, "No se encontraron comentarios"
    comentario_recargado = comentarios_recarados["data"][0]

    print(f"\n🔍 Comentario recargado:")
    print(f"   - ID: {comentario_recargado['id']}")
    print(f"   - Contenido: {comentario_recargado['contenido']}")
    print(f"   - Archivos: {comentario_recargado.get('archivos_adjuntos', [])}")

    # ASSERTION CRÍTICA
    archivos_recargados = comentario_recargado.get("archivos_adjuntos", [])
    assert len(archivos_recargados) > 0, (
        "❌ BUG #1: Archivo DESAPARECIÓ después de recargar. "
        f"Esperado 1 archivo, encontrado {len(archivos_recargados)}"
    )
    assert archivos_recargados[0]["archivo_id"] == archivo_id, (
        f"❌ ID de archivo incorrecto. Esperado {archivo_id}, "
        f"encontrado {archivos_recargados[0].get('archivo_id')}"
    )

    print("\n✅ TEST PASADO: Archivos persisten después de recargar")


def test_respuestas_aparecen_anidadas_despues_recargar(db: Session, setup_data):
    """
    BUG #2: Respuestas aparecen como mensajes nuevos (no anidados).
    
    Test:
    1. Crear comentario padre
    2. Crear respuesta (comentario con comentario_padre_id)
    3. Simular "recargar" obteniendo comentarios
    4. Verificar que la respuesta aparece en array respuestas, no como comentario raíz
    """
    print("\n" + "="*80)
    print("TEST 2: Respuestas aparecen anidadas (no como nuevos mensajes)")
    print("="*80)

    usuario = setup_data["usuario"]
    curso_id = setup_data["curso"].curso_id

    # PASO 1: Crear comentario PADRE
    comentario_padre = ComentarioService.crear_comentario(
        db=db,
        curso_id=str(curso_id),
        contenido="Comentario padre",
        usuario=usuario,
        tipo=TipoComentario.comentario,
    )
    comentario_padre_id = comentario_padre["id"]
    print(f"✅ Comentario padre creado: {comentario_padre_id}")

    # PASO 2: Crear RESPUESTA (comentario hijo)
    respuesta = ComentarioService.crear_comentario(
        db=db,
        curso_id=str(curso_id),
        contenido="Esta es una respuesta",
        usuario=usuario,
        tipo=TipoComentario.comentario,
        comentario_padre_id=comentario_padre_id,  # ← KEY: Indicar que es respuesta
    )
    respuesta_id = respuesta["id"]
    print(f"✅ Respuesta creada: {respuesta_id}")
    print(f"   comentario_padre_id enviado: {comentario_padre_id}")

    # PASO 3: Simular "recargar página" - obtener comentarios
    comentarios_recarados = ComentarioService.obtener_comentarios_curso(
        db=db,
        curso_id=str(curso_id),
        usuario=usuario,
    )
    print(f"✅ Comentarios recargados: {len(comentarios_recarados['data'])} comentarios raíz")

    # PASO 4: Verificar estructura
    # Debería haber SOLO 1 comentario raíz (el padre)
    # Y la respuesta debería estar dentro del array "respuestas" del padre
    
    comentarios_raiz = comentarios_recarados["data"]
    
    print(f"\n🔍 Análisis de comentarios recargados:")
    print(f"   - Total de comentarios raíz: {len(comentarios_raiz)}")
    
    if len(comentarios_raiz) == 0:
        # Si no hay comentarios raíz, algo está MUY mal
        assert False, (
            "❌ No se encontraron comentarios raíz. "
            "El padre debería estar en la raíz"
        )
    
    if len(comentarios_raiz) == 2:
        # BUG #2: Ambos aparecen como raíz (respuesta NO está anidada)
        assert False, (
            "❌ BUG #2 DETECTADO: Se encontraron 2 comentarios raíz. "
            "La respuesta aparece como nuevo mensaje en lugar de estar anidada. "
            f"Comentarios: {[c['id'] for c in comentarios_raiz]}"
        )
    
    # Verificar que el padre tiene la respuesta anidada
    padre = comentarios_raiz[0]
    print(f"   - Comentario padre: {padre['id']}")
    print(f"   - Respuestas anidadas: {len(padre.get('respuestas', []))}")
    
    if padre['id'] == respuesta_id:
        # Padre y respuesta están invertidos
        padre, respuesta_row = respuesta_row, padre
    
    respuestas_anidadas = padre.get("respuestas", [])
    
    print(f"\n🔍 Estructura del comentario padre:")
    print(f"   - ID: {padre['id']}")
    print(f"   - Contenido: {padre['contenido']}")
    print(f"   - Respuestas anidadas: {len(respuestas_anidadas)}")
    for r in respuestas_anidadas:
        print(f"      • {r['id']}: {r['contenido']}")
    
    # ASSERTION CRÍTICA
    assert len(respuestas_anidadas) > 0, (
        "❌ BUG #2: Respuesta NO aparece en array 'respuestas' del padre. "
        f"Se encontraron {len(respuestas_anidadas)} respuestas anidadas."
    )
    
    assert any(r["id"] == respuesta_id for r in respuestas_anidadas), (
        f"❌ Respuesta {respuesta_id} no encontrada en respuestas del padre. "
        f"Respuestas encontradas: {[r['id'] for r in respuestas_anidadas]}"
    )
    
    print("\n✅ TEST PASADO: Respuestas aparecen correctamente anidadas")


def test_archivos_en_respuestas(db: Session, setup_data):
    """
    Test combinado: Verificar que archivos también persisten en RESPUESTAS.
    """
    print("\n" + "="*80)
    print("TEST 3: Archivos persisten en respuestas (test combinado)")
    print("="*80)

    usuario = setup_data["usuario"]
    curso_id = setup_data["curso"].curso_id

    # PASO 1: Crear comentario padre
    comentario_padre = ComentarioService.crear_comentario(
        db=db,
        curso_id=str(curso_id),
        contenido="Comentario padre",
        usuario=usuario,
    )
    comentario_padre_id = comentario_padre["id"]

    # PASO 2: Crear archivo para respuesta
    archivo_id = str(uuid4())
    archivo = ArchivoCurso(
        archivo_id=archivo_id,
        nombre="respuesta.pdf",
        url="/uploads/respuesta.pdf",
        tamaño=51200,
        tipo="application/pdf",
        curso_id=curso_id,
        usuario_id=usuario.usuario_id,
        fecha_subida=datetime.now(UTC),
    )
    db.add(archivo)
    db.commit()

    # PASO 3: Crear respuesta CON archivo
    respuesta = ComentarioService.crear_comentario(
        db=db,
        curso_id=str(curso_id),
        contenido="Respuesta con documento",
        usuario=usuario,
        comentario_padre_id=comentario_padre_id,
        archivos_adjuntos=[{"archivo_id": archivo_id}],
    )
    respuesta_id = respuesta["id"]

    # PASO 4: Recargar comentarios
    comentarios_recarados = ComentarioService.obtener_comentarios_curso(
        db=db,
        curso_id=str(curso_id),
        usuario=usuario,
    )

    # PASO 5: Verificar
    padre = comentarios_recarados["data"][0]
    respuestas_anidadas = padre.get("respuestas", [])
    
    print(f"✅ Padre: {padre['id']}")
    print(f"✅ Respuestas anidadas: {len(respuestas_anidadas)}")

    assert len(respuestas_anidadas) > 0, "Respuesta no encontrada"
    respuesta_recargada = respuestas_anidadas[0]
    
    archivos_en_respuesta = respuesta_recargada.get("archivos_adjuntos", [])
    print(f"✅ Archivos en respuesta: {len(archivos_en_respuesta)}")

    assert len(archivos_en_respuesta) > 0, (
        "❌ Archivo en respuesta DESAPARECIÓ después de recargar"
    )
    assert archivos_en_respuesta[0]["archivo_id"] == archivo_id, (
        f"❌ ID de archivo incorrecto en respuesta"
    )

    print("\n✅ TEST PASADO: Archivos persisten en respuestas")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
