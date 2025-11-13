# src/api/routes/auth/auth_users.py

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
import redis.asyncio as redis
from sqlalchemy.orm import Session

from src.api.deps import get_current_active_user, get_db, get_redis_client
from src.models.users.usuario import Usuario
from src.schemas.auth.auth_schemas import (
    MessageResponse,
    UserCurrentResponse,
    UserProfileUpdate,
)
from src.schemas.users.usuario import UsuarioCreate
from src.services.auth.auth_service import AuthService


logger = logging.getLogger(__name__)

# Router de gestión de usuarios (solo administradores)
router = APIRouter(
    prefix="/auth/users",
    tags=["👥 Autenticación - Gestión de Usuarios (Admin)"],
    responses={
        401: {"description": "Token inválido o usuario no autenticado"},
        403: {"description": "Solo administradores pueden acceder"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"},
    },
)

ERROR_INTERNO_SERVIDOR = "Error interno del servidor"
USUARIO_NO_ENCONTRADO = "Usuario no encontrado"


def _verify_admin_permissions(current_user: Usuario) -> None:
    """Verificar que el usuario actual es administrador."""
    if current_user.rol.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden realizar esta acción",
        )


@router.post(
    "", response_model=UserCurrentResponse, status_code=status.HTTP_201_CREATED
)
async def create_user_by_admin(
    *,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client),
    user_data: UsuarioCreate,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Crear usuario (solo administradores).

    **Permisos requeridos:** Rol administrador

    **Funcionalidad:**
    - Administradores pueden crear usuarios de cualquier rol
    - Aplican las mismas validaciones que registro público
    - Usuario creado queda activo inmediatamente

    **Validaciones:**
    - Todas las validaciones de registro estándar
    - Verificación de permisos de administrador
    - Constraints de base de datos (emails, usernames únicos)

    **Casos de uso:**
    - Registro masivo de usuarios
    - Creación de cuentas institucionales
    - Gestión administrativa de usuarios

    **Respuestas:**
    - 201: Usuario creado exitosamente
    - 400: Datos inválidos o duplicados
    - 403: Permisos insuficientes
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)

    auth_service = AuthService(redis_client)

    try:
        new_user = await auth_service.register_user(db, user_data)
        return UserCurrentResponse.model_validate(new_user)
    except Exception as e:
        logger.exception(f"Error creando usuario (admin): {e}")
        raise


@router.get("", response_model=list[UserCurrentResponse])
async def list_users(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    role: str | None = None,
    search: str | None = None,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Listar usuarios con paginación y filtros (solo administradores).

    **Permisos requeridos:** Rol administrador

    **Parámetros de consulta:**
    - skip: Número de registros a saltar (paginación)
    - limit: Máximo número de registros (default: 100, max: 1000)
    - role: Filtrar por rol específico (administrador, coordinador, docente, estudiante)
    - search: Buscar por nombre, email o número de documento

    **Filtros disponibles:**
    - **Por rol**: role=administrador, role=estudiante, etc.
    - **Por texto**: search="Juan" busca en nombres, apellidos, emails y documentos
    - **Combinados**: Puede combinar role y search

    **Ordenamiento:** Por fecha de creación (más recientes primero)

    **Respuestas:**
    - 200: Lista de usuarios (puede estar vacía)
    - 400: Parámetros inválidos (rol no existe)
    - 403: Permisos insuficientes
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)

    try:
        from src.crud.user.usuario import usuario_crud
        from src.enums.users.usuario_enums import RolUsuario

        if search:
            # Buscar usuarios por texto
            role_filter = None
            if role:
                try:
                    role_filter = RolUsuario(role)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido"
                    ) from None

            users = usuario_crud.search_users(
                db, query=search, role=role_filter, skip=skip, limit=limit
            )
        elif role:
            # Filtrar por rol
            try:
                role_filter = RolUsuario(role)
                users = usuario_crud.get_users_by_role(
                    db, rol=role_filter, skip=skip, limit=limit
                )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Rol inválido"
                ) from None
        else:
            # Listar todos los usuarios activos
            users = usuario_crud.get_active_users(db, skip=skip, limit=limit)

        return [UserCurrentResponse.model_validate(user) for user in users]

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listando usuarios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR,
        ) from e


