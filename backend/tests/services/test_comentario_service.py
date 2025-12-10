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

        # Agregar side_effect robusto para db.execute para responder según el SQL
        def execute_side_effect(query, params=None):
            sql = str(query).lower()
            if 'count(' in sql:
                return mock_count
            if 'comentario_padre_id' in sql:
                mock_resp = Mock()
                mock_resp.fetchall.return_value = []
                return mock_resp
            return mock_result

        mock_db.execute.side_effect = execute_side_effect
        
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
        # _validar_acceso_curso puede ser llamado tanto al inicio como al validar
        # respuestas anidadas; comprobar que se invocó al menos una vez.
        mock_validar.assert_called()

    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_enriquecidos_archivos(self, mock_validar, mock_db, mock_usuario):
        """Test: Obtener comentarios debe enriquecer archivos a partir de archivos_curso"""
        curso_id = str(uuid4())

        # Simular resultado principal con archivos_adjuntos guardados como JSON string
        mock_row = Mock()
        mock_row._mapping = {
            "comentario_id": str(uuid4()),
            "contenido": "Comentario con archivo",
            "tipo": "comentario",
            "fecha_creacion": datetime.now(),
            "archivos_adjuntos": "[\"file-1\"]",
            "autor_id": str(uuid4()),
            "autor_nombre": "Ana Perez",
            "autor_avatar": None,
            "total_respuestas": 0,
            "total_reacciones": 0,
        }

        mock_result = Mock()
        mock_result.fetchall.return_value = [mock_row]

        # Mock count
        mock_count = Mock()
        mock_count.scalar.return_value = 1

        # Archivo metadata
        mock_archivo_row = Mock()
        mock_archivo_row._mapping = {
            "archivo_id": "file-1",
            "nombre_original": "documento.pdf",
            "url": "/uploads/cursos/1/documento.pdf",
            "tipo": "application/pdf",
            "tamaño": 2048,
            "fecha_subida": None,
        }

        # Ejecutar side_effect según la query que llega
        def execute_side_effect(query, params=None):
            sql = str(query).lower()
            if 'FROM archivos_curso' in sql:
                mock_exec = Mock()
                mock_exec.fetchone.return_value = mock_archivo_row
                return mock_exec
            if 'comentario_padre_id' in sql:
                mock_resp = Mock()
                mock_resp.fetchall.return_value = []
                return mock_resp
            if 'count(' in sql:
                return mock_count
            return mock_result

        mock_db.execute.side_effect = execute_side_effect

        # Parchear para que obtener_respuestas no intente ejecutar queries
        with patch('src.services.academic.comentario_service.ComentarioService.obtener_respuestas') as mock_respuestas:
            mock_respuestas.return_value = {"success": True, "data": []}

            result = ComentarioService.obtener_comentarios_curso(
                mock_db, curso_id, mock_usuario
            )

        assert result["success"] is True
        assert len(result["data"]) == 1
        comment = result["data"][0]
        assert "archivos_adjuntos" in comment
        assert len(comment["archivos_adjuntos"]) == 1
        archivo = comment["archivos_adjuntos"][0]
        assert archivo["archivo_id"] == "file-1"
        assert archivo["nombre"] == "documento.pdf"
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    def test_obtener_comentarios_vacio(self, mock_validar, mock_db, mock_usuario):
        """Test: Curso sin comentarios"""
        # Arrange
        curso_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.fetchall.return_value = []
        mock_count = Mock()
        mock_count.scalar.return_value = 0
        mock_db.execute.side_effect = [mock_result, mock_count, Mock()]
        
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
        mock_db.execute.side_effect = [mock_result, mock_count, Mock()]
        
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
    
    @patch('src.services.academic.comentario_service.Comentario')
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

    @patch('src.services.academic.comentario_service.Comentario')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_contenido')
    def test_crear_comentario_persiste_referencias_si_no_validadas(self, mock_validar_cont, mock_validar_acc, mock_comentario_cls, mock_db, mock_usuario):
        """Test: Si los archivos referenciados no se encuentran en archivos_curso,
        se deben persistir las referencias originales como fallback en lugar de
        descartar completamente."""
        curso_id = str(uuid4())
        archivo_id = "file-missing"

        # Preparar db.execute para que SELECT no devuelva registro (archivo no registrado)
        def execute_side_effect(query, params=None):
            # Cualquier query a archivos_curso debe devolver None
            mock_exec = Mock()
            mock_exec.fetchone.return_value = None
            return mock_exec

        mock_db.execute.side_effect = execute_side_effect

        # Llamar a crear_comentario con archivos no validados
        result = ComentarioService.crear_comentario(
            mock_db,
            curso_id,
            "Test comentario con referencia",
            mock_usuario,
            archivos_adjuntos=[{"archivo_id": archivo_id}]
        )

        # Como usamos un mock para la clase Comentario, verificamos que el
        # servicio intentó persistir las referencias originales en el
        # atributo archivos_lista del modelo sin perder la referencia.
        assert result["success"] is True
        # Debido a que Comentario está parcheado como Mock, el servicio
        # asignará directamente el atributo archivos_lista en la instancia
        # mock; comprobamos ese atributo en lugar de depender de
        # serializadores/propiedades de SQLAlchemy.
        assert mock_comentario_cls.return_value.archivos_lista[0]["archivo_id"] == archivo_id
    
    @patch('src.services.academic.comentario_service.ComentarioService._validar_acceso_curso')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_contenido')
    @patch('src.services.academic.comentario_service.ComentarioService._validar_comentario_padre')
    @patch('src.services.academic.comentario_service.Comentario')
    def test_crear_respuesta(self, mock_comentario_cls, mock_validar_padre, mock_validar_cont, mock_validar_acc, mock_db, mock_usuario):
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

    # ==================== Tests de Enriquecimiento de Archivos Adjuntos ====================

    def test_enriquecer_archivos_adjuntos_string_id_found(self, mock_db):
        """Test: Enriquecer archivos cuando se recibe una lista de strings con IDs existentes"""
        archivo_id = "file-123"
        mock_row = Mock()
        mock_row._mapping = {
            "archivo_id": archivo_id,
            "nombre_original": "archivo.pdf",
            "url": "http://files.example.com/file-123",
            "tipo": "application/pdf",
            "tamaño": 1024,
            "fecha_subida": None,
        }

        mock_db.execute.return_value.fetchone.return_value = mock_row

        enriched = ComentarioService._enriquecer_archivos_adjuntos(mock_db, [archivo_id])
        assert len(enriched) == 1
        e = enriched[0]
        assert e["archivo_id"] == archivo_id
        assert e["id"] == archivo_id
        assert e["nombre"] == "archivo.pdf"
        assert e["url"] == "http://files.example.com/file-123"

    def test_enriquecer_archivos_adjuntos_missing_metadata_returns_minimal(self, mock_db):
        """Test: Si no existe metadata en archivos_curso, debe devolver objeto mínimo con id"""
        archivo_id = "missing-file"
        # Simular que no hay registro en archivos_curso
        mock_db.execute.return_value.fetchone.return_value = None

        enriched = ComentarioService._enriquecer_archivos_adjuntos(mock_db, [archivo_id])
        assert len(enriched) == 1
        assert enriched[0]["archivo_id"] == archivo_id
        assert enriched[0]["id"] == archivo_id

    def test_enriquecer_archivos_adjuntos_alternate_key_names(self, mock_db):
        """Test: Aceptar distintas keys como id: archivo_id, id, file_id o archivoId"""
        for key in ("archivo_id", "id", "file_id", "archivoId"):
            mock_db.execute.reset_mock()
            val = "file-abc"
            mock_row = Mock()
            mock_row._mapping = {
                "archivo_id": val,
                "nombre_original": "doc.txt",
                "url": "http://files.example.com/doc.txt",
                "tipo": "text/plain",
                "tamaño": 512,
                "fecha_subida": None,
            }
            mock_db.execute.return_value.fetchone.return_value = mock_row

            enriched = ComentarioService._enriquecer_archivos_adjuntos(mock_db, [{key: val}])
            assert len(enriched) == 1
            assert enriched[0]["archivo_id"] == val

    def test_enriquecer_archivos_adjuntos_unexpected_input_type(self, mock_db):
        """Test: Formatos inesperados deben ser convertidos a string y devueltos como mínimos"""
        mock_db.execute.return_value.fetchone.return_value = None
        enriched = ComentarioService._enriquecer_archivos_adjuntos(mock_db, [12345])
        assert len(enriched) == 1
        assert enriched[0]["archivo_id"] == "12345"
    
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
                ,
                "autor_nombre": "Usuario Test"
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
        
        # Assert: 3 queries: 1 para datos + 1 para count + 1 para respuestas en bloque
        assert mock_db.execute.call_count == 3
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
                    ,"autor_nombre": "Usuario Test"
            }
            mock_rows.append(mock_row)
        
        mock_result = Mock()
        mock_result.fetchall.return_value = mock_rows
        mock_count = Mock()
        mock_count.scalar.return_value = 1000
        mock_db.execute.side_effect = [mock_result, mock_count, Mock()]
        
        # Act
        import time
        start = time.time()
        result = ComentarioService.obtener_comentarios_curso(
            mock_db,
            curso_id,
            mock_usuario
        )
        elapsed = time.time() - start
        
        # Assert - allow some leniency on CI: < 3 seconds is reasonable
        assert elapsed < 3.0  # < 3 segundos
        assert len(result["data"]) == 1000
