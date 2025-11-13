"""Endpoints públicos para el sistema de invitaciones.

Este router maneja las invitaciones sin autenticación requerida para:
- Validar códigos de invitación
- Aceptar invitaciones y registrar coordinadores

Principios SOLID aplicados:
- Single Responsibility: Cada endpoint tiene una sola responsabilidad
- Dependency Inversion: Depende de abstracciones (Session, Services)
- Open/Closed: Extensible sin modificar código existente
"""

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user
from src.api.deps import get_db
from src.models.users.usuario import Usuario
from src.services.invitation_service import InvitationService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Invitaciones Públicas"])


@router.get("/mis-invitaciones", response_model=list[dict[str, Any]])
def obtener_mis_invitaciones(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtiene las invitaciones pendientes del usuario autenticado.

    **Endpoint protegido** que retorna las invitaciones enviadas al email
    del usuario que aún no han sido aceptadas.

    Returns:
        Lista de invitaciones pendientes con información de la institución

    Raises:
        HTTPException 401: Usuario no autenticado
        HTTPException 500: Error interno del servidor
    """
    logger.info(f"📨 Obteniendo invitaciones para usuario: {current_user.email}")

    try:
        from src.crud.academic.institucion_crud import crud_institucion
        from src.crud.auth.invitation_token_crud import crud_invitation_token

        # Obtener invitaciones pendientes del usuario
        invitaciones = crud_invitation_token.get_by_email(
            db, email=current_user.email, only_valid=True
        )

        resultado = []
        for inv in invitaciones:
            # Obtener información de la institución
            institucion = crud_institucion.get(db, id=inv.institucion_id)
            if institucion:
                resultado.append(
                    {
                        "invitacion_id": str(inv.id),
                        "codigo": inv.codigo,
                        "email_destino": inv.email_destino,
                        "fecha_creacion": inv.fecha_creacion.isoformat(),
                        "fecha_expiracion": inv.fecha_expiracion.isoformat(),
                        "institucion": {
                            "institucion_id": str(institucion.institucion_id),
                            "nombre": institucion.nombre,
                            "sigla": institucion.sigla,
                            "logo_url": institucion.logo_url,
                            "tipo_institucion": institucion.tipo_institucion,
                            "nivel_educativo": institucion.nivel_educativo,
                            "ciudad": institucion.ciudad,
                            "pais": institucion.pais,
                        },
                    }
                )

        logger.info(f"✓ Encontradas {len(resultado)} invitaciones pendientes")
        return resultado

    except Exception as e:
        logger.exception(f"✗ Error al obtener invitaciones: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener invitaciones",
        ) from e


@router.get("/validar/{codigo}", response_model=dict[str, Any])
def validar_codigo_invitacion(codigo: str, db: Session = Depends(get_db)):
    """Valida un código de invitación sin usarlo.

    **Endpoint público** que permite verificar si un código es válido
    antes de que el coordinador complete su registro.

    Args:
        codigo: Código de invitación de 6 dígitos

    Returns:
        - valido: boolean
        - invitacion: datos de la invitación
        - institucion: información de la institución

    Raises:
        HTTPException 400: Si el código es inválido, usado o expirado
        HTTPException 404: Si la institución no existe
        HTTPException 500: Error interno del servidor
    """
    logger.info(f"📨 Validando código de invitación: {codigo}")

    try:
        resultado = InvitationService.validar_y_obtener_info(db, codigo)
        logger.info(
            f"✓ Código válido para institución: {resultado['institucion']['nombre']}"
        )
        return resultado
    except HTTPException as e:
        logger.warning(f"✗ Validación fallida: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"✗ Error inesperado en validación: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al validar el código",
        ) from e


@router.post("/aceptar", response_model=dict[str, Any])
def aceptar_invitacion_coordinador(
    codigo: str = Body(
        ..., description="Código de invitación de 6 dígitos", min_length=6, max_length=6
    ),
    nombre: str = Body(
        ..., description="Nombre del coordinador", min_length=2, max_length=50
    ),
    apellido: str = Body(
        ..., description="Apellido del coordinador", min_length=2, max_length=50
    ),
    password: str = Body(
        ...,
        description="Contraseña (mínimo 8 caracteres)",
        min_length=8,
        max_length=100,
    ),
    db: Session = Depends(get_db),
):
    """Acepta una invitación y completa el registro del coordinador.

    **Endpoint público** que realiza el proceso completo:

    1. ✓ Valida el código de invitación
    2. ✓ Crea el usuario coordinador
    3. ✓ Crea el perfil de coordinador
    4. ✓ Vincula el coordinador con la institución
    5. ✓ Activa la institución
    6. ✓ Marca la invitación como usada

    Este proceso es **atómico**: si algún paso falla, toda la transacción
    se revierte (rollback).

    Args:
        codigo: Código de invitación de 6 dígitos
        nombre: Nombre del coordinador
        apellido: Apellido del coordinador
        password: Contraseña del coordinador (mínimo 8 caracteres)

    Returns:
        - success: boolean
        - message: string
        - usuario: información del usuario creado
        - institucion: información de la institución activada

    Raises:
        HTTPException 400: Validación de datos fallida
        HTTPException 404: Institución no encontrada
        HTTPException 500: Error interno del servidor

    Example:
        ```json
        {
            "codigo": "AB12C3",
            "nombre": "Juan Carlos",
            "apellido": "Pérez Gómez",
            "password": "SecurePass123!"
        }
        ```
    """
    # Validación básica de longitud de contraseña
    if len(password) < 8:
        logger.warning(f"✗ Contraseña muy corta para código {codigo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres",
        )

    if len(password) > 100:
        logger.warning(f"✗ Contraseña muy larga para código {codigo}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña no puede exceder 100 caracteres",
        )

    # Validación de nombres (sin números)
    if not nombre.replace(" ", "").isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre solo puede contener letras",
        )

    if not apellido.replace(" ", "").isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El apellido solo puede contener letras",
        )

    logger.info(f"📨 Procesando aceptación de invitación: {codigo}")
    logger.info(f"   Coordinador: {nombre} {apellido}")

    try:
        resultado = InvitationService.aceptar_invitacion(
            db=db, codigo=codigo, nombre=nombre, apellido=apellido, password=password
        )

        logger.info("✓ Invitación aceptada exitosamente")
        logger.info(f"   Usuario: {resultado['usuario']['email']}")
        logger.info(f"   Institución: {resultado['institucion']['nombre']}")

        return resultado

    except HTTPException as e:
        logger.warning(f"✗ Error al aceptar invitación: {e.detail}")
        raise
    except Exception as e:
        logger.exception(f"✗ Error inesperado al aceptar invitación: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al procesar la invitación",
        ) from e
