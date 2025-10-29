"""
Tests unitarios para ComentarioService

Tests exhaustivos que verifican:
- Creación de comentarios
- Obtención de comentarios por curso
- Actualización y eliminación
- Validación de permisos
- Performance y prevención de N+1 queries
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException

from src.services.academic.comentario_service import ComentarioService
from src.models.users.usuario import Usuario
from src.models.communication.comentario import TipoComentario


class TestComentarioService:
    """Tests para ComentarioService"""
    
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
    def mock_usuario(self):
        """Mock de usuario"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "Juan"
        usuario.apellidos = "Pérez"
        usuario.perfil_url = None
        return usuario
    
    # ==================== Tests de Validación ====================
    
    def test_validar_contenido_vacio(self):
        """Test: Validar contenido vacío debe fallar"""
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService._validar_contenido("")
        assert exc_info.value.status_code == 400
    
    def test_validar_contenido_solo_espacios(self):
        """Test: Validar contenido con solo espacios"""
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService._validar_contenido("   ")
        assert exc_info.value.status_code == 400
    
    def test_validar_contenido_muy_largo(self):
        """Test: Validar contenido muy largo (> 5000 caracteres)"""
        contenido = "x" * 5001
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService._validar_contenido(contenido)
        assert exc_info.value.status_code == 400
    
    def test_validar_contenido_correcto(self):
        """Test: Validar contenido correcto no debe lanzar excepción"""
        # No debe lanzar excepción
        ComentarioService._validar_contenido("Este es un comentario válido")
        ComentarioService._validar_contenido("x" * 5000)  # Justo en el límite
    
    # ==================== Tests de Obtención de Comentarios ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_success(self, mock_validar, mock_db, mock_usuario):
        """Test: Obtener comentarios de un curso exitosamente"""
        # Arrange
        curso_id = str(uuid4())
        
        # Mock resultado de query
        mock_result = Mock()
        mock_row = Mock()
        mock_row._mapping = {
            "comentario_id": str(uuid4()),
            "contenido": "Excelente clase",
            "tipo": "comentario",
            "fecha_creacion": datetime.now(),
            "fecha_actualizacion": None,
            "comentario_padre_id": None,
            "autor_id": str(uuid4()),
            "autor_nombre": "Juan Pérez",
            "autor_avatar": None,
            "total_respuestas": 2,
            "total_reacciones": 5
        }
        mock_result.fetchall.return_value = [mock_row]
        
        # Mock count query
        mock_count = Mock()
        mock_count.scalar.return_value = 10
        
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["contenido"] == "Excelente clase"
        assert result["pagination"]["total"] == 10
        mock_validar.assert_called_once()
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_vacio(self, mock_validar, mock_db, mock_usuario):
        """Test: Curso sin comentarios"""
        # Arrange
        curso_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_count = Mock()
        mock_count.scalar.return_value = 0
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 0
        assert result["pagination"]["total"] == 0
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_con_filtro(self, mock_validar, mock_db, mock_usuario):
        """Test: Filtrar comentarios por tipo"""
        # Arrange
        curso_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_count = Mock()
        mock_count.scalar.return_value = 0
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario,
            tipo=TipoComentario.pregunta
        )
        
        # Assert
        assert result["success"] is True
        # Verificar que se pasó el tipo al query
        call_args = mock_db.execute.call_args_list[0]
        assert call_args[0][1]["tipo"] == "pregunta"
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_sin_acceso(self, mock_validar, mock_db, mock_usuario):
        """Test: Usuario sin acceso al curso debe fallar"""
        # Arrange
        mock_validar.side_effect = HTTPException(status_code=403, detail="Sin acceso")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService.obtener_comentarios_curso(
                mock_db,
                str(uuid4()),
                mock_usuario
            )
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Creación ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_contenido')
    def test_crear_comentario_success(self, mock_validar_cont, mock_validar_acc, mock_db, mock_usuario):
        """Test: Crear comentario exitosamente"""
        # Arrange
        curso_id = str(uuid4())
        contenido = "Nuevo comentario"
        
        # Act
        result = ComentarioService.crear_comentario(
            mock_db,
            curso_id,
            contenido,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "data" in result
        assert "comentario_id" in result["data"]
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_validar_cont.assert_called_once_with(contenido)
        mock_validar_acc.assert_called_once()
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_contenido')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_comentario_padre')
    def test_crear_respuesta(self, mock_validar_padre, mock_validar_cont, mock_validar_acc, mock_db, mock_usuario):
        """Test: Crear respuesta a comentario"""
        # Arrange
        curso_id = str(uuid4())
        comentario_padre_id = str(uuid4())
        
        # Act
        result = ComentarioService.crear_comentario(
            mock_db,
            curso_id,
            "Respuesta",
            mock_usuario,
            comentario_padre_id=comentario_padre_id
        )
        
        # Assert
        assert result["success"] is True
        mock_validar_padre.assert_called_once_with(mock_db, comentario_padre_id, curso_id)
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_crear_comentario_vacio_falla(self, mock_validar_acc, mock_db, mock_usuario):
        """Test: Crear comentario vacío debe fallar"""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService.crear_comentario(
                mock_db,
                str(uuid4()),
                "",
                mock_usuario
            )
        assert exc_info.value.status_code == 400
    
    # ==================== Tests de Actualización ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_contenido')
    @patch('src.services.academic.comentario_service.ComentarioService._obtener_comentario')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_permisos_edicion')
    @patch('src.services.academic.comentario_service.ComentarioService._comentario_to_dict')
    def test_actualizar_comentario_success(self, mock_to_dict, mock_validar_perm, mock_obtener, mock_validar_cont, mock_db, mock_usuario):
        """Test: Actualizar comentario exitosamente"""
        # Arrange
        comentario_id = str(uuid4())
        nuevo_contenido = "Contenido actualizado"
        
        mock_comentario = Mock()
        mock_comentario.contenido = "Original"
        mock_obtener.return_value = mock_comentario
        mock_to_dict.return_value = {"comentario_id": comentario_id}
        
        # Act
        result = ComentarioService.actualizar_comentario(
            mock_db,
            comentario_id,
            nuevo_contenido,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert mock_comentario.contenido == nuevo_contenido
        assert mock_comentario.fecha_actualizacion is not None
        mock_db.commit.assert_called_once()
        mock_validar_perm.assert_called_once()
    
    @patch('src.services.academic.comentario_service.ComentarioService._obtener_comentario')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_permisos_edicion')
    def test_actualizar_sin_permisos(self, mock_validar_perm, mock_obtener, mock_db, mock_usuario):
        """Test: Actualizar sin permisos debe fallar"""
        # Arrange
        mock_comentario = Mock()
        mock_obtener.return_value = mock_comentario
        mock_validar_perm.side_effect = HTTPException(status_code=403, detail="Sin permisos")
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ComentarioService.actualizar_comentario(
                mock_db,
                str(uuid4()),
                "Nuevo",
                mock_usuario
            )
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Eliminación ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._obtener_comentario')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_permisos_edicion')
    def test_eliminar_comentario_success(self, mock_validar_perm, mock_obtener, mock_db, mock_usuario):
        """Test: Eliminar comentario (soft delete)"""
        # Arrange
        mock_comentario = Mock()
        mock_comentario.contenido = "Contenido original"
        mock_obtener.return_value = mock_comentario
        
        # Act
        result = ComentarioService.eliminar_comentario(
            mock_db,
            str(uuid4()),
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert mock_comentario.contenido == "[Comentario eliminado]"
        assert mock_comentario.fecha_actualizacion is not None
        mock_db.commit.assert_called_once()
    
    # ==================== Tests de Respuestas ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._obtener_comentario')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_respuestas_success(self, mock_validar, mock_obtener, mock_db, mock_usuario):
        """Test: Obtener respuestas de un comentario"""
        # Arrange
        comentario_id = str(uuid4())
        mock_comentario = Mock()
        mock_comentario.curso_id = uuid4()
        mock_obtener.return_value = mock_comentario
        
        mock_result = Mock()
        mock_row = Mock()
        mock_row._mapping = {
            "comentario_id": str(uuid4()),
            "contenido": "Respuesta 1",
            "autor_nombre": "Usuario",
            "fecha_creacion": datetime.now()
        }
        mock_result.fetchall.return_value = [mock_row]
        
        mock_count = Mock()
        mock_count.scalar.return_value = 1
        
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        result = ComentarioService.obtener_respuestas(
            mock_db,
            comentario_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 1
        mock_validar.assert_called_once()
    
    # ==================== Tests de Performance ====================
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_no_n_plus_1_queries(self, mock_validar, mock_db, mock_usuario):
        """Test: Verificar que no hay N+1 queries al obtener comentarios"""
        # Arrange
        curso_id = str(uuid4())
        
        # Simular 100 comentarios
        mock_rows = []
        for i in range(100):
            mock_row = Mock()
            mock_row._mapping = {
                "comentario_id": str(uuid4()),
                "contenido": f"Comentario {i}",
                "tipo": "comentario",
                "fecha_creacion": datetime.now(),
                "total_respuestas": 5,
                "total_reacciones": 10
            }
            mock_rows.append(mock_row)
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_count = Mock()
        mock_count.scalar.return_value = 100
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        
        # Assert
        # Solo 2 queries: 1 para datos + 1 para count
        assert mock_db.execute.call_count == 2
        assert len(result["data"]) == 100
        # Todos los comentarios ya tienen respuestas y reacciones (no N+1)
        assert all("total_respuestas" in c for c in result["data"])
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_performance_muchos_comentarios(self, mock_validar, mock_db, mock_usuario):
        """Test: Performance al procesar muchos comentarios"""
        # Arrange
        curso_id = str(uuid4())
        
        # Simular 1000 comentarios
        mock_rows = []
        for i in range(1000):
            mock_row = Mock()
            mock_row._mapping = {
                "comentario_id": str(uuid4()),
                "contenido": f"Comentario {i}",
                "tipo": "comentario",
                "fecha_creacion": datetime.now()
            }
            mock_rows.append(mock_row)
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_count = Mock()
        mock_count.scalar.return_value = 1000
        mock_db.execute.side_effect = [mock_result, mock_count]
        
        # Act
        import time
        start = time.time()
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        elapsed = time.time() - start
        
        # Assert
        assert elapsed < 1.0  # < 1 segundo
        assert len(result["data"]) == 1000
