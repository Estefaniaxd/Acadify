"""Rutas API para el sistema de avatars."""

import contextlib
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, require_admin
from src.api.deps import get_db
from src.models.users.usuario import Usuario
from src.schemas.avatar import (
    CacheStatsResponse,
    ManifestResponse,
    PreviewRequest,
    PreviewResponse,
    SaveAvatarRequest,
    UpdateAvatarRequest,
    UserAvatarListResponse,
    UserAvatarResponse,
    UserStatsResponse,
)
from src.services.avatar_service import avatar_service


router = APIRouter()


# Handler específico para OPTIONS en rutas de avatar
@router.options("/assets")
@router.options("/preview")
@router.options("/save")
@router.options("/me")
@router.options("/{path:path}")
async def avatar_options_handler(path: str = ""):
    """Maneja peticiones OPTIONS para todas las rutas de avatar."""
    return {"message": "OK"}


# Inicializar conexión Redis al importar el módulo
# (mejor práctica que eventos startup/shutdown que pueden fallar)
with contextlib.suppress(Exception):
    avatar_service.connect_redis()


# Endpoint de test simple para verificar CORS
@router.get("/test-cors")
async def test_cors():
    """Endpoint simple para probar CORS sin dependencias."""
    return {"message": "CORS working!", "timestamp": "2025-09-23"}


@router.get(
    "/assets",
    response_model=ManifestResponse,
    summary="Obtener manifest de assets",
    description="Retorna todas las categorías y archivos de assets disponibles para construcción de avatars.",
)
async def get_assets_manifest(
    gender: str | None = None, db: Session = Depends(get_db)
) -> ManifestResponse:
    """Obtiene el manifest completo de assets disponibles.

    Args:
        gender: Filtrar por género (male, female) o None para todos

    Este endpoint es público y no requiere autenticación para permitir
    que los usuarios vean las opciones antes de registrarse.
    """
    try:
        if gender and gender in ["male", "female"]:
            manifest = await avatar_service.get_manifest_for_gender(db, gender)
        else:
            manifest = await avatar_service.get_manifest(db)
        return ManifestResponse(**manifest)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading assets manifest: {e!s}",
        ) from e


@router.post(
    "/preview",
    response_model=PreviewResponse,
    summary="Generar preview de avatar",
    description="Genera un preview temporal del avatar sin guardarlo. Útil para mostrar en tiempo real mientras el usuario selecciona capas.",
)
async def generate_avatar_preview(
    request: PreviewRequest, db: Session = Depends(get_db)
) -> PreviewResponse:
    """Genera preview de avatar sin guardarlo.

    Este endpoint puede ser público o requerir autenticación según la configuración.
    El preview se cachea temporalmente para mejorar performance.
    """
    try:
        # Convertir LayerItem objects a diccionarios
        layers_dict = [layer.model_dump() for layer in request.layers]
        preview_data = await avatar_service.generate_preview(
            db, request.base_gender, layers_dict
        )
        return PreviewResponse(**preview_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating preview: {e!s}",
        ) from e


