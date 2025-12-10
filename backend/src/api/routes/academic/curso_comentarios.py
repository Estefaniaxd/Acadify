from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import logging
import mimetypes
from pathlib import Path
from fastapi.responses import FileResponse

from src.api.dependencies import get_current_user, get_db
from src.models.users.usuario import Usuario
from src.models.communication.comentario import TipoComentario
from src.schemas.communication.comentario import ComentarioCreate as ComentarioCreateSchema, ComentarioResponse as ComentarioResponseSchema
from src.services.academic import comentario_service, reaccion_service
from src.services.academic.curso_service import CursoService

# Schema específico para request body (sin curso_id)
class ComentarioCreateRequest(BaseModel):
    contenido: str
    tipo: str = 'comentario'
    archivos_adjuntos: Optional[List[Dict[str, Any]]] = None
    comentario_padre_id: Optional[str] = None

router = APIRouter(prefix="/cursos", tags=["Comentarios"])
logger = logging.getLogger(__name__)

# Pydantic schemas
class ComentarioCreate(BaseModel):
    contenido: str
    tipo: str = 'comentario'  # anuncio, pregunta, comentario
    archivos: Optional[List[str]] = []

class ComentarioResponse(BaseModel):
    id: str
    contenido: str
    tipo: str
    autor: str
    fecha: str

class ReporteCreate(BaseModel):
    comentario_id: str
    razon: str
    descripcion: Optional[str] = None

class ReporteResponse(BaseModel):
    id: str
    comentario_id: str
    razon: str
    descripcion: Optional[str]
    reportado_por: str
    fecha_reporte: str
    estado: str = "pendiente"


# Schema para actualizar contenido de comentario/respuesta
class ComentarioUpdate(BaseModel):
    contenido: str

@router.post("/{curso_id}/comentarios")
async def crear_comentario(
    curso_id: str,
    comentario: ComentarioCreateRequest,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"📨 POST /cursos/{curso_id}/comentarios")
    logger.info(f"📨 Datos recibidos: {comentario.model_dump()}")
    logger.info(f"📨 comentario_padre_id: {comentario.comentario_padre_id}")
    logger.info(f"📨 archivos_adjuntos: {comentario.archivos_adjuntos}")
    logger.info(f"📨 Tipo de archivos_adjuntos: {type(comentario.archivos_adjuntos)}")

    # Crear objeto completo para validación con ComentarioCreateSchema
    # Intentar recuperar formas alternativas de enviar archivos adjuntos (legacy keys)
    comentario_data = comentario.model_dump()
    comentario_data['curso_id'] = curso_id

    # Si no vinieron archivos en el modelo pydantic, intentar leer el JSON crudo
    archivos_raw = comentario.archivos_adjuntos
    if not archivos_raw:
        try:
            raw = await request.json()
        except Exception:
            # Fallback: no raw body available or already consumed
            raw = {}

        # Buscar claves alternativas que algunos frontends/libraries podrían enviar
        archivos_raw = raw.get('archivos_adjuntos') or raw.get('archivos') or raw.get('attached_files') or raw.get('files')

    # Normalizar a la forma esperada: lista de dicts con { archivo_id }
    def _normalize_archivos(lst):
        if not lst:
            return None
        normalized = []
        for it in lst:
            if isinstance(it, str):
                normalized.append({'archivo_id': it})
            elif isinstance(it, dict):
                archivo_id = it.get('archivo_id') or it.get('id') or it.get('file_id') or it.get('archivoId')
                if archivo_id:
                    normalized.append({'archivo_id': archivo_id})
        return normalized

    archivos_normalizados = _normalize_archivos(archivos_raw)
    comentario_data['archivos_adjuntos'] = archivos_normalizados

    # Validar con schema completo
    validated_comentario = ComentarioCreateSchema(**comentario_data)

    return comentario_service.crear_comentario(
        db=db,
        curso_id=curso_id,
        contenido=validated_comentario.contenido,
        usuario=current_user,
        tipo=validated_comentario.tipo,
        comentario_padre_id=validated_comentario.comentario_padre_id,
        archivos_adjuntos=validated_comentario.archivos_adjuntos,
    )

