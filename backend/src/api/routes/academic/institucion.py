"""Endpoints para gestión de instituciones educativas.

Incluye operaciones CRUD, vinculación de coordinadores,
estadísticas y búsqueda por dominio.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.crud.academic.crud_institucion import institucion_crud
from src.models.users.usuario import Usuario
from src.schemas.academic.institucion import (
    Institucion,
    InstitucionCreate,
    InstitucionUpdate,
)
from src.schemas.academic.institucion_onboarding import (
    InstitucionBrandingUpdate,
    InstitucionDominioAdd,
    InstitucionOnboardingComplete,
    InstitucionOnboardingStatus,
)
from src.services.academic.institucion_service import institucion_service


router = APIRouter()


# ==================== ENDPOINTS BÁSICOS CRUD ====================


@router.get("/", response_model=list[Institucion])
def listar_instituciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Lista todas las instituciones (público).

    - **skip**: Número de registros a saltar (paginación)
    - **limit**: Número máximo de resultados
    """
    return institucion_crud.get_multi(db, skip=skip, limit=limit)


@router.get("/buscar/dominio/{dominio}")
def buscar_por_dominio(dominio: str, db: Session = Depends(get_db)):
    """Busca una institución por su dominio de email.

    - **dominio**: Dominio a buscar (ej: "example.edu")
    """
    institucion = institucion_service.buscar_por_dominio(db, dominio)

    if not institucion:
        return {
            "success": False,
            "message": f"No se encontró institución con dominio '{dominio}'",
            "data": None,
        }

    return {
        "success": True,
        "message": "Institución encontrada",
        "data": {
            "institucion_id": institucion.institucion_id,
            "nombre": institucion.nombre,
            "dominio_principal": institucion.dominio_principal,
            "tipo_institucion": (
                institucion.tipo_institucion.value
                if institucion.tipo_institucion
                else None
            ),
        },
    }


