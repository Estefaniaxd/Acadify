"""Rutas de API para archivos - REFACTORIZADO."""

import logging

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from src.api import deps
from src.models.users.usuario import Usuario
from src.services.academic.archivo_service import archivo_service


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos/archivos")


@router.post("/{curso_id}/subir")
async def subir_archivo(
    curso_id: str,
    archivo: UploadFile = File(...),
    descripcion: str | None = Form(None),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return await archivo_service.subir_archivo(
        db=db,
        curso_id=curso_id,
        archivo=archivo,
        descripcion=descripcion,
        usuario=current_user,
    )


@router.get("/{curso_id}/archivos")
async def obtener_archivos(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return archivo_service.obtener_archivos_curso(
        db=db, curso_id=curso_id, usuario=current_user
    )


@router.get("/descargar/{archivo_id}")
async def descargar_archivo(
    archivo_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return archivo_service.descargar_archivo(
        db=db, archivo_id=archivo_id, usuario=current_user
    )


@router.delete("/{archivo_id}")
async def eliminar_archivo(
    archivo_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    return archivo_service.eliminar_archivo(
        db=db, archivo_id=archivo_id, usuario=current_user
    )
