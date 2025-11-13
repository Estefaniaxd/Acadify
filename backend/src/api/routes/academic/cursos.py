"""Rutas de API para gestión básica de cursos - REFACTORIZADO.

Thin controllers usando curso_service
SOLID + Clean Code: Rutas simples delegando lógica a services
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api import deps
from src.models.users.usuario import Usuario
from src.models.academic.curso import Curso as CursoModel
from src.services.academic.curso_service import curso_service
from src.crud.academic.crud_curso import CRUDCurso
from src.schemas.academic.curso import Curso, CursoCreate, CursoUpdate
from src.api.routes.academic.inscripciones import router as inscripciones_router


# Configuración
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cursos")
curso_crud = CRUDCurso(CursoModel)


# ==================== ENDPOINTS CURSOS ====================


@router.get("/mis-cursos")
async def get_mis_cursos(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene cursos del usuario según su rol:
    - Estudiante: cursos inscritos
    - Docente: cursos que imparte
    - Coordinador: todos los cursos.
    """
    logger.info(
        f"GET mis-cursos - Usuario: {current_user.usuario_id} ({current_user.rol})"
    )
    return curso_service.obtener_cursos_usuario(
        db=db, usuario=current_user, limit=limit, offset=offset
    )


@router.get("/disponibles")
async def get_cursos_disponibles(
    institucion_id: str | None = None,
    area: str | None = None,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene cursos disponibles para inscripción."""
    logger.info(f"GET cursos disponibles - Usuario: {current_user.usuario_id}")
    return curso_service.obtener_cursos_disponibles(
        db=db,
        usuario=current_user,
        institucion_id=institucion_id,
        area=area,
        limit=limit,
        offset=offset,
    )


@router.get("/{curso_id}")
async def get_curso_detalle(
    curso_id: str,
    current_user: Usuario = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """Obtiene detalles completos de un curso."""
    logger.info(f"GET curso {curso_id} - Usuario: {current_user.usuario_id}")
    return curso_service.obtener_detalle_curso(
        db=db, curso_id=curso_id, usuario=current_user
    )


# ==================== ENDPOINTS CRUD ====================


@router.post("/", response_model=Curso)
def crear_curso(
    obj_in: CursoCreate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user),
) -> Curso:
    """Crea un nuevo curso (coordinadores)."""
    logger.info(f"POST crear curso - Usuario: {current_user.usuario_id}")
    
    # Asignar coordinador_id si no viene en el request
    if not obj_in.coordinador_id:
        obj_in.coordinador_id = current_user.usuario_id
    
    # Crear curso con código de acceso único
    curso = curso_crud.create(db, obj_in)
    
    # Generar código de acceso si no tiene
    if not curso.codigo_acceso:
        codigo_acceso = curso_crud.generar_codigo_acceso_unico(db)
        curso.codigo_acceso = codigo_acceso
        db.commit()
        db.refresh(curso)
    
    return curso


@router.put("/{curso_id}", response_model=Curso)
def actualizar_curso(
    curso_id: UUID,
    obj_in: CursoUpdate,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user),
) -> Curso:
    """Actualiza un curso existente (coordinadores)."""
    logger.info(f"PUT actualizar curso {curso_id} - Usuario: {current_user.usuario_id}")
    
    db_obj = curso_crud.get(db, curso_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    return curso_crud.update(db, db_obj, obj_in)


@router.delete("/{curso_id}", response_model=Curso)
def eliminar_curso(
    curso_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user),
) -> Curso:
    """Elimina un curso (coordinadores)."""
    logger.info(f"DELETE curso {curso_id} - Usuario: {current_user.usuario_id}")
    
    obj = curso_crud.remove(db, curso_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    return obj


# Incluir router de inscripciones
router.include_router(inscripciones_router, prefix="/inscripciones", tags=["Inscripciones"])
