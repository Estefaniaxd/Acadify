"""
Tests unitarios para InscripcionService

Tests que verifican:
- Inscripción por código
- Generación de códigos
- Validaciones de permisos
- Validaciones de institución
"""
import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.services.academic.inscripcion_service import InscripcionService
from src.models.users.usuario import Usuario


class TestInscripcionService:
    """Tests para InscripcionService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de sesión de base de datos"""
        db = Mock()
        db.execute = Mock()
        db.commit = Mock()
        db.rollback = Mock()
        return db
    
    @pytest.fixture
    def mock_estudiante(self):
        """Mock de usuario estudiante"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "Juan"
        usuario.apellidos = "Pérez"
        usuario.rol = "estudiante"
        usuario.institucion_id = uuid4()
        return usuario
    
    @pytest.fixture
    def mock_coordinador(self):
        """Mock de usuario coordinador"""
        usuario = Mock(spec=Usuario)
        usuario.usuario_id = uuid4()
        usuario.nombres = "María"
        usuario.apellidos = "García"
        usuario.rol = "coordinador"
        usuario.institucion_id = uuid4()
        return usuario
    
    # ==================== Tests de Inscripción por Código ====================
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._vincular_estudiante_grupo')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_o_crear_grupo')
    @patch('src.services.academic.inscripcion_service.InscripcionService._esta_inscrito')
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_misma_institucion')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_inscribir_por_codigo_success(
        self, mock_obtener_curso, mock_validar_inst, mock_esta_inscrito,
        mock_obtener_grupo, mock_vincular, mock_db, mock_estudiante
    ):
        """Test: Estudiante se inscribe exitosamente con código"""
        # Arrange
        codigo = "ABC12345"
        curso_id = str(uuid4())
        grupo_id = uuid4()
        
        mock_obtener_curso.return_value = {
            "curso_id": curso_id,
            "nombre": "Matemáticas 101"
        }
        mock_esta_inscrito.return_value = False
        mock_obtener_grupo.return_value = grupo_id
        
        # Act
        result = InscripcionService.inscribir_por_codigo(
            mock_db,
            codigo,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["curso_id"] == curso_id
        assert "mensaje" in result or "message" in result
        mock_vincular.assert_called_once()
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_inscribir_no_estudiante(self, mock_obtener_curso, mock_db, mock_coordinador):
        """Test: Solo estudiantes pueden inscribirse"""
        # Arrange
        codigo = "ABC12345"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.inscribir_por_codigo(
                mock_db,
                codigo,
                mock_coordinador
            )
        
        assert exc_info.value.status_code == 403
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._esta_inscrito')
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_misma_institucion')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_inscribir_ya_inscrito(
        self, mock_obtener_curso, mock_validar, mock_esta_inscrito,
        mock_db, mock_estudiante
    ):
        """Test: No puede inscribirse dos veces en el mismo curso"""
        # Arrange
        codigo = "ABC12345"
        mock_obtener_curso.return_value = {
            "curso_id": str(uuid4()),
            "nombre": "Curso Test"
        }
        mock_esta_inscrito.return_value = True
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.inscribir_por_codigo(
                mock_db,
                codigo,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 400
    
    # ==================== Tests de Generación de Códigos ====================
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._generar_codigo_unico')
    def test_generar_codigo_success(self, mock_generar, mock_db, mock_coordinador):
        """Test: Coordinador genera código exitosamente"""
        # Arrange
        programa_id = str(uuid4())
        codigo_generado = "XYZ98765"
        mock_generar.return_value = codigo_generado
        
        # Mock del execute para INSERT
        mock_result = Mock()
        mock_result.fetchone.return_value = [codigo_generado]
        mock_db.execute.return_value = mock_result
        
        # Act
        result = InscripcionService.generar_codigo_invitacion(
            mock_db,
            programa_id,
            mock_coordinador
        )
        
        # Assert
        assert result["success"] is True
        assert "codigo" in result["data"] or "token" in result["data"]
        mock_db.commit.assert_called_once()
    
    def test_generar_codigo_no_coordinador(self, mock_db, mock_estudiante):
        """Test: Solo coordinadores pueden generar códigos"""
        # Arrange
        programa_id = str(uuid4())
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.generar_codigo_invitacion(
                mock_db,
                programa_id,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Validación ====================
    
    def test_validar_codigo_length(self):
        """Test: Constante de longitud de código"""
        assert InscripcionService.CODIGO_LENGTH == 8
    
    def test_validar_expiracion_dias(self):
        """Test: Constante de días de expiración"""
        assert InscripcionService.CODIGO_EXPIRACION_DIAS == 30
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_codigo_invalido(self, mock_obtener, mock_db, mock_estudiante):
        """Test: Código de acceso inválido"""
        # Arrange
        codigo = "INVALIDO"
        mock_obtener.side_effect = HTTPException(
            status_code=404,
            detail="Código no encontrado"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.inscribir_por_codigo(
                mock_db,
                codigo,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 404
    
    # ==================== Tests de Institución ====================
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_misma_institucion')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_diferente_institucion(
        self, mock_obtener_curso, mock_validar,
        mock_db, mock_estudiante
    ):
        """Test: No puede inscribirse en curso de otra institución"""
        # Arrange
        codigo = "ABC12345"
        mock_obtener_curso.return_value = {
            "curso_id": str(uuid4()),
            "nombre": "Curso Test"
        }
        mock_validar.side_effect = HTTPException(
            status_code=403,
            detail="Curso de otra institución"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.inscribir_por_codigo(
                mock_db,
                codigo,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Grupos ====================
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._vincular_estudiante_grupo')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_o_crear_grupo')
    @patch('src.services.academic.inscripcion_service.InscripcionService._esta_inscrito')
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_misma_institucion')
    @patch('src.services.academic.inscripcion_service.InscripcionService._obtener_curso_por_codigo')
    def test_crear_grupo_si_no_existe(
        self, mock_obtener_curso, mock_validar, mock_esta_inscrito,
        mock_obtener_grupo, mock_vincular, mock_db, mock_estudiante
    ):
        """Test: Se crea grupo automáticamente si no existe"""
        # Arrange
        codigo = "ABC12345"
        curso_id = str(uuid4())
        nuevo_grupo_id = uuid4()
        
        mock_obtener_curso.return_value = {
            "curso_id": curso_id,
            "nombre": "Curso Test"
        }
        mock_esta_inscrito.return_value = False
        mock_obtener_grupo.return_value = nuevo_grupo_id  # Simula creación
        
        # Act
        result = InscripcionService.inscribir_por_codigo(
            mock_db,
            codigo,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        mock_obtener_grupo.assert_called_once_with(mock_db, curso_id)
        mock_vincular.assert_called_once_with(
            mock_db,
            mock_estudiante.usuario_id,
            nuevo_grupo_id
        )
    
    # ==================== Tests de Códigos de Invitación ====================
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._marcar_codigo_usado')
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_codigo_invitacion')
    def test_vincular_por_codigo_invitacion_success(
        self, mock_validar_codigo, mock_marcar_usado,
        mock_db, mock_estudiante
    ):
        """Test: Estudiante se vincula a programa con código de invitación"""
        # Arrange
        codigo = "INV12345"
        programa_id = str(uuid4())
        token_id = str(uuid4())
        
        mock_validar_codigo.return_value = {
            "token_id": token_id,
            "programa_id": programa_id,
            "programa_nombre": "Ingeniería de Software"
        }
        
        # Act
        result = InscripcionService.vincular_por_codigo_invitacion(
            mock_db,
            codigo,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["programa_id"] == programa_id
        mock_marcar_usado.assert_called_once_with(
            mock_db,
            token_id,
            mock_estudiante.usuario_id
        )
        mock_db.commit.assert_called_once()
    
    def test_vincular_codigo_invitacion_no_estudiante(self, mock_db, mock_coordinador):
        """Test: Solo estudiantes pueden usar códigos de invitación"""
        # Arrange
        codigo = "INV12345"
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.vincular_por_codigo_invitacion(
                mock_db,
                codigo,
                mock_coordinador
            )
        
        assert exc_info.value.status_code == 403
        assert "estudiantes" in exc_info.value.detail.lower()
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_codigo_invitacion')
    def test_vincular_codigo_invitacion_invalido(
        self, mock_validar_codigo, mock_db, mock_estudiante
    ):
        """Test: Código de invitación inválido"""
        # Arrange
        codigo = "INVALIDO"
        mock_validar_codigo.side_effect = HTTPException(
            status_code=404,
            detail="Código de invitación inválido"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.vincular_por_codigo_invitacion(
                mock_db,
                codigo,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 404
    
    @patch('src.services.academic.inscripcion_service.InscripcionService._validar_codigo_invitacion')
    def test_vincular_codigo_invitacion_expirado(
        self, mock_validar_codigo, mock_db, mock_estudiante
    ):
        """Test: Código de invitación expirado"""
        # Arrange
        codigo = "EXP12345"
        mock_validar_codigo.side_effect = HTTPException(
            status_code=400,
            detail="Este código ha expirado"
        )
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.vincular_por_codigo_invitacion(
                mock_db,
                codigo,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 400
        assert "expirado" in exc_info.value.detail.lower()
    
    # ==================== Tests de Confirmación de Programa ====================
    
    def test_confirmar_programa_estudiante_success(self, mock_db, mock_estudiante):
        """Test: Estudiante confirma su programa exitosamente"""
        # Arrange
        programa_id = str(uuid4())
        programa_nombre = "Ingeniería de Sistemas"
        
        # Mock para verificar programa existe
        mock_result_programa = Mock()
        mock_result_programa.fetchone.return_value = (programa_nombre,)
        
        mock_db.execute.return_value = mock_result_programa
        
        # Act
        result = InscripcionService.confirmar_programa_estudiante(
            mock_db,
            programa_id,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"]["programa_id"] == programa_id
        assert programa_nombre in result["message"]
        mock_db.commit.assert_called_once()
    
    def test_confirmar_programa_no_estudiante(self, mock_db, mock_coordinador):
        """Test: Solo estudiantes pueden confirmar programa"""
        # Arrange
        programa_id = str(uuid4())
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.confirmar_programa_estudiante(
                mock_db,
                programa_id,
                mock_coordinador
            )
        
        assert exc_info.value.status_code == 403
    
    def test_confirmar_programa_no_existe(self, mock_db, mock_estudiante):
        """Test: Programa no encontrado"""
        # Arrange
        programa_id = str(uuid4())
        
        # Mock para programa no encontrado
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InscripcionService.confirmar_programa_estudiante(
                mock_db,
                programa_id,
                mock_estudiante
            )
        
        assert exc_info.value.status_code == 404
        assert "no encontrado" in exc_info.value.detail.lower()
    
    # ==================== Tests de Obtención de Programas ====================
    
    def test_obtener_programas_disponibles_success(self, mock_db, mock_estudiante):
        """Test: Obtiene lista de programas disponibles"""
        # Arrange
        institucion_id = str(uuid4())
        
        # Mock resultado de institución
        mock_result_inst = Mock()
        mock_result_inst.fetchone.return_value = (institucion_id,)
        
        # Mock resultado de programas
        mock_result_programas = Mock()
        programas_data = [
            Mock(_mapping={
                "programa_id": str(uuid4()),
                "nombre": "Ingeniería de Software",
                "descripcion": "Programa de ingeniería",
                "duracion": 10,
                "total_estudiantes": 25
            }),
            Mock(_mapping={
                "programa_id": str(uuid4()),
                "nombre": "Diseño Gráfico",
                "descripcion": "Programa de diseño",
                "duracion": 8,
                "total_estudiantes": 15
            })
        ]
        mock_result_programas.fetchall.return_value = programas_data
        
        mock_db.execute.side_effect = [mock_result_inst, mock_result_programas]
        
        # Act
        result = InscripcionService.obtener_programas_disponibles(
            mock_db,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert result["total"] == 2
        assert len(result["data"]) == 2
        assert result["data"][0]["nombre"] == "Ingeniería de Software"
    
    def test_obtener_programas_sin_institucion(self, mock_db, mock_estudiante):
        """Test: Usuario sin institución asignada"""
        # Arrange
        mock_result = Mock()
        mock_result.fetchone.return_value = None
        mock_db.execute.return_value = mock_result
        
        # Act
        result = InscripcionService.obtener_programas_disponibles(
            mock_db,
            mock_estudiante
        )
        
        # Assert
        assert result["success"] is True
        assert result["data"] == []
        assert "no tienes institución" in result["message"].lower()
    
    def test_obtener_programas_con_institucion_especifica(self, mock_db, mock_estudiante):
        """Test: Obtiene programas de institución específica"""
        # Arrange
        institucion_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Act
        result = InscripcionService.obtener_programas_disponibles(
            mock_db,
            mock_estudiante,
            institucion_id=institucion_id
        )
        
        # Assert
        assert result["success"] is True
        assert isinstance(result["data"], list)
    
    # ==================== Tests de Métodos Privados ====================
    
    def test_generar_codigo_unico_formato(self, mock_db):
        """Test: Código generado tiene formato correcto"""
        # Arrange
        mock_result = Mock()
        mock_result.scalar.return_value = False  # Código único
        mock_db.execute.return_value = mock_result
        
        # Act
        codigo = InscripcionService._generar_codigo_unico(mock_db)
        
        # Assert
        assert len(codigo) == InscripcionService.CODIGO_LENGTH
        assert codigo.isupper() or codigo.isalnum()
    
    def test_generar_codigo_unico_colision(self, mock_db):
        """Test: Maneja colisiones generando nuevo código"""
        # Arrange
        mock_result = Mock()
        # Primera vez existe (True), segunda no existe (False)
        mock_result.scalar.side_effect = [True, False]
        mock_db.execute.return_value = mock_result
        
        # Act
        codigo = InscripcionService._generar_codigo_unico(mock_db)
        
        # Assert
        assert len(codigo) == InscripcionService.CODIGO_LENGTH
        # Verificar que se llamó dos veces (por la colisión)
        assert mock_db.execute.call_count == 2
