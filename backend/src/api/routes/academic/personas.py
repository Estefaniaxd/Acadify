"""Endpoints para gestión de personas y perfiles.

Incluye listado de personas en cursos y perfiles de usuario completos.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.models.users.usuario import Usuario
from src.services.academic.personas_service import personas_service


router = APIRouter()


@router.get("/cursos/{curso_id}/personas")
def obtener_personas_curso(
    curso_id: str,
    rol: str | None = Query(None, description="Filtro por rol: docente, estudiante"),
    busqueda: str | None = Query(None, description="Búsqueda por nombre"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene las personas asociadas a un curso.

    - **curso_id**: ID del curso
    - **rol**: Filtro opcional por rol (docente, estudiante)
    - **busqueda**: Búsqueda por nombre (ILIKE)
    - **skip**: Offset para paginación
    - **limit**: Límite de resultados (max 100)

    Retorna:
    - Lista de personas con información básica
    - Total de resultados
    - Metadatos de paginación
    """
    return personas_service.obtener_personas_curso(
        db,
        curso_id,
        rol_filtro=rol,
        busqueda=busqueda,
        usuario_actual=current_user,
        skip=skip,
        limit=limit,
    )


@router.get("/users/{usuario_id}/perfil")
def obtener_perfil_usuario(
    usuario_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene el perfil completo de un usuario.

    - **usuario_id**: ID del usuario

    Retorna:
    - Información básica del usuario
    - Información específica según rol (docente, estudiante, coordinador)
    - Cursos activos (máximo 10)
    - Actividad reciente (últimas 5 acciones)

    El perfil incluye:
    - **Docente**: horario_atencion, especialidad, total_cursos
    - **Estudiante**: fecha_ingreso, codigo_estudiantil, total_cursos
    - **Coordinador**: horario_atencion, total_instituciones
    """
    return personas_service.obtener_perfil_usuario(db, usuario_id, current_user)


@router.get("/users/me/perfil")
def obtener_mi_perfil(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
):
    """Obtiene el perfil del usuario actual.

    Equivalente a GET /users/{usuario_id}/perfil con el ID del usuario actual.
    """
    return personas_service.obtener_perfil_usuario(
        db, str(current_user.usuario_id), current_user
    )
