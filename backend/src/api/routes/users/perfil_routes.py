"""Rutas para gestión de personalización de perfil."""

from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user, get_db
from src.models.users.usuario import Usuario
from src.schemas.users.perfil_schemas import (
    BannerUpdate,
    MarcoPerfilUpdate,
    PerfilPersonalizacionResponse,
    UploadResponse,
)
from src.services.users.perfil_service import PerfilService


router = APIRouter(prefix="/perfil", tags=["Perfil - Personalización"])


@router.get(
    "/personalizacion",
    response_model=PerfilPersonalizacionResponse,
    summary="Obtener personalización del perfil",
)
async def obtener_personalizacion(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene toda la personalización del perfil del usuario actual.

    Incluye:
    - Foto de perfil (custom o avatar)
    - Banner/portada
    - Marco de perfil
    """
    service = PerfilService(db)
    return await service.obtener_personalizacion(current_user.usuario_id)


@router.post(
    "/foto-perfil/upload",
    response_model=UploadResponse,
    summary="Subir foto de perfil custom",
)
async def upload_foto_perfil(
    file: UploadFile = File(
        ..., description="Imagen de perfil (máx 5MB, JPG/PNG/WEBP)"
    ),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sube una foto de perfil custom.

    - **file**: Imagen (JPG, PNG, WEBP)
    - **Tamaño máximo**: 5MB
    - **Se redimensiona automáticamente**: Máx 800x800px
    - **Activa automáticamente**: La foto custom se activa al subirla
    """
    service = PerfilService(db)
    url = await service.upload_foto_perfil(current_user.usuario_id, file)

    return UploadResponse(
        success=True, url=url, message="Foto de perfil subida y activada correctamente"
    )


@router.post("/foto-perfil/usar-avatar", summary="Cambiar a avatar")
async def cambiar_a_avatar(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cambia de foto custom a avatar.

    El avatar se genera desde el editor de avatares.
    """
    service = PerfilService(db)
    return await service.cambiar_a_avatar(current_user.usuario_id)


@router.post("/foto-perfil/usar-custom", summary="Cambiar a foto custom")
async def cambiar_a_foto_custom(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cambia de avatar a foto custom.

    Requiere haber subido una foto previamente.
    """
    service = PerfilService(db)
    return await service.cambiar_a_foto_custom(current_user.usuario_id)


@router.post(
    "/banner/upload",
    response_model=UploadResponse,
    summary="Subir banner/portada custom",
)
async def upload_banner(
    file: UploadFile = File(..., description="Banner/portada (máx 10MB, JPG/PNG/WEBP)"),
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Sube un banner/portada custom.

    - **file**: Imagen (JPG, PNG, WEBP)
    - **Tamaño máximo**: 10MB
    - **Se redimensiona automáticamente**: Máx 1920x400px
    - **Recomendado**: Relación de aspecto 16:3
    """
    service = PerfilService(db)
    url = await service.upload_banner(current_user.usuario_id, file)

    return UploadResponse(success=True, url=url, message="Banner subido correctamente")


@router.post("/banner/equipar", summary="Equipar banner de la tienda")
async def equipar_banner_tienda(
    banner_update: BannerUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Equipa un banner comprado en la tienda.

    - **banner_activo_id**: ID del item (null para quitar)
    - **Requiere**: Tener el item en el inventario
    """
    service = PerfilService(db)
    return await service.equipar_banner_tienda(
        current_user.usuario_id, banner_update.banner_activo_id
    )


@router.post("/marco/equipar", summary="Equipar marco de perfil")
async def equipar_marco_perfil(
    marco_update: MarcoPerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Equipa un marco de perfil comprado en la tienda.

    - **marco_perfil_id**: ID del item (null para quitar)
    - **Requiere**: Tener el item en el inventario
    """
    service = PerfilService(db)
    return await service.equipar_marco_perfil(
        current_user.usuario_id, marco_update.marco_perfil_id
    )


@router.get(
    "/{usuario_id}/personalizacion",
    response_model=PerfilPersonalizacionResponse,
    summary="Obtener personalización de otro usuario (público)",
)
async def obtener_personalizacion_publico(
    usuario_id: UUID, db: AsyncSession = Depends(get_db)
):
    """Obtiene la personalización del perfil de cualquier usuario.

    **Endpoint público** para ver perfiles de otros usuarios.
    """
    service = PerfilService(db)
    return await service.obtener_personalizacion(usuario_id)