@router.get("/{user_id}", response_model=UserCurrentResponse)
async def get_user_by_id(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Obtener usuario por ID (solo administradores).

    **Permisos requeridos:** Rol administrador

    **Funcionalidad:**
    - Acceso completo a información de cualquier usuario
    - Incluye datos sensibles (configuración 2FA, estado cuenta)
    - Útil para gestión administrativa detallada

    **Información incluida:**
    - Datos personales completos
    - Estado de cuenta y configuraciones
    - Fechas de registro y último acceso
    - Configuración de seguridad (2FA)
    - Información de contacto

    **Respuestas:**
    - 200: Información del usuario
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)

    try:
        from src.crud.user.usuario import usuario_crud

        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
            )

        return UserCurrentResponse.model_validate(user)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error obteniendo usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR,
        ) from e


@router.put("/{user_id}", response_model=UserCurrentResponse)
async def update_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    user_update: UserProfileUpdate,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Actualizar usuario por ID (solo administradores).

    **Permisos requeridos:** Rol administrador

    **Campos actualizables:**
    - nombres: Nombres completos
    - apellidos: Apellidos completos
    - telefono: Número de teléfono
    - descripcion: Descripción o biografía

    **Campos protegidos:** (no actualizables via este endpoint)
    - correo_institucional
    - username
    - numero_documento
    - rol
    - estado_cuenta
    - configuración 2FA

    **Consideraciones:**
    - Solo actualiza campos proporcionados (PATCH)
    - Mantiene integridad de datos críticos
    - Para cambios de rol/estado usar endpoints específicos

    **Respuestas:**
    - 200: Usuario actualizado exitosamente
    - 400: Datos inválidos
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)

    try:
        from src.crud.user.usuario import usuario_crud

        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
            )

        # Actualizar usuario
        update_dict = user_update.model_dump(exclude_unset=True)
        updated_user = usuario_crud.update(db, db_obj=user, obj_in=update_dict)

        return UserCurrentResponse.model_validate(updated_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error actualizando usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR,
        ) from e


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user_by_admin(
    *,
    db: Session = Depends(get_db),
    user_id: UUID,
    current_user: Usuario = Depends(get_current_active_user),
) -> Any:
    """Eliminar usuario por ID (soft delete - solo administradores).

    **Permisos requeridos:** Rol administrador

    **Tipo de eliminación:** Soft delete
    - No elimina físicamente el registro
    - Marca estado como "eliminado"
    - Preserva integridad referencial
    - Mantiene auditoría histórica

    **Restricciones:**
    - Administrador no puede eliminar su propia cuenta
    - Usuario eliminado no puede iniciar sesión
    - Datos quedan disponibles para auditoría

    **Consideraciones:**
    - Acción irreversible desde UI estándar
    - Para reactivar se requiere intervención técnica
    - Recomendado usar desactivación temporal en su lugar

    **Respuestas:**
    - 200: Usuario eliminado exitosamente
    - 400: Intento de auto-eliminación
    - 403: Permisos insuficientes
    - 404: Usuario no encontrado
    - 500: Error interno del servidor
    """
    _verify_admin_permissions(current_user)

    # Prevenir auto-eliminación
    if user_id == current_user.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puede eliminar su propia cuenta",
        )

    try:
        from src.crud.user.usuario import usuario_crud

        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=USUARIO_NO_ENCONTRADO
            )

        # Soft delete
        usuario_crud.delete_account(db, user_id=user_id)

        return MessageResponse(message="Usuario eliminado exitosamente")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error eliminando usuario {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ERROR_INTERNO_SERVIDOR,
        ) from e
