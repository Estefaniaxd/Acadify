"""
Tests unitarios para ArchivoService

Tests que verifican:
- Subida de archivos
- Validación de tamaño
- Validación de extensiones
- Obtención de archivos
- Eliminación de archivos
- Permisos de acceso
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4
from pathlib import Path
from fastapi import HTTPException, UploadFile

from src.services.academic.archivo_service import ArchivoService
from src.models.users.usuario import Usuario


class TestArchivoService:
    """Tests para ArchivoService"""
    
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
        usuario.rol = "docente"
        return usuario
    
    @pytest.fixture
    def mock_archivo_valido(self):
        """Mock de archivo válido"""
        archivo = Mock(spec=UploadFile)
        archivo.filename = "documento.pdf"
        archivo.size = 5 * 1024 * 1024  # 5 MB
        archivo.content_type = "application/pdf"
        return archivo
    
    # ==================== Tests de Constantes ====================
    
    def test_max_file_size(self):
        """Test: Tamaño máximo definido correctamente"""
        assert ArchivoService.MAX_FILE_SIZE == 10 * 1024 * 1024  # 10 MB
    
    def test_allowed_extensions(self):
        """Test: Extensiones permitidas"""
        extensiones = ArchivoService.ALLOWED_EXTENSIONS
        assert '.pdf' in extensiones
        assert '.doc' in extensiones
        assert '.docx' in extensiones
        assert '.jpg' in extensiones
        assert '.png' in extensiones
        assert '.zip' in extensiones
        assert len(extensiones) == 9
    
    # ==================== Tests de Validación ====================
    
    def test_validar_archivo_valido(self, mock_archivo_valido):
        """Test: Archivo válido pasa validación"""
        # No debe lanzar excepción
        ArchivoService._validar_archivo(mock_archivo_valido)
    
    def test_validar_archivo_muy_grande(self):
        """Test: Archivo excede tamaño máximo"""
        # Arrange
        archivo = Mock(spec=UploadFile)
        archivo.filename = "archivo_grande.pdf"
        archivo.size = 15 * 1024 * 1024  # 15 MB (excede el límite)
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService._validar_archivo(archivo)
        
        assert exc_info.value.status_code == 400
        assert "exceder" in str(exc_info.value.detail).lower()
    
    def test_validar_extension_invalida(self):
        """Test: Extensión no permitida"""
        # Arrange
        archivo = Mock(spec=UploadFile)
        archivo.filename = "script.exe"  # Extensión peligrosa
        archivo.size = 1 * 1024 * 1024  # 1 MB
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService._validar_archivo(archivo)
        
        assert exc_info.value.status_code == 400
        assert "extensión" in str(exc_info.value.detail).lower()
    
    def test_validar_sin_extension(self):
        """Test: Archivo sin extensión"""
        # Arrange
        archivo = Mock(spec=UploadFile)
        archivo.filename = "archivo_sin_extension"
        archivo.size = 1 * 1024 * 1024
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService._validar_archivo(archivo)
        
        assert exc_info.value.status_code == 400
    
    # ==================== Tests de Subida de Archivos ====================
    
    @pytest.mark.asyncio
    @patch('src.services.academic.archivo_service.ArchivoService._registrar_archivo_bd')
    @patch('src.services.academic.archivo_service.ArchivoService._guardar_archivo')
    @patch('src.services.academic.archivo_service.ArchivoService._validar_acceso_curso')
    async def test_subir_archivo_success(
        self, mock_validar, mock_guardar, mock_registrar,
        mock_db, mock_usuario, mock_archivo_valido
    ):
        """Test: Subir archivo exitosamente"""
        # Arrange
        curso_id = str(uuid4())
        mock_guardar.return_value = None
        mock_registrar.return_value = {'archivo_id': uuid4()}
        
        # Act
        result = await ArchivoService.subir_archivo(
            mock_db,
            curso_id,
            mock_archivo_valido,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "archivo_id" in result["data"]
        assert result["data"]["nombre"] == "documento.pdf"
        mock_guardar.assert_called_once()
        mock_registrar.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.services.academic.archivo_service.ArchivoService._validar_acceso_curso')
    async def test_subir_archivo_invalido(
        self, mock_validar, mock_db, mock_usuario
    ):
        """Test: No se puede subir archivo inválido"""
        # Arrange
        curso_id = str(uuid4())
        archivo_invalido = Mock(spec=UploadFile)
        archivo_invalido.filename = "virus.exe"
        archivo_invalido.size = 1 * 1024 * 1024
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await ArchivoService.subir_archivo(
                mock_db,
                curso_id,
                archivo_invalido,
                mock_usuario
            )
        
        assert exc_info.value.status_code == 400
    
    # ==================== Tests de Obtención de Archivos ====================
    
    @patch('src.services.academic.archivo_service.ArchivoService._validar_acceso_curso')
    def test_obtener_archivos_curso_success(
        self, mock_validar, mock_db, mock_usuario
    ):
        """Test: Obtener archivos de un curso"""
        # Arrange
        curso_id = str(uuid4())
        mock_rows = [
            Mock(_mapping={
                'archivo_id': str(uuid4()),
                'nombre': 'archivo1.pdf',
                'url': '/uploads/archivo1.pdf',
                'tipo': 'material'
            }),
            Mock(_mapping={
                'archivo_id': str(uuid4()),
                'nombre': 'archivo2.docx',
                'url': '/uploads/archivo2.docx',
                'tipo': 'recurso'
            })
        ]
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_db.execute.return_value = mock_result
        
        # Act
        result = ArchivoService.obtener_archivos_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 2
        assert result["data"][0]["nombre"] == "archivo1.pdf"
    
    @patch('src.services.academic.archivo_service.ArchivoService._validar_acceso_curso')
    def test_obtener_archivos_vacio(
        self, mock_validar, mock_db, mock_usuario
    ):
        """Test: Curso sin archivos"""
        # Arrange
        curso_id = str(uuid4())
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Act
        result = ArchivoService.obtener_archivos_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert len(result["data"]) == 0
    
    # ==================== Tests de Eliminación ====================
    
    @patch('pathlib.Path.unlink')
    @patch('pathlib.Path.exists')
    def test_eliminar_archivo_success(
        self, mock_exists, mock_unlink, mock_db, mock_usuario
    ):
        """Test: Eliminar archivo exitosamente"""
        # Arrange
        archivo_id = str(uuid4())
        usuario_id = mock_usuario.usuario_id
        
        # Mock para obtener info del archivo
        mock_row = Mock()
        mock_row._mapping = {
            'url': '/uploads/archivo.pdf',
            'subido_por': usuario_id,  # Mismo usuario
            'curso_id': str(uuid4())
        }
        mock_result_select = Mock()
        mock_result_select.fetchone.return_value = mock_row
        
        # Mock para DELETE
        mock_result_delete = Mock()
        
        # Configurar execute para devolver diferentes resultados
        mock_db.execute.side_effect = [mock_result_select, mock_result_delete]
        mock_exists.return_value = True
        
        # Act
        result = ArchivoService.eliminar_archivo(
            mock_db,
            archivo_id,
            mock_usuario
        )
        
        # Assert
        assert result["success"] is True
        assert "eliminado" in result["message"].lower()
        mock_db.commit.assert_called_once()
        mock_unlink.assert_called_once()
    
    def test_eliminar_archivo_no_existe(self, mock_db, mock_usuario):
        """Test: Intentar eliminar archivo que no existe"""
        # Arrange
        archivo_id = str(uuid4())
        mock_result = Mock()
        mock_result.fetchone.return_value = None  # No existe
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService.eliminar_archivo(
                mock_db,
                archivo_id,
                mock_usuario
            )
        
        assert exc_info.value.status_code == 404
    
    def test_eliminar_archivo_sin_permisos(self, mock_db):
        """Test: Usuario sin permisos para eliminar"""
        # Arrange
        archivo_id = str(uuid4())
        
        # Usuario que intenta eliminar (NO es el autor)
        usuario_sin_permisos = Mock(spec=Usuario)
        usuario_sin_permisos.usuario_id = uuid4()
        usuario_sin_permisos.rol = "estudiante"
        
        # Mock del archivo (subido por otro usuario)
        mock_row = Mock()
        mock_row._mapping = {
            'url': '/uploads/archivo.pdf',
            'subido_por': uuid4(),  # Diferente usuario
            'curso_id': str(uuid4())
        }
        mock_result = Mock()
        mock_result.fetchone.return_value = mock_row
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService.eliminar_archivo(
                mock_db,
                archivo_id,
                usuario_sin_permisos
            )
        
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Permisos ====================
    
    def test_validar_acceso_curso_sin_acceso(self, mock_db, mock_usuario):
        """Test: Usuario sin acceso al curso"""
        # Arrange
        curso_id = str(uuid4())
        mock_result = Mock()
        mock_result.scalar.return_value = False  # No tiene acceso
        mock_db.execute.return_value = mock_result
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ArchivoService._validar_acceso_curso(mock_db, curso_id, mock_usuario)
        
        assert exc_info.value.status_code == 403
    
    # ==================== Tests de Tipos de Archivo ====================
    
    @pytest.mark.asyncio
    @patch('src.services.academic.archivo_service.ArchivoService._registrar_archivo_bd')
    @patch('src.services.academic.archivo_service.ArchivoService._guardar_archivo')
    @patch('src.services.academic.archivo_service.ArchivoService._validar_acceso_curso')
    async def test_subir_archivo_con_tipo(
        self, mock_validar, mock_guardar, mock_registrar,
        mock_db, mock_usuario, mock_archivo_valido
    ):
        """Test: Subir archivo con tipo específico"""
        # Arrange
        curso_id = str(uuid4())
        mock_guardar.return_value = None
        mock_registrar.return_value = {'archivo_id': uuid4()}
        
        # Act
        result = await ArchivoService.subir_archivo(
            mock_db,
            curso_id,
            mock_archivo_valido,
            mock_usuario,
            tipo="recurso"
        )
        
        # Assert
        assert result["success"] is True
        # Verificar que se llamó con el tipo correcto
        call_args = mock_registrar.call_args
        assert call_args[0][5] == "recurso"  # tipo es el 6to argumento
    
    # ==================== Tests de Extensiones Específicas ====================
    
    def test_validar_pdf(self):
        """Test: Archivo PDF válido"""
        archivo = Mock(spec=UploadFile)
        archivo.filename = "documento.pdf"
        archivo.size = 1 * 1024 * 1024
        ArchivoService._validar_archivo(archivo)
    
    def test_validar_imagen(self):
        """Test: Imagen válida"""
        archivo = Mock(spec=UploadFile)
        archivo.filename = "foto.jpg"
        archivo.size = 2 * 1024 * 1024
        ArchivoService._validar_archivo(archivo)
    
    def test_validar_zip(self):
        """Test: Archivo ZIP válido"""
        archivo = Mock(spec=UploadFile)
        archivo.filename = "recursos.zip"
        archivo.size = 8 * 1024 * 1024
        ArchivoService._validar_archivo(archivo)
