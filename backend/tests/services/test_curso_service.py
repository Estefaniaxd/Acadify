"""
Tests unitarios para CursoService

Tests que verifican:
- Obtención de cursos por rol (estudiante, docente, coordinador)
- Validación de permisos
- Manejo de errores
- Performance
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

from src.services.academic.curso_service import CursoService
from src.models.users.usuario import Usuario


class TestCursoService:
    """Tests para CursoService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de sesión de base de datos"""
        db = Mock()
        db.execute = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        db.add = Mock()
        db.query = Mock()
        db.refresh = Mock()
        return db
    
    @pytest.fixture
    def mock_usuario_estudiante(self):
        """Mock de usuario estudiante"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "Juan"
        usuario.apellidos = "Pérez"
        usuario.rol = "estudiante"
        usuario.institucion_id = uuid4()
        return usuario
    
    @pytest.fixture
    def mock_usuario_docente(self):
        """Mock de usuario docente"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "María"
        usuario.apellidos = "García"
        usuario.rol = "docente"
        usuario.institucion_id = uuid4()
        return usuario
    
    @pytest.fixture
    def mock_usuario_coordinador(self):
        """Mock de usuario coordinador"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "Pedro"
        usuario.apellidos = "López"
        usuario.rol = "coordinador"
        usuario.institucion_id = uuid4()
        return usuario
    
    # ==================== Tests de Obtención por Estudiante ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_obtener_cursos_estudiante_success(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Estudiante obtiene sus cursos exitosamente"""
        # Arrange
        mock_cursos = [
            {
                "curso_id": str(uuid4()),
                "nombre": "Matemáticas",
                "descripcion": "Curso de matemáticas",
                "institucion_nombre": "Institución Test"
            },
            {
                "curso_id": str(uuid4()),
                "nombre": "Física",
                "descripcion": "Curso de física",
                "institucion_nombre": "Institución Test"
            }
        ]
        mock_get_cursos.return_value = mock_cursos
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["source"] == "student_enrollments"
        assert result["user_role"] == "estudiante"
        assert result["empty_state"] is False
        mock_get_cursos.assert_called_once()
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_obtener_cursos_estudiante_vacio(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Estudiante sin cursos inscritos"""
        # Arrange
        mock_get_cursos.return_value = []
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 0
        assert result["empty_state"] is True
        assert result["empty_message"] is not None
    
    # ==================== Tests de Obtención por Docente ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_docente')
    def test_obtener_cursos_docente_success(self, mock_get_cursos, mock_db, mock_usuario_docente):
        """Test: Docente obtiene sus cursos asignados"""
        # Arrange
        mock_cursos = [
            {
                "curso_id": str(uuid4()),
                "nombre": "Programación I",
                "descripcion": "Curso básico",
                "total_estudiantes": 30
            }
        ]
        mock_get_cursos.return_value = mock_cursos
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_docente
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["source"] == "teacher_assignments"
        assert result["user_role"] == "docente"
    
    # ==================== Tests de Obtención por Coordinador ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_coordinador')
    def test_obtener_cursos_coordinador_success(self, mock_get_cursos, mock_db, mock_usuario_coordinador):
        """Test: Coordinador obtiene todos los cursos de su institución"""
        # Arrange
        mock_cursos = [
            {"curso_id": str(uuid4()), "nombre": f"Curso {i}"}
            for i in range(10)
        ]
        mock_get_cursos.return_value = mock_cursos
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_coordinador
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 10
        assert result["source"] == "coordinator_institution"
        assert result["user_role"] == "coordinador"
    
    # ==================== Tests de Validación de Roles ====================
    
    def test_obtener_cursos_rol_invalido(self, mock_db):
        """Test: Usuario con rol inválido no puede acceder"""
        # Arrange
        usuario_invalido = Mock(spec=Usuario)
        usuario_invalido.rol = "rol_inexistente"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CursoService.obtener_cursos_usuario(
                mock_db,
                usuario_invalido
            )
        
        assert exc_info.value.status_code == 403
        assert "no tiene acceso" in str(exc_info.value.detail)
    
    # ==================== Tests de Manejo de Errores ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_obtener_cursos_db_error(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Error de base de datos se maneja correctamente"""
        # Arrange
        mock_get_cursos.side_effect = Exception("Database connection error")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CursoService.obtener_cursos_usuario(
                mock_db,
                mock_usuario_estudiante
            )
        
        assert exc_info.value.status_code == 500
        assert "Error interno" in str(exc_info.value.detail)
    
    # ==================== Tests de Paginación ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_obtener_cursos_con_paginacion(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Paginación funciona correctamente"""
        # Arrange
        mock_cursos = [{"curso_id": str(uuid4())} for _ in range(50)]
        mock_get_cursos.return_value = mock_cursos
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante,
            limit=50,
            offset=0
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 50
        # Verificar que se pasaron los parámetros de paginación
        mock_get_cursos.assert_called_once_with(mock_db, mock_usuario_estudiante, 50, 0)
    
    # ==================== Tests de Performance ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_performance_muchos_cursos(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Performance al procesar muchos cursos"""
        # Arrange
        mock_cursos = [
            {
                "curso_id": str(uuid4()),
                "nombre": f"Curso {i}",
                "descripcion": f"Descripción {i}"
            }
            for i in range(1000)
        ]
        mock_get_cursos.return_value = mock_cursos
        
        # Act
        import time
        start = time.time()
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante
        )
        elapsed = time.time() - start
        
        # Assert
        assert elapsed < 1.0  # < 1 segundo
        assert len(result["data"]) == 1000
    
    # ==================== Tests de Respuesta Vacía ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_empty_message')
    @patch('src.services.academic.curso_service.CursoService._get_cursos_docente')
    def test_mensaje_vacio_docente(self, mock_get_cursos, mock_get_message, mock_db, mock_usuario_docente):
        """Test: Mensaje apropiado cuando docente no tiene cursos"""
        # Arrange
        mock_get_cursos.return_value = []
        mock_get_message.return_value = "No tienes cursos asignados"
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_docente
        )
        
        # Assert
        assert result["empty_state"] is True
        assert result["empty_message"] == "No tienes cursos asignados"
        mock_get_message.assert_called_once_with("docente")
    
    # ==================== Tests de Estructura de Respuesta ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_estructura_respuesta_completa(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: La respuesta contiene todos los campos requeridos"""
        # Arrange
        mock_get_cursos.return_value = [{"curso_id": str(uuid4())}]
        
        # Act
        result = CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante
        )
        
        # Assert
        assert "success" in result
        assert "message" in result
        assert "data" in result
        assert "total" in result
        assert "source" in result
        assert "user_role" in result
        assert "empty_state" in result
        assert isinstance(result["data"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["empty_state"], bool)
    
    # ==================== Tests de Límites ====================
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_limite_default(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Límite por defecto es 100"""
        # Arrange
        mock_get_cursos.return_value = []
        
        # Act
        CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante
        )
        
        # Assert
        # Verificar que se usó el límite por defecto
        call_args = mock_get_cursos.call_args
        assert call_args[0][2] == 100  # limit
        assert call_args[0][3] == 0    # offset
    
    @patch('src.services.academic.curso_service.CursoService._get_cursos_estudiante')
    def test_limite_personalizado(self, mock_get_cursos, mock_db, mock_usuario_estudiante):
        """Test: Se puede especificar límite personalizado"""
        # Arrange
        mock_get_cursos.return_value = []
        
        # Act
        CursoService.obtener_cursos_usuario(
            mock_db,
            mock_usuario_estudiante,
            limit=25,
            offset=50
        )
        
        # Assert
        call_args = mock_get_cursos.call_args
        assert call_args[0][2] == 25   # limit
        assert call_args[0][3] == 50   # offset