@router.post(
    "/save",
    response_model=UserAvatarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar avatar permanentemente",
    description="Guarda un avatar permanentemente para el usuario autenticado. Compone la imagen final y la almacena.",
)
async def save_avatar(
    request: SaveAvatarRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserAvatarResponse:
    """Guarda un avatar permanentemente para el usuario.

    - Compone la imagen final de todas las capas
    - Almacena el archivo en el sistema de archivos
    - Guarda la configuración en base de datos
    - Opcionalmente lo marca como avatar activo
    """
    try:
        avatar = await avatar_service.save_avatar(
            db=db,
            user_id=current_user.usuario_id,
            name=request.name,
            base_gender=request.base_gender,
            layers=[layer.model_dump() for layer in request.layers],
            is_active=request.is_active,
            is_public=request.is_public,
        )

        # Convertir a response format
        return UserAvatarResponse(
            id=str(avatar.id),
            user_id=str(avatar.user_id),
            name=avatar.name,
            base_gender=avatar.base_gender,
            layers=avatar.layers,
            image_url=avatar.image_url,
            layers_hash=avatar.layers_hash,
            is_active=avatar.is_active,
            is_public=avatar.is_public,
            created_at=avatar.created_at,
            updated_at=avatar.updated_at,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving avatar: {e!s}",
        ) from e


@router.get(
    "/user/{user_id}",
    response_model=UserAvatarListResponse,
    summary="Obtener avatars de usuario",
    description="Retorna todos los avatars de un usuario específico. Solo el propietario o admins pueden acceder.",
)
async def get_user_avatars(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserAvatarListResponse:
    """Obtiene avatars de un usuario específico.

    Los usuarios solo pueden ver sus propios avatars,
    los administradores pueden ver avatars de cualquier usuario.
    """
    print(f"🔍 [get_user_avatars] Requested user_id: {user_id}, Current user: {current_user.usuario_id} ({current_user.nombres})")
    # Verificar permisos
    if current_user.usuario_id != user_id and str(current_user.rol) != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los avatars de este usuario",
        )

    try:
        from src.crud.avatar import crud_user_avatar

        # Obtener avatars
        avatars = crud_user_avatar.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

        # Obtener estadísticas
        stats = crud_user_avatar.get_user_stats(db, user_id=user_id)

        # Convertir a response format
        avatar_responses = [
            UserAvatarResponse(
                id=str(avatar.id),
                user_id=str(avatar.user_id),
                name=avatar.name,
                base_gender=avatar.base_gender,
                layers=avatar.layers,
                image_url=avatar.image_url,
                layers_hash=avatar.layers_hash,
                is_active=avatar.is_active,
                is_public=avatar.is_public,
                created_at=avatar.created_at,
                updated_at=avatar.updated_at,
            )
            for avatar in avatars
        ]

        return UserAvatarListResponse(
            avatars=avatar_responses,
            total=stats["total_avatars"],
            has_active=stats["has_active_avatar"],
            active_avatar_id=(
                str(stats["active_avatar_id"]) if stats["active_avatar_id"] else None
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user avatars: {e!s}",
        ) from e


@router.get(
    "/me",
    response_model=UserAvatarListResponse,
    summary="Obtener mis avatars",
    description="Retorna todos los avatars del usuario autenticado.",
)
async def get_my_avatars(
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserAvatarListResponse:
    """Obtiene avatars del usuario autenticado."""
    print(f"👤 [get_my_avatars] Current user: {current_user.usuario_id} ({current_user.nombres} - {current_user.rol})")
    return await get_user_avatars(
        user_id=current_user.usuario_id,
        skip=skip,
        limit=limit,
        current_user=current_user,
        db=db,
    )


@router.put(
    "/{avatar_id}",
    response_model=UserAvatarResponse,
    summary="Actualizar avatar",
    description="Actualiza nombre, privacidad o estado activo de un avatar existente.",
)
async def update_avatar(
    avatar_id: UUID,
    request: UpdateAvatarRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserAvatarResponse:
    """Actualiza un avatar existente.

    Solo el propietario puede actualizar sus avatars.
    """
    try:
        from src.crud.avatar import crud_user_avatar

        # Verificar que el avatar pertenece al usuario
        avatar = crud_user_avatar.get(db, id=avatar_id)
        if not avatar or avatar.user_id != current_user.usuario_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar no encontrado o no tienes permisos",
            )

        # Preparar datos de actualización
        update_data = {}
        if request.name is not None:
            update_data["name"] = request.name
        if request.is_public is not None:
            update_data["is_public"] = request.is_public

        # Manejar is_active especialmente
        if request.is_active is not None and request.is_active:
            # Activar este avatar (desactiva otros automáticamente)
            avatar = crud_user_avatar.set_active_avatar(
                db, user_id=current_user.usuario_id, avatar_id=avatar_id
            )
        elif request.is_active is not None and not request.is_active:
            update_data["is_active"] = False

        # Aplicar otras actualizaciones si las hay
        if update_data:
            avatar = crud_user_avatar.update(db, db_obj=avatar, obj_in=update_data)

        return UserAvatarResponse(
            id=str(avatar.id),
            user_id=str(avatar.user_id),
            name=avatar.name,
            base_gender=avatar.base_gender,
            layers=avatar.layers,
            image_url=avatar.image_url,
            layers_hash=avatar.layers_hash,
            is_active=avatar.is_active,
            is_public=avatar.is_public,
            created_at=avatar.created_at,
            updated_at=avatar.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating avatar: {e!s}",
        ) from e


@router.delete(
    "/{avatar_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar avatar",
    description="Elimina un avatar y su archivo asociado. Solo el propietario puede eliminar sus avatars.",
)
async def delete_avatar(
    avatar_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Elimina un avatar permanentemente.

    - Elimina el registro de la base de datos
    - Elimina el archivo de imagen (si no es usado por otros avatars)
    - Limpia el cache asociado
    """
    try:
        deleted = await avatar_service.delete_avatar(
            db=db, user_id=current_user.usuario_id, avatar_id=avatar_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avatar no encontrado o no tienes permisos",
            )

        return  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting avatar: {e!s}",
        ) from e


@router.get(
    "/stats/user",
    response_model=UserStatsResponse,
    summary="Estadísticas de avatars del usuario",
    description="Retorna estadísticas de los avatars del usuario autenticado.",
)
async def get_user_avatar_stats(
    current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
) -> UserStatsResponse:
    """Obtiene estadísticas de avatars del usuario."""
    try:
        from src.crud.avatar import crud_user_avatar

        stats = crud_user_avatar.get_user_stats(db, user_id=current_user.usuario_id)

        return UserStatsResponse(
            total_avatars=stats["total_avatars"],
            public_avatars=stats["public_avatars"],
            private_avatars=stats["private_avatars"],
            has_active_avatar=stats["has_active_avatar"],
            active_avatar_id=(
                str(stats["active_avatar_id"]) if stats["active_avatar_id"] else None
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user stats: {e!s}",
        ) from e


@router.get(
    "/stats/cache",
    response_model=CacheStatsResponse,
    summary="Estadísticas del cache",
    description="Retorna estadísticas del cache Redis de avatars. Solo admins.",
    dependencies=[Depends(require_admin)],
)
async def get_cache_stats() -> CacheStatsResponse:
    """Obtiene estadísticas del cache de avatars (solo admins)."""
    try:
        stats = avatar_service.get_cache_stats()

        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=stats["error"]
            )

        return CacheStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting cache stats: {e!s}",
        ) from e


@router.post(
    "/maintenance/cleanup-previews",
    summary="Limpiar previews temporales",
    description="Limpia archivos de preview temporales antiguos. Solo admins.",
    dependencies=[Depends(require_admin)],
)
async def cleanup_temp_previews(
    background_tasks: BackgroundTasks, max_age_hours: int = 24
):
    """Limpia previews temporales antiguos (solo admins).

    Ejecuta la limpieza en background para no bloquear la respuesta.
    """
    try:
        # Ejecutar limpieza en background
        background_tasks.add_task(
            avatar_service.cleanup_temp_previews, max_age_hours=max_age_hours
        )

        return {"message": "Cleanup scheduled", "max_age_hours": max_age_hours}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scheduling cleanup: {e!s}",
        ) from e
