"""
Tests unitarios para ReaccionService

Tests que verifican:
- Agregar reacciones
- Eliminar reacciones
- Actualizar reacciones
- Tipos de reacciones válidos
- Estadísticas
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from fastapi import HTTPException

from src.services.academic.reaccion_service import ReaccionService
from src.models.users.usuario import Usuario


class TestReaccionService:
    """Tests para ReaccionService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de sesión de base de datos"""
        db = Mock()
        db.execute = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    @pytest.fixture
    def mock_usuario(self):
        """Mock de usuario"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "Juan"
        usuario.apellidos = "Pérez"
        usuario.rol = "estudiante"
        return usuario
    
    # ==================== Tests de Constantes ====================
    
    def test_tipos_reaccion_validos(self):
        """Test: Tipos de reacción válidos definidos"""
        tipos = ReaccionService.TIPOS_REACCION_VALIDOS
        assert 'like' in tipos
        assert 'love' in tipos
        assert 'haha' in tipos
        assert 'wow' in tipos
        assert 'sad' in tipos
        assert 'angry' in tipos
        assert len(tipos) == 6
    
    # ==================== Tests de Agregar Reacción ====================
    
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_estadisticas')
    @patch('src.services.academic.reaccion_service.ReaccionService._crear_reaccion')
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_reaccion_existente')
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_agregar_reaccion_nueva(
        self, mock_validar, mock_obtener, mock_crear, mock_stats,
        mock_db, mock_usuario
    ):
        """Test: Agregar reacción nueva exitosamente"""
        # Arrange
        comentario_id = str(uuid4())
        mock_obtener.return_value = None  # No existe reacción previa
        mock_stats.return_value = {'like': 1, 'total': 1}
        
        # Act
        result = ReaccionService.agregar_reaccion(
            mock_db,
            comentario_id,
            'like',
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "agregada" in result["message"].lower() or "agrega" in result["message"].lower()
        mock_crear.assert_called_once()
    
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_estadisticas')
    @patch('src.services.academic.reaccion_service.ReaccionService._actualizar_reaccion')
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_reaccion_existente')
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_actualizar_reaccion_existente(
        self, mock_validar, mock_obtener, mock_actualizar, mock_stats,
        mock_db, mock_usuario
    ):
        """Test: Actualizar reacción existente"""
        # Arrange
        comentario_id = str(uuid4())
        reaccion_id = uuid4()
        mock_obtener.return_value = {'reaccion_id': reaccion_id}  # Ya existe
        mock_stats.return_value = {'love': 1, 'total': 1}
        
        # Act
        result = ReaccionService.agregar_reaccion(
            mock_db,
            comentario_id,
            'love',
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "actualiza" in result["message"].lower()
        mock_actualizar.assert_called_once()
    
    def test_agregar_reaccion_tipo_invalido(self, mock_db, mock_usuario):
        """Test: No se puede agregar reacción con tipo inválido"""
        # Arrange
        comentario_id = str(uuid4())
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReaccionService.agregar_reaccion(
                mock_db,
                comentario_id,
                'invalid_type',  # Tipo inválido
                mock_usuario
            )
        
        assert exc_info.value.status_code == 400
    
    # ==================== Tests de Eliminar Reacción ====================
    
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_estadisticas')
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_eliminar_reaccion_success(
        self, mock_validar, mock_stats,
        mock_db, mock_usuario
    ):
        """Test: Eliminar reacción exitosamente"""
        # Arrange
        comentario_id = str(uuid4())
        mock_result = Mock()
        mock_result.rowcount = 1  # Se eliminó 1 reacción
        mock_db.execute.return_value = mock_result
        mock_stats.return_value = {'total': 0}
        
        # Act
        result = ReaccionService.eliminar_reaccion(
            mock_db,
            comentario_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "eliminada" in result["message"].lower()
        mock_db.commit.assert_called_once()
    
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_eliminar_reaccion_no_existe(self, mock_validar, mock_db, mock_usuario):
        """Test: Intentar eliminar reacción que no existe"""
        # Arrange
        comentario_id = str(uuid4())
        mock_result = Mock()
        mock_result.rowcount = 0  # No se eliminó nada
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ReaccionService.eliminar_reaccion(
                mock_db,
                comentario_id,
                mock_usuario
            )
        
        assert exc_info.value.status_code == 404
    
    # ==================== Tests de Obtener Reacciones ====================
    
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_estadisticas')
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_obtener_reacciones_success(self, mock_validar, mock_stats, mock_db, mock_usuario):
        """Test: Obtener reacciones de un comentario"""
        # Arrange
        comentario_id = str(uuid4())
        mock_rows = [
            Mock(_mapping={'tipo_reaccion': 'like', 'usuario': 'Juan Pérez', 'es_mi_reaccion': False}),
            Mock(_mapping={'tipo_reaccion': 'love', 'usuario': 'María García', 'es_mi_reaccion': True})
        ]
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_db.execute.return_value = mock_result
        mock_stats.return_value = {'like': 1, 'love': 1, 'total': 2}
        
        # Act
        result = ReaccionService.obtener_reacciones(
            mock_db,
            comentario_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]["reacciones"]) == 2
        assert result["data"]["total"] == 2
    
    @patch('src.services.academic.reaccion_service.ReaccionService._obtener_estadisticas')
    @patch('src.services.academic.reaccion_service.ReaccionService._validar_acceso_comentario')
    def test_obtener_reacciones_vacio(self, mock_validar, mock_stats, mock_db, mock_usuario):
        """Test: Comentario sin reacciones"""
        # Arrange
        comentario_id = str(uuid4())
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        mock_stats.return_value = {'total': 0}
        
        # Act
        result = ReaccionService.obtener_reacciones(
            mock_db,
            comentario_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]["reacciones"]) == 0
        assert result["data"]["total"] == 0
    
    # ==================== Tests de Validación ====================
    
    def test_validar_tipo_reaccion_valido(self):
        """Test: Validar tipo de reacción válido"""
        # No debe lanzar excepción
        ReaccionService._validar_tipo_reaccion('like')
        ReaccionService._validar_tipo_reaccion('love')
        ReaccionService._validar_tipo_reaccion('haha')
    
    def test_validar_tipo_reaccion_invalido(self):
        """Test: Validar tipo de reacción inválido"""
        with pytest.raises(HTTPException) as exc_info:
            ReaccionService._validar_tipo_reaccion('invalid')
        assert exc_info.value.status_code == 400
