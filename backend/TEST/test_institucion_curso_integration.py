"""
Test de integración para verificar el sistema de Instituciones y Cursos

Valida:
- Creación de instituciones con dominio
- Vinculación de coordinadores
- Búsqueda por dominio
- Estadísticas de instituciones
- Relaciones con cursos y usuarios
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.core.config import settings
from src.models.academic.institucion import Institucion
from src.models.academic.curso import Curso
from src.models.users.usuario import Usuario
from src.services.academic.institucion_service import institucion_service
from src.schemas.academic.institucion import InstitucionCreate


# Configuración de base de datos de prueba
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    """Fixture para sesión de base de datos"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def coordinador_usuario(db_session):
    """Crea un usuario coordinador de prueba"""
    # Verificar si existe
    existing = db_session.execute(
        text("SELECT * FROM \"Usuario\" WHERE correo_institucional = :email"),
        {"email": "coord.test@example.edu"}
    ).fetchone()
    
    if existing:
        return db_session.query(Usuario).filter(
            Usuario.correo_institucional == "coord.test@example.edu",
        ).first()
    
    # Crear nuevo
    usuario = Usuario(
        nombres="Coordinador",
        apellidos="Test",
        correo_institucional="coord.test@example.edu",
        rol="coordinador",
        estado_cuenta="activo",
    )
    usuario.set_password("Test123!")
    
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


class TestInstitucionIntegration:
    """Tests de integración para instituciones"""
    
    def test_crear_institucion_con_dominio(self, db_session, coordinador_usuario):
        """Test: Crear institución con dominio automático"""
        
        # Datos de la institución
        institucion_data = InstitucionCreate(
            nombre="Universidad de Prueba",
            tipo="Universidad",
            direccion="Calle Falsa 123",
            telefono="1234567890",
            correo_institucional="info@uprueba.edu",
            # dominio se extrae automáticamente
        )
        
        # Crear institución
        resultado = institucion_service.crear_institucion(
            db_session,
            institucion_data,
            coordinador_usuario
        )
        
        assert resultado["success"] is True
        assert resultado["data"]["dominio"] == "uprueba.edu"
        assert resultado["data"]["coordinador_vinculado"] is True
        
        print("✅ Institución creada con dominio automático")
    
    def test_buscar_institucion_por_dominio(self, db_session):
        """Test: Buscar institución por dominio"""
        
        # Buscar institución existente (si hay alguna)
        dominio_test = "uprueba.edu"
        
        institucion = institucion_service.buscar_por_dominio(
            db_session,
            dominio_test
        )
        
        if institucion:
            assert institucion.dominio == dominio_test,
            assert institucion.estado == "activo"
            print(f"✅ Institución encontrada por dominio: {institucion.nombre}")
        else:
            print(f"ℹ️  No se encontró institución con dominio '{dominio_test}'")
    
    def test_obtener_instituciones_coordinador(self, db_session, coordinador_usuario):
        """Test: Obtener instituciones de un coordinador"""
        
        resultado = institucion_service.obtener_instituciones_coordinador(
            db_session,
            coordinador_usuario,
            incluir_estadisticas=True,
        )
        
        assert resultado["success"] is True
        assert "data" in resultado
        assert "total" in resultado
        
        if resultado["total"] > 0:
            primera_inst = resultado["data"][0]
            assert "institucion_id" in primera_inst
            assert "nombre" in primera_inst
            assert "total_cursos" in primera_inst
            print(f"✅ Coordinador tiene {resultado['total']} instituciones")
        else:
            print("ℹ️  Coordinador no tiene instituciones asignadas")
    
    def test_estadisticas_institucion(self, db_session, coordinador_usuario):
        """Test: Obtener estadísticas de institución"""
        
        # Primero obtener instituciones del coordinador
        instituciones = institucion_service.obtener_instituciones_coordinador(
            db_session,
            coordinador_usuario,
            incluir_estadisticas=False,
        )
        
        if instituciones["total"] == 0:
            print("ℹ️  No hay instituciones para obtener estadísticas")
            return
        
        institucion_id = instituciones["data"][0]["institucion_id"]
        
        # Obtener estadísticas
        resultado = institucion_service.obtener_estadisticas_institucion(
            db_session,
            institucion_id,
            coordinador_usuario
        )
        
        assert resultado["success"] is True
        stats = resultado["data"]
        
        assert "total_cursos" in stats
        assert "total_docentes" in stats
        assert "total_estudiantes" in stats
        assert "total_programas" in stats
        assert "total_coordinadores" in stats
        
        print("✅ Estadísticas de institución:")
        print(f"   - Cursos: {stats['total_cursos']}")
        print(f"   - Docentes: {stats['total_docentes']}")
        print(f"   - Estudiantes: {stats['total_estudiantes']}")
        print(f"   - Programas: {stats['total_programas']}")
        print(f"   - Coordinadores: {stats['total_coordinadores']}")


