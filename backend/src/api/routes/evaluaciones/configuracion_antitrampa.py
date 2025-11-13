"""API Routes para gestionar configuraciones del sistema anti-trampa.
Endpoints para CRUD, perfiles, plantillas, importar/exportar.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, get_db
from src.models.evaluaciones.configuracion_antitrampa import (
    NivelSeguridad,
    TipoConfiguracion,
)
from src.models.usuario import Usuario
from src.schemas.evaluaciones.configuracion import (
    AplicarPlantillaRequest,
    ConfiguracionAntiTrampaCreate,
    ConfiguracionAntiTrampaResponse,
    ConfiguracionAntiTrampaUpdate,
    ExportarConfiguracionResponse,
    ImportarConfiguracionRequest,
    PerfilSeguridadResponse,
    PlantillaConfiguracionCreate,
    PlantillaConfiguracionResponse,
)
from src.services.evaluaciones.configuracion_service import (
    ConfiguracionAntiTrampaService,
)


router = APIRouter()


# ==========================================
# CRUD BÁSICO DE CONFIGURACIONES
# ==========================================


@router.post(
    "/",
    response_model=ConfiguracionAntiTrampaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear configuración anti-trampa",
    description="Crea una nueva configuración del sistema anti-trampa. Requiere rol docente o coordinador.",
)
async def crear_configuracion(
    config_data: ConfiguracionAntiTrampaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva configuración del sistema anti-trampa."""
    # Verificar permisos (solo docente/coordinador/admin)
    if current_user.rol not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear configuraciones",
        )

    try:
        return ConfiguracionAntiTrampaService.crear_configuracion(
            db=db, config_data=config_data, creado_por_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear configuración: {e!s}",
        ) from e


@router.get(
    "/{config_id}",
    response_model=ConfiguracionAntiTrampaResponse,
    summary="Obtener configuración",
    description="Obtiene una configuración específica por ID",
)
async def obtener_configuracion(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene una configuración específica."""
    config = ConfiguracionAntiTrampaService.obtener_configuracion(db, config_id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    return config


@router.put(
    "/{config_id}",
    response_model=ConfiguracionAntiTrampaResponse,
    summary="Actualizar configuración",
    description="Actualiza una configuración existente. Solo el creador o admin puede actualizar.",
)
async def actualizar_configuracion(
    config_id: UUID,
    config_update: ConfiguracionAntiTrampaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una configuración existente."""
    # Verificar que la configuración existe
    config_existente = ConfiguracionAntiTrampaService.obtener_configuracion(
        db, config_id
    )
    if not config_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    # Verificar permisos (creador o admin)
    if (
        config_existente.creado_por_id != current_user.id
        and current_user.rol != "administrador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para actualizar esta configuración",
        )

    try:
        return ConfiguracionAntiTrampaService.actualizar_configuracion(
            db=db, config_id=config_id, config_update=config_update
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar configuración: {e!s}",
        ) from e


@router.delete(
    "/{config_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar configuración",
    description="Elimina una configuración. Solo el creador o admin puede eliminar.",
)
async def eliminar_configuracion(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
) -> None:
    """Elimina una configuración."""
    config_existente = ConfiguracionAntiTrampaService.obtener_configuracion(
        db, config_id
    )
    if not config_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    if (
        config_existente.creado_por_id != current_user.id
        and current_user.rol != "administrador"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para eliminar esta configuración",
        )

    eliminada = ConfiguracionAntiTrampaService.eliminar_configuracion(db, config_id)
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al eliminar configuración",
        )


# ==========================================
# CONFIGURACIÓN EFECTIVA CON HERENCIA
# ==========================================


