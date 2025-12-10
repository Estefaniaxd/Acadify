"""Service para gestión de archivos en cursos.

SOLID + Clean Code
"""

from datetime import UTC, datetime
import logging
from pathlib import Path
from typing import Any
import uuid

import aiofiles
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users.usuario import Usuario


logger = logging.getLogger(__name__)


class ArchivoService:
    """Service para gestión de archivos."""

    # Constantes
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".doc",
        ".docx",
        ".ppt",
        ".pptx",
        ".txt",
        ".jpg",
        ".png",
        ".zip",
    }
    UPLOAD_DIR = Path("uploads/cursos")

    @staticmethod
    async def subir_archivo(
        db: Session,
        curso_id: str,
        archivo: UploadFile,
        usuario: Usuario,
        descripcion: str | None = None,
        tipo: str = "material",
    ) -> dict[str, Any]:
        """Sube un archivo al curso.

        Args:
            db: Sesión de BD
            curso_id: ID del curso
            archivo: Archivo a subir
            usuario: Usuario que sube
            descripcion: Descripción del archivo
            tipo: Tipo (material, tarea, recurso)

        Returns:
            Dict con información del archivo subido
        """
        try:
            # Validaciones
            ArchivoService._validar_acceso_curso(db, curso_id, usuario)
            ArchivoService._validar_archivo(archivo)

            # Generar nombre único
            extension = Path(archivo.filename).suffix
            nombre_unico = f"{uuid.uuid4()}{extension}"
            ruta_completa = ArchivoService.UPLOAD_DIR / curso_id / nombre_unico

            # Crear directorio si no existe
            ruta_completa.parent.mkdir(parents=True, exist_ok=True)

            # Guardar archivo
            await ArchivoService._guardar_archivo(archivo, ruta_completa)

            # Verificar que el archivo se guardó correctamente
            if not ruta_completa.exists():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al guardar el archivo en el sistema de archivos",
                )

            # Calcular tamaño real del archivo guardado
            try:
                tamaño_real = ruta_completa.stat().st_size
                if tamaño_real == 0:
                    # Si el tamaño es 0, intentar esperar un poco y recalcular
                    import asyncio
                    await asyncio.sleep(0.1)
                    tamaño_real = ruta_completa.stat().st_size
                    if tamaño_real == 0:
                        logger.warning(f"Archivo {ruta_completa} tiene tamaño 0")
            except OSError as e:
                logger.error(f"Error al calcular tamaño del archivo {ruta_completa}: {e}")
                tamaño_real = 0

            # Log para debugging
            logger.info(f"Archivo guardado: {ruta_completa}, tamaño calculado: {tamaño_real} bytes")

            # Registrar en BD
            url_archivo = f"/uploads/cursos/{curso_id}/{nombre_unico}"
            registro = ArchivoService._registrar_archivo_bd(
                db,
                curso_id,
                archivo.filename,
                url_archivo,
                descripcion,
                tipo,
                usuario.usuario_id,
                tamaño_real,
            )

            logger.info(f"Archivo subido: {nombre_unico} al curso {curso_id}")

            return {
                "success": True,
                "message": "Archivo subido exitosamente",
                "data": {
                    "archivo_id": str(registro["archivo_id"]),
                    "nombre": archivo.filename,
                    "url": url_archivo,
                    "tamaño": tamaño_real,
                },
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error subiendo archivo: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir archivo: {e!s}",
            ) from e

    @staticmethod
    def obtener_archivos_curso(
        db: Session, curso_id: str, usuario: Usuario, tipo: str | None = None
    ) -> dict[str, Any]:
        """Obtiene archivos de un curso."""
        try:
            ArchivoService._validar_acceso_curso(db, curso_id, usuario)

            query = text(
                """
                SELECT
                    a.archivo_id,
                    a.nombre_original,
                    a.url,
                    a.tipo,
                    a.descripcion,
                    a.tamaño,
                    a.fecha_subida,
                    u.nombres || ' ' || u.apellidos as subido_por
                FROM archivos_curso a
                JOIN "Usuario" u ON a.subido_por = u.usuario_id
                WHERE a.curso_id = :curso_id
                    AND (:tipo IS NULL OR a.tipo = :tipo)
                ORDER BY a.fecha_subida DESC
            """
            )

            result = db.execute(query, {"curso_id": curso_id, "tipo": tipo}).fetchall()

            archivos = [dict(row._mapping) for row in result]

            return {"success": True, "data": archivos, "total": len(archivos)}

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error obteniendo archivos: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al obtener archivos",
            ) from e

    @staticmethod
    def descargar_archivo(
        db: Session, archivo_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Descarga un archivo."""
        try:
            # Obtener info del archivo
            query = text(
                """
                SELECT
                    a.nombre_original,
                    a.url,
                    a.curso_id,
                    a.subido_por
                FROM archivos_curso a
                WHERE a.archivo_id = :archivo_id
            """
            )

            archivo = db.execute(query, {"archivo_id": archivo_id}).fetchone()

            if not archivo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Archivo no encontrado",
                )

            archivo_dict = dict(archivo._mapping)

            # Validar acceso al curso
            ArchivoService._validar_acceso_curso(db, archivo_dict["curso_id"], usuario)

            # Construir ruta física del archivo
            ruta_relativa = archivo_dict["url"].lstrip("/")
            ruta_archivo = Path(ruta_relativa)

            if not ruta_archivo.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Archivo no encontrado en el sistema de archivos",
                )

            # Determinar tipo MIME
            import mimetypes
            content_type, _ = mimetypes.guess_type(str(ruta_archivo))
            if not content_type:
                content_type = "application/octet-stream"

            # Leer y devolver el archivo
            from fastapi.responses import FileResponse
            return FileResponse(
                path=ruta_archivo,
                media_type=content_type,
                filename=archivo_dict["nombre_original"],
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error descargando archivo: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al descargar archivo",
            ) from e

    @staticmethod
    def eliminar_archivo(
        db: Session, archivo_id: str, usuario: Usuario
    ) -> dict[str, Any]:
        """Elimina un archivo."""
        try:
            # Obtener info del archivo
            query = text(
                """
                SELECT url, subido_por, curso_id
                FROM archivos_curso
                WHERE archivo_id = :archivo_id
            """
            )

            archivo = db.execute(query, {"archivo_id": archivo_id}).fetchone()

            if not archivo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Archivo no encontrado",
                )

            archivo_dict = dict(archivo._mapping)

            # Validar permisos
            es_autor = str(archivo_dict["subido_por"]) == str(usuario.usuario_id)
            es_docente = usuario.rol in ["docente", "coordinador"]

            if not (es_autor or es_docente):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No tienes permisos para eliminar este archivo",
                )

            # Eliminar archivo físico
            ruta_archivo = Path(archivo_dict["url"].lstrip("/"))
            if ruta_archivo.exists():
                ruta_archivo.unlink()

            # Eliminar registro de BD
            delete_query = text(
                "DELETE FROM archivos_curso WHERE archivo_id = :archivo_id"
            )
            db.execute(delete_query, {"archivo_id": archivo_id})
            db.commit()

            logger.info(f"Archivo eliminado: {archivo_id}")

            return {"success": True, "message": "Archivo eliminado exitosamente"}

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Error eliminando archivo: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar archivo",
            ) from e

    # ========== MÉTODOS PRIVADOS ==========

    @staticmethod
    def _validar_archivo(archivo: UploadFile) -> None:
        """Valida el archivo subido."""
        # Validar tamaño
        if archivo.size and archivo.size > ArchivoService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo no puede exceder {ArchivoService.MAX_FILE_SIZE / 1024 / 1024:.0f} MB",
            )

        # Validar extensión
        extension = Path(archivo.filename).suffix.lower()
        if extension not in ArchivoService.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Extensión no permitida. Permitidas: {', '.join(ArchivoService.ALLOWED_EXTENSIONS)}",
            )

    @staticmethod
    def _validar_acceso_curso(db: Session, curso_id: str, usuario: Usuario) -> None:
        """Valida acceso al curso."""
        from src.services.academic.curso_service import CursoService

        if not CursoService._usuario_tiene_acceso(db, curso_id, usuario):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso",
            )

    @staticmethod
    async def _guardar_archivo(archivo: UploadFile, ruta: Path) -> None:
        """Guarda el archivo en disco."""
        async with aiofiles.open(ruta, "wb") as f:
            contenido = await archivo.read()
            await f.write(contenido)

    @staticmethod
    def _registrar_archivo_bd(
        db: Session,
        curso_id: str,
        nombre: str,
        url: str,
        descripcion: str | None,
        tipo: str,
        subido_por: uuid.UUID,
        tamaño: int,
    ) -> dict[str, Any]:
        """Registra el archivo en la BD."""
        query = text(
            """
            INSERT INTO archivos_curso (
                curso_id, nombre_original, url, tipo,
                descripcion, subido_por, fecha_subida, tamaño
            )
            VALUES (
                :curso_id, :nombre_original, :url, :tipo,
                :descripcion, :subido_por, :fecha_subida, :tamaño
            )
            RETURNING archivo_id
        """
        )

        result = db.execute(
            query,
            {
                "curso_id": curso_id,
                "nombre_original": nombre,
                "url": url,
                "tipo": tipo,
                "descripcion": descripcion,
                "subido_por": subido_por,
                "fecha_subida": datetime.now(UTC),
                "tamaño": tamaño,
            },
        )

        archivo_id = result.fetchone()[0]
        db.commit()

        return {"archivo_id": archivo_id}


# Instancia global
archivo_service = ArchivoService()