class TestCursoIntegration:
    """Tests de integración para cursos"""
    
    def test_verificar_estructura_curso(self, db_session):
        """Test: Verificar que la tabla Curso tiene todas las columnas necesarias"""
        
        query = text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public',
            AND table_name = 'Curso'
            ORDER BY ordinal_position
        """)
        
        columnas = db_session.execute(query).fetchall()
        
        # Columnas mínimas requeridas para el sistema
        columnas_requeridas = [
            'curso_id', 'nombre', 'institucion_id', 'codigo_acceso'
        ]
        
        columnas_encontradas = [col[0] for col in columnas]
        
        for col_requerida in columnas_requeridas:
            assert col_requerida in columnas_encontradas, \
                f"Columna requerida '{col_requerida}' no encontrada en tabla Curso"
        
        print("✅ Estructura de tabla Curso validada")
        print(f"   - Total columnas: {len(columnas)}")
        print(f"   - Columnas requeridas presentes: {', '.join(columnas_requeridas)}")
        print(f"   - Columnas completas: {', '.join(columnas_encontradas[:10])}...")
    
    def test_relaciones_curso_institucion(self, db_session):
        """Test: Verificar relación entre Curso e Institución"""
        
        query = text("""
            SELECT COUNT(*) as total_cursos
            FROM "Curso" c
            INNER JOIN "Institucion" i ON c.institucion_id = i.institucion_id
        """)
        
        resultado = db_session.execute(query).scalar()
        
        print(f"✅ Relación Curso-Institución verificada: {resultado} cursos vinculados")
    
    def test_curso_sin_institucion(self, db_session):
        """Test: Verificar si hay cursos sin institución (deberían ser 0)"""
        
        query = text("""
            SELECT COUNT(*) as cursos_huerfanos
            FROM "Curso" c
            WHERE c.institucion_id IS NULL
        """)
        
        resultado = db_session.execute(query).scalar()
        
        assert resultado == 0 or resultado is None, \
            f"Hay {resultado} cursos sin institución asignada"
        
        print("✅ No hay cursos huérfanos (sin institución)")


class TestRelacionesCompletas:
    """Tests de relaciones completas del sistema"""
    
    def test_cadena_institucion_curso_estudiante(self, db_session):
        """Test: Verificar cadena completa Institución -> Curso -> Grupo -> Estudiante"""
        
        query = text("""
            SELECT
                i.nombre as institucion,
                c.nombre as curso,
                g.nombre as grupo,
                COUNT(DISTINCT eg.estudiante_id) as estudiantes
            FROM "Institucion" i
            LEFT JOIN "Curso" c ON i.institucion_id = c.institucion_id,
            LEFT JOIN "GrupoCurso" gc ON c.curso_id = gc.curso_id,
            LEFT JOIN "Grupo" g ON gc.grupo_id = g.grupo_id,
            LEFT JOIN "EstudianteGrupo" eg ON g.grupo_id = eg.grupo_id
            GROUP BY i.nombre, c.nombre, g.nombre
            HAVING COUNT(DISTINCT eg.estudiante_id) > 0
            LIMIT 5
        """)
        
        resultado = db_session.execute(query).fetchall()
        
        if len(resultado) > 0:
            print("✅ Cadena completa verificada:")
            for row in resultado:
                print(f"   - {row[0]} > {row[1]} > {row[2]} ({row[3]} estudiantes)")
        else:
            print("ℹ️  No hay datos completos en la cadena (BD limpia)")
    
    def test_integridad_referencial(self, db_session):
        """Test: Verificar integridad referencial de todas las relaciones"""
        
        # Verificar FKs de Curso
        checks = [
            {
                "name": "Curso -> Institución",
                "query": """
                    SELECT COUNT(*) FROM "Curso" c
                    WHERE c.institucion_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM "Institucion" i
                        WHERE i.institucion_id = c.institucion_id,
                    )
                """
            },
            {
                "name": "Curso -> Programa",
                "query": """
                    SELECT COUNT(*) FROM "Curso" c
                    WHERE c.programa_id IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM "Programa" p
                        WHERE p.programa_id = c.programa_id,
                    )
                """
            },
            {
                "name": "InstitucionCoordinador -> Institución",
                "query": """
                    SELECT COUNT(*) FROM "InstitucionCoordinador" ic
                    WHERE NOT EXISTS (
                        SELECT 1 FROM "Institucion" i
                        WHERE i.institucion_id = ic.institucion_id,
                    )
                """
            },
            {
                "name": "InstitucionCoordinador -> Usuario",
                "query": """
                    SELECT COUNT(*) FROM "InstitucionCoordinador" ic
                    WHERE NOT EXISTS (
                        SELECT 1 FROM "Usuario" u
                        WHERE u.usuario_id = ic.coordinador_id,
                    )
                """
            }
        ]
        
        errores = []
        for check in checks:
            resultado = db_session.execute(text(check["query"])).scalar()
            if resultado and resultado > 0:
                errores.append(f"{check['name']}: {resultado} referencias rotas")
            else:
                print(f"✅ {check['name']}: OK")
        
        assert len(errores) == 0, \
            f"Errores de integridad referencial: {', '.join(errores)}"


def test_suite_completa():
    """
    Ejecuta la suite completa de tests de integración
    
    Uso:
        pytest TEST/test_institucion_curso_integration.py -v
    """
    print("\n" + "="*70)
    print("SUITE DE TESTS: INSTITUCIONES Y CURSOS")
    print("="*70 + "\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