@router.get("/{curso_id}/comentarios")
async def obtener_comentarios(
    curso_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return comentario_service.obtener_comentarios_curso(
        db=db, curso_id=curso_id, limit=limit, offset=offset, usuario=current_user
    )

@router.post("/comentarios/{comentario_id}/reacciones")
async def crear_reaccion(
    comentario_id: str,
    tipo: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reaccion_service.crear_reaccion(
        db=db, comentario_id=comentario_id, tipo=tipo, usuario=current_user
    )

@router.get("/comentarios/{comentario_id}/reacciones")
async def obtener_reacciones(
    comentario_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return reaccion_service.obtener_reacciones(
        db=db, comentario_id=comentario_id, usuario=current_user
    )

@router.get("/{curso_id}/archivos/{filename}")
async def obtener_archivo_adjunto(
    curso_id: str,
    filename: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene un archivo adjunto de un curso."""
    try:
        # Validar acceso al curso
        tiene_acceso = CursoService.validar_acceso_curso(db, curso_id, current_user)
        if not tiene_acceso:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes acceso a este curso",
            )

        # Construir ruta del archivo
        uploads_dir = Path("uploads") / "cursos" / curso_id
        file_path = uploads_dir / filename

        # Verificar que el archivo existe
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado",
            )

        # Determinar tipo MIME
        content_type, _ = mimetypes.guess_type(str(file_path))
        if not content_type:
            content_type = "application/octet-stream"

        # Leer y devolver el archivo
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error obteniendo archivo %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener archivo: {e!s}",
        ) from e

@router.get("/comentarios/{comentario_id}/respuestas")
async def obtener_respuestas_comentario(
    comentario_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Obtiene las respuestas de un comentario específico."""
    return comentario_service.obtener_respuestas(
        db=db,
        comentario_id=comentario_id,
        usuario=current_user,
        limit=limit,
        offset=offset,
    )

@router.post("/comentarios/{comentario_id}/respuestas")
async def crear_respuesta_comentario(
    comentario_id: str,
    respuesta: ComentarioCreateRequest,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Crea una respuesta a un comentario específico."""
    logger.info(f"📨 POST /comentarios/{comentario_id}/respuestas")
    logger.info(f"📨 Datos recibidos: {respuesta.model_dump()}")

    # Validar que el comentario padre existe y el usuario tiene acceso
    comentario_padre = comentario_service.obtener_comentario_por_id(
        db=db, comentario_id=comentario_id, usuario=current_user
    )
    if not comentario_padre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario padre no encontrado"
        )

    # Crear objeto completo para validación
    respuesta_data = respuesta.model_dump()
    respuesta_data['curso_id'] = comentario_padre.get('curso_id')
    respuesta_data['comentario_padre_id'] = comentario_id

    # Intentar recuperar archivos adjuntos desde JSON crudo si no vienen en el modelo
    archivos_raw = respuesta.archivos_adjuntos
    if not archivos_raw:
        try:
            raw = await request.json()
        except Exception:
            raw = {}
        archivos_raw = raw.get('archivos_adjuntos') or raw.get('archivos') or raw.get('files')

    def _normalize_archivos(lst):
        if not lst:
            return None
        normalized = []
        for it in lst:
            if isinstance(it, str):
                normalized.append({'archivo_id': it})
            elif isinstance(it, dict):
                archivo_id = it.get('archivo_id') or it.get('id') or it.get('file_id') or it.get('archivoId')
                if archivo_id:
                    normalized.append({'archivo_id': archivo_id})
        return normalized

    respuesta_data['archivos_adjuntos'] = _normalize_archivos(archivos_raw)

    # Validar con schema completo
    validated_respuesta = ComentarioCreateSchema(**respuesta_data)

    return comentario_service.crear_comentario(
        db=db,
        curso_id=validated_respuesta.curso_id,
        contenido=validated_respuesta.contenido,
        usuario=current_user,
        tipo=validated_respuesta.tipo,
        comentario_padre_id=validated_respuesta.comentario_padre_id,
        archivos_adjuntos=validated_respuesta.archivos_adjuntos,
    )

@router.post("/comentarios/{comentario_id}/reportes")
async def reportar_comentario(
    comentario_id: str,
    reporte: ReporteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Reporta un comentario por contenido inapropiado."""
    logger.info(f"🚨 POST /comentarios/{comentario_id}/reportes")
    logger.info(f"📨 Reporte recibido: {reporte.model_dump()}")

    # Validar que el comentario existe
    comentario = comentario_service.obtener_comentario_por_id(
        db=db, comentario_id=comentario_id, usuario=current_user
    )
    if not comentario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comentario no encontrado"
        )

    # Validar que el usuario no esté reportando su propio comentario
    if comentario.get('autor_id') == current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes reportar tu propio comentario"
        )

    # Aquí iría la lógica para guardar el reporte en la base de datos
    # Por ahora, simulamos el guardado exitoso
    logger.info(f"✅ Reporte registrado: comentario {comentario_id} reportado por usuario {current_user.usuario_id}")

    # En una implementación real, crearíamos un registro en tabla de reportes
    # reporte_data = {
    #     "comentario_id": comentario_id,
    #     "reportado_por": current_user.usuario_id,
    #     "razon": reporte.razon,
    #     "descripcion": reporte.descripcion,
    #     "fecha_reporte": datetime.utcnow(),
    #     "estado": "pendiente"
    # }

    return {
        "success": True,
        "message": "Reporte enviado exitosamente. Será revisado por nuestro equipo.",
        "data": {
            "comentario_id": comentario_id,
            "razon": reporte.razon,
            "reportado_por": f"{current_user.nombres} {current_user.apellidos}",
            "fecha_reporte": "2025-01-01T00:00:00Z",  # Placeholder
            "estado": "pendiente"
        }
    }


# Actualizar comentario (PUT /api/cursos/comentarios/{comentario_id})
@router.put("/comentarios/{comentario_id}")
async def actualizar_comentario_endpoint(
    comentario_id: str,
    payload: ComentarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"🔄 PUT /comentarios/{comentario_id} - actualizar comentario")
    return comentario_service.actualizar_comentario(db=db, comentario_id=comentario_id, nuevo_contenido=payload.contenido, usuario=current_user)


# Eliminar comentario (DELETE /api/cursos/comentarios/{comentario_id})
@router.delete("/comentarios/{comentario_id}")
async def eliminar_comentario_endpoint(
    comentario_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"🔄 DELETE /comentarios/{comentario_id} - eliminar comentario")
    return comentario_service.eliminar_comentario(db=db, comentario_id=comentario_id, usuario=current_user)


# Endpoints para actualizar/eliminar respuestas (mapeadas a los mismos servicios)
@router.put("/respuestas/{respuesta_id}")
async def actualizar_respuesta_endpoint(
    respuesta_id: str,
    payload: ComentarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"🔄 PUT /respuestas/{respuesta_id} - actualizar respuesta")
    return comentario_service.actualizar_comentario(db=db, comentario_id=respuesta_id, nuevo_contenido=payload.contenido, usuario=current_user)


@router.delete("/respuestas/{respuesta_id}")
async def eliminar_respuesta_endpoint(
    respuesta_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logger.info(f"🔄 DELETE /respuestas/{respuesta_id} - eliminar respuesta")
    return comentario_service.eliminar_comentario(db=db, comentario_id=respuesta_id, usuario=current_user)
