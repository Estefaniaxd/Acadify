"""Router para el sistema de notificaciones.

Este módulo maneja las notificaciones del usuario y su configuración.
POR AHORA: Implementación básica que retorna respuestas vacías/mock
TODO: Implementar completamente cuando se creen los modelos y CRUD
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.deps import get_db
from src.models.users.usuario import Usuario

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notificaciones",
    tags=["Notificaciones"],
)


@router.get("", response_model=dict[str, Any])
def obtener_notificaciones(
    solo_no_leidas: bool = Query(False),
    ordenar_por: str = Query("fecha_creacion"),
    orden_desc: bool = Query(True),
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene las notificaciones del usuario actual.

    **Implementación temporal**: Retorna lista vacía hasta que se implemente el sistema completo.

    Returns:
        Lista de notificaciones del usuario
    """
    logger.info(
        f"📬 Obteniendo notificaciones para usuario: {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real cuando exista el modelo Notificacion
    return {
        "notificaciones": [],
        "total": 0,
        "no_leidas": 0,
    }


@router.post("/marcar-leidas", status_code=status.HTTP_200_OK)
def marcar_notificaciones_como_leidas(
    ids: list[str],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca notificaciones específicas como leídas.

    **Implementación temporal**: Retorna éxito sin hacer nada.

    Args:
        ids: Lista de IDs de notificaciones a marcar como leídas
    """
    logger.info(
        f"✓ Marcando {len(ids)} notificaciones como leídas para {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real
    return {
        "success": True,
        "marcadas": 0,
        "message": "Sistema de notificaciones en desarrollo",
    }


@router.post("/marcar-todas-leidas", status_code=status.HTTP_200_OK)
def marcar_todas_notificaciones_como_leidas(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marca todas las notificaciones del usuario como leídas.

    **Implementación temporal**: Retorna éxito sin hacer nada.
    """
    logger.info(
        f"✓ Marcando todas las notificaciones como leídas para {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real
    return {
        "success": True,
        "marcadas": 0,
        "message": "Sistema de notificaciones en desarrollo",
    }


@router.get("/count", response_model=dict[str, int])
def obtener_contador_notificaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene el contador de notificaciones no leídas.

    **Implementación temporal**: Retorna 0.

    Returns:
        total: Total de notificaciones
        no_leidas: Notificaciones no leídas
    """
    logger.info(
        f"📊 Obteniendo contador de notificaciones para {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real
    return {
        "total": 0,
        "no_leidas": 0,
    }


@router.get("/configuracion", response_model=dict[str, Any])
def obtener_configuracion_notificaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene la configuración de notificaciones del usuario.

    **Implementación temporal**: Retorna configuración por defecto.

    Returns:
        Configuración de notificaciones
    """
    logger.info(
        f"⚙️  Obteniendo configuración de notificaciones para {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real cuando exista el modelo ConfiguracionNotificaciones
    return {
        "email_notificaciones": True,
        "notificaciones_push": True,
        "notificaciones_tareas": True,
        "notificaciones_mensajes": True,
        "notificaciones_calificaciones": True,
        "notificaciones_anuncios": True,
        "resumen_diario": False,
        "resumen_semanal": False,
    }


@router.put("/configuracion", response_model=dict[str, Any])
def actualizar_configuracion_notificaciones(
    config: dict[str, Any],
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza la configuración de notificaciones del usuario.

    **Implementación temporal**: Acepta la configuración pero no la guarda.

    Args:
        config: Nueva configuración de notificaciones
    """
    logger.info(
        f"⚙️  Actualizando configuración de notificaciones para {current_user.correo_institucional}"
    )

    # TODO: Implementar lógica real
    return {
        "success": True,
        "message": "Sistema de notificaciones en desarrollo",
        **config,
    }