@router.get(
    "/efectiva/{tipo}/{entidad_id}",
    response_model=dict,
    summary="Obtener configuración efectiva",
    description="""
    Obtiene la configuración efectiva para una entidad aplicando herencia jerárquica.
    Jerarquía: Global → Institución → Curso → Examen → Estudiante
    """,
)
async def obtener_configuracion_efectiva(
    tipo: TipoConfiguracion,
    entidad_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene la configuración efectiva después de aplicar herencia.
    Devuelve también el origen de cada valor (propio, heredado, default).
    """
    try:
        return ConfiguracionAntiTrampaService.obtener_configuracion_efectiva(
            db=db, tipo=tipo, entidad_id=entidad_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener configuración efectiva: {e!s}",
        ) from e


# ==========================================
# PERFILES PREDEFINIDOS
# ==========================================


@router.get(
    "/perfiles/sistema",
    response_model=list[PerfilSeguridadResponse],
    summary="Obtener perfiles del sistema",
    description="Devuelve los 4 perfiles predefinidos: Bajo, Medio, Alto, Máximo",
)
async def obtener_perfiles_sistema(current_user: Usuario = Depends(get_current_user)):
    """Obtiene los perfiles predefinidos del sistema."""
    return ConfiguracionAntiTrampaService.obtener_perfiles_sistema()


@router.post(
    "/perfiles/aplicar",
    response_model=ConfiguracionAntiTrampaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Aplicar perfil predefinido",
    description="Aplica un perfil predefinido del sistema a una entidad (examen, curso, etc.)",
)
async def aplicar_perfil(
    nivel: NivelSeguridad = Query(..., description="Nivel de seguridad del perfil"),
    tipo: TipoConfiguracion = Query(..., description="Tipo de entidad destino"),
    entidad_id: UUID = Query(..., description="ID de la entidad destino"),
    nombre_config: str | None = Query(None, description="Nombre personalizado"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Aplica un perfil predefinido a una entidad."""
    if current_user.rol not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para aplicar perfiles",
        )

    try:
        return ConfiguracionAntiTrampaService.aplicar_perfil(
            db=db,
            nivel=nivel,
            tipo=tipo,
            entidad_id=entidad_id,
            creado_por_id=current_user.id,
            nombre_config=nombre_config,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aplicar perfil: {e!s}",
        ) from e


# ==========================================
# PLANTILLAS
# ==========================================


@router.post(
    "/plantillas",
    response_model=PlantillaConfiguracionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear plantilla",
    description="Crea una plantilla reutilizable desde una configuración",
)
async def crear_plantilla(
    plantilla_data: PlantillaConfiguracionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una plantilla reutilizable."""
    if current_user.rol not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para crear plantillas",
        )

    try:
        return ConfiguracionAntiTrampaService.crear_plantilla(
            db=db,
            nombre=plantilla_data.nombre,
            descripcion=plantilla_data.descripcion,
            nivel_seguridad=plantilla_data.nivel_seguridad,
            configuracion_base=plantilla_data.configuracion_base,
            creado_por_id=current_user.id,
            institucion_id=current_user.institucion_id,
            es_publica=plantilla_data.es_publica,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear plantilla: {e!s}",
        ) from e


@router.post(
    "/plantillas/aplicar",
    response_model=ConfiguracionAntiTrampaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Aplicar plantilla",
    description="Aplica una plantilla existente a una entidad",
)
async def aplicar_plantilla(
    request: AplicarPlantillaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Aplica una plantilla a una entidad."""
    if current_user.rol not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para aplicar plantillas",
        )

    try:
        return ConfiguracionAntiTrampaService.aplicar_plantilla(
            db=db,
            plantilla_id=request.plantilla_id,
            tipo=request.tipo_destino,
            entidad_id=request.destino_id,
            creado_por_id=current_user.id,
            sobrescribir=request.sobrescribir_existente,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aplicar plantilla: {e!s}",
        ) from e


# ==========================================
# IMPORTAR/EXPORTAR
# ==========================================


@router.get(
    "/exportar/{config_id}",
    response_model=ExportarConfiguracionResponse,
    summary="Exportar configuración",
    description="Exporta una configuración a formato JSON portable",
)
async def exportar_configuracion(
    config_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta una configuración a JSON."""
    config_existente = ConfiguracionAntiTrampaService.obtener_configuracion(
        db, config_id
    )
    if not config_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Configuración no encontrada"
        )

    try:
        return ConfiguracionAntiTrampaService.exportar_configuracion(
            db=db, config_id=config_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al exportar configuración: {e!s}",
        ) from e


@router.post(
    "/importar",
    response_model=ConfiguracionAntiTrampaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Importar configuración",
    description="Importa una configuración desde JSON exportado",
)
async def importar_configuracion(
    request: ImportarConfiguracionRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Importa una configuración desde JSON."""
    if current_user.rol not in ["docente", "coordinador", "administrador"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para importar configuraciones",
        )

    try:
        return ConfiguracionAntiTrampaService.importar_configuracion(
            db=db,
            datos_exportados=request.datos_exportados,
            tipo_destino=request.tipo_destino,
            destino_id=request.destino_id,
            nombre_config=request.nombre_config,
            creado_por_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al importar configuración: {e!s}",
        ) from e