@router.get("/{institucion_id}", response_model=Institucion)
def obtener_institucion(institucion_id: UUID, db: Session = Depends(get_db)):
    """Obtiene una institución por su ID.

    - **institucion_id**: ID de la institución (UUID)
    """
    obj = institucion_crud.get(db, institucion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return obj


# ==================== ENDPOINTS DE COORDINADOR ====================


@router.post("/", response_model=dict)
def crear_institucion(
    obj_in: InstitucionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva institución (solo coordinadores).

    - Se vincula automáticamente al coordinador creador
    - Se extrae el dominio del correo institucional si no está presente
    - Valida que el dominio no exista previamente
    """
    return institucion_service.crear_institucion(db, obj_in, current_user)


@router.get("/mis-instituciones/list")
def obtener_mis_instituciones(
    incluir_estadisticas: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene las instituciones del coordinador actual.

    - **incluir_estadisticas**: Si debe incluir conteos de cursos, docentes, estudiantes
    """
    return institucion_service.obtener_instituciones_coordinador(
        db, current_user, incluir_estadisticas
    )


@router.put("/{institucion_id}", response_model=dict)
def actualizar_institucion(
    institucion_id: UUID,
    obj_in: InstitucionUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una institución (solo coordinadores vinculados).

    - **institucion_id**: ID de la institución (UUID)
    - Valida que el coordinador tenga acceso a la institución
    """
    return institucion_service.actualizar_institucion(
        db, institucion_id, obj_in, current_user
    )


@router.get("/{institucion_id}/estadisticas")
def obtener_estadisticas(
    institucion_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene estadísticas detalladas de una institución.

    - **institucion_id**: ID de la institución (UUID)
    - Total de cursos (activos e inactivos)
    - Total de docentes únicos
    - Total de estudiantes únicos
    - Total de programas
    - Total de coordinadores
    """
    return institucion_service.obtener_estadisticas_institucion(
        db, institucion_id, current_user
    )


@router.post("/{institucion_id}/vincular-usuario")
def vincular_usuario(
    institucion_id: UUID,
    usuario_id: UUID,
    rol: str = Query(
        ..., description="Rol del usuario: coordinador, docente, estudiante"
    ),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Vincula un usuario a una institución.

    - **institucion_id**: ID de la institución (UUID)
    - **usuario_id**: ID del usuario a vincular (UUID)
    - **rol**: Rol del usuario (coordinador, docente, estudiante)

    Nota: Docentes y estudiantes se vinculan a través de cursos/grupos
    """
    return institucion_service.vincular_usuario_institucion(
        db, institucion_id, usuario_id, rol
    )


# ==================== ENDPOINTS DE ONBOARDING ====================


@router.put("/{institucion_id}/onboarding", response_model=dict)
def completar_onboarding(
    institucion_id: UUID,
    data: InstitucionOnboardingComplete,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Completa el onboarding de una institución en un solo paso.

    **Endpoint para coordinadores** que permite completar toda la información
    inicial de la institución después de aceptar la invitación.

    Incluye:
    - Branding (logo, colores)
    - Contacto (dirección, teléfono, website)
    - Redes sociales
    - Configuración académica (jornadas)
    - Dominios adicionales
    - Acreditaciones

    Args:
        institucion_id: ID de la institución (UUID)
        data: Datos completos del onboarding

    Returns:
        Dict con la institución actualizada y estado del onboarding

    Raises:
        HTTPException 403: Si el usuario no es coordinador o no tiene acceso
        HTTPException 404: Si la institución no existe
    """
    return institucion_service.completar_onboarding(
        db, institucion_id, data, current_user
    )


@router.put("/{institucion_id}/branding", response_model=dict)
def actualizar_branding(
    institucion_id: UUID,
    data: InstitucionBrandingUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza el branding visual de la institución.

    **Endpoint para coordinadores** que permite personalizar:
    - Logo institucional
    - Color primario
    - Color secundario

    Args:
        institucion_id: ID de la institución (UUID)
        data: Datos de branding (logo y colores)

    Returns:
        Dict con la institución actualizada

    Raises:
        HTTPException 403: Si el usuario no es coordinador o no tiene acceso
        HTTPException 404: Si la institución no existe
    """
    return institucion_service.actualizar_branding(db, institucion_id, data, current_user)


@router.post("/{institucion_id}/dominios", response_model=dict)
def agregar_dominio_adicional(
    institucion_id: UUID,
    data: InstitucionDominioAdd,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Agrega un dominio adicional a la institución.

    **Endpoint para coordinadores** que permite configurar dominios secundarios
    para registro automático de usuarios.

    Ejemplo: Si la institución principal es "universidad.edu.co",
    puede agregar "estudiantes.universidad.edu.co" para estudiantes.

    Args:
        institucion_id: ID de la institución (UUID)
        data: Dominio a agregar (sin @)

    Returns:
        Dict con la institución actualizada y lista de dominios

    Raises:
        HTTPException 400: Si el dominio ya existe o es inválido
        HTTPException 403: Si el usuario no es coordinador o no tiene acceso
        HTTPException 404: Si la institución no existe
    """
    return institucion_service.agregar_dominio_adicional(
        db, institucion_id, data.dominio, current_user
    )


@router.get("/{institucion_id}/onboarding-status", response_model=InstitucionOnboardingStatus)
def obtener_estado_onboarding(
    institucion_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene el estado actual del onboarding de una institución.

    **Endpoint para coordinadores** que muestra qué pasos del onboarding
    han sido completados y cuáles faltan.

    Útil para mostrar progreso en el frontend y guiar al coordinador.

    Args:
        institucion_id: ID de la institución (UUID)

    Returns:
        InstitucionOnboardingStatus con:
        - onboarding_completo: boolean
        - pasos_completados: dict de pasos
        - pasos_faltantes: lista de pasos
        - porcentaje_completado: int (0-100)

    Raises:
        HTTPException 403: Si el usuario no es coordinador o no tiene acceso
        HTTPException 404: Si la institución no existe
    """
    return institucion_service.obtener_estado_onboarding(
        db, institucion_id, current_user
    )


# ==================== ENDPOINT DE ELIMINACIÓN ====================


@router.delete("/{institucion_id}", response_model=Institucion)
def eliminar_institucion(
    institucion_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Elimina una institución (solo coordinadores vinculados).

    - **institucion_id**: ID de la institución (UUID)

    ADVERTENCIA: Esta operación puede afectar cursos, programas y usuarios vinculados
    """
    # Verificar que sea coordinador
    if current_user.rol != "coordinador":
        raise HTTPException(
            status_code=403, detail="Solo coordinadores pueden eliminar instituciones"
        )

    obj = institucion_crud.remove(db, institucion_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return obj
