"""Endpoints PÚBLICOS para instituciones.
Permite verificar dominios de email y registro automático de usuarios.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.crud.academic.crud_institucion import institucion_crud
from src.enums.academic.institucion_enums import (
    ModalidadEnsenanza,
    NivelEducativoInstitucion,
    SectorInstitucion,
    TipoInstitucion,
)
from src.models.users.usuario import RolUsuario
from src.services.invitation_service import InvitationService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/instituciones", tags=["Instituciones Públicas"])


# ============================================
# SCHEMAS ESPECÍFICOS PARA ESTOS ENDPOINTS
# ============================================


class VerificarDominioRequest(BaseModel):
    """Schema para verificar si un email pertenece a una institución."""

    email: EmailStr = Field(..., description="Email a verificar")


class RegistroAutomaticoRequest(BaseModel):
    """Schema para registro automático por dominio."""

    email: EmailStr = Field(..., description="Email institucional")
    nombre: str = Field(..., min_length=2, max_length=50)
    apellido: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    rol: RolUsuario = Field(
        default=RolUsuario.estudiante,
        description="Rol del usuario (estudiante, docente, etc.)",
    )


class FiltrosInstitucionRequest(BaseModel):
    """Schema para filtros de búsqueda de instituciones."""

    tipo_institucion: TipoInstitucion | None = None
    nivel_educativo: NivelEducativoInstitucion | None = None
    modalidad_ensenanza: ModalidadEnsenanza | None = None
    sector: SectorInstitucion | None = None
    estado: str | None = Field(None, description="Estado de la institución")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)


# ============================================
# ENDPOINTS PÚBLICOS
# ============================================


@router.post("/verificar-dominio", response_model=dict[str, Any])
def verificar_dominio_email(
    request: VerificarDominioRequest, db: Session = Depends(get_db)
):
    """Verifica si un email pertenece a alguna institución registrada.

    **Público** - No requiere autenticación.

    Este endpoint permite a usuarios verificar si su email institucional
    está asociado a una institución en el sistema, permitiéndoles registrarse
    automáticamente sin necesidad de código de invitación.

    **Casos de uso:**
    - Usuario con email @arp.edu.co verifica si puede registrarse en ARP
    - Estudiante con email @uni.edu verifica su institución
    - Docente verifica si puede unirse automáticamente

    **Respuesta exitosa:**
    ```json
    {
        "encontrada": true,
        "institucion": {
            "institucion_id": "uuid",
            "nombre": "Universidad ARP",
            "logo_url": "https://...",
            "tipo_institucion": "universidad",
            "permite_registro_automatico": true
        }
    }
    ```

    **Sin coincidencia:**
    ```json
    {
        "encontrada": false,
        "mensaje": "No se encontró institución para este dominio",
        "sugerencia": "Solicita un código de invitación a tu institución"
    }
    ```
    """
    logger.info(f"Verificando dominio para email: {request.email}")

    try:
        info_institucion = InvitationService.buscar_institucion_por_email(
            db=db, email=request.email
        )

        if info_institucion:
            return {"encontrada": True, "institucion": info_institucion}
        return {
            "encontrada": False,
            "mensaje": "No se encontró ninguna institución activa para este dominio de email",
            "sugerencia": "Solicita un código de invitación a tu coordinador institucional",
        }

    except Exception as e:
        logger.exception(f"Error al verificar dominio: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al verificar el dominio",
        ) from e


@router.post("/registro-automatico", response_model=dict[str, Any])
def registro_automatico_por_dominio(
    request: RegistroAutomaticoRequest, db: Session = Depends(get_db)
):
    """Registra un usuario automáticamente basándose en el dominio de su email.

    **Público** - No requiere autenticación.

    Flujo automático:
    1. Extrae el dominio del email (ej: @arp.edu.co)
    2. Busca la institución que tenga ese dominio configurado
    3. Crea el usuario con el rol especificado
    4. Lo vincula automáticamente a la institución

    **Requisitos:**
    - El dominio del email debe estar registrado en `dominio_principal` o `dominios_adicionales`
    - La institución debe estar activa
    - El email no debe estar ya registrado

    **Ejemplo de uso:**
    ```json
    {
        "email": "juan.perez@arp.edu.co",
        "nombre": "Juan",
        "apellido": "Pérez",
        "password": "MiPassword123!",
        "rol": "estudiante"
    }
    ```

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "message": "Usuario registrado exitosamente en Universidad ARP",
        "usuario": {
            "id": "uuid",
            "email": "juan.perez@arp.edu.co",
            "username": "juan_perez",
            "rol": "estudiante"
        },
        "institucion": {
            "nombre": "Universidad ARP",
            "logo_url": "https://..."
        }
    }
    ```
    """
    logger.info(f"Intento de registro automático para email: {request.email}")

    try:
        resultado = InvitationService.registrar_usuario_por_dominio(
            db=db,
            email=request.email,
            nombre=request.nombre,
            apellido=request.apellido,
            password=request.password,
            rol=request.rol,
        )

        logger.info(f"Usuario registrado exitosamente: {request.email}")
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error en registro automático: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al procesar el registro automático",
        ) from e


@router.get("/buscar", response_model=list[dict[str, Any]])
def buscar_instituciones_con_filtros(
    tipo_institucion: str | None = None,
    nivel_educativo: str | None = None,
    modalidad_ensenanza: str | None = None,
    sector: str | None = None,
    estado: str | None = "activa",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Busca instituciones aplicando filtros.

    **Público** - No requiere autenticación.

    Permite filtrar instituciones por múltiples criterios.
    Por defecto, solo muestra instituciones activas.

    **Parámetros de búsqueda:**
    - `tipo_institucion`: universidad, colegio, instituto, etc.
    - `nivel_educativo`: basica, media, superior, etc.
    - `modalidad_ensenanza`: presencial, virtual, hibrida, dual
    - `sector`: publico, privado
    - `estado`: pendiente, activa, suspendida, inactiva
    - `skip`: Número de resultados a saltar (paginación)
    - `limit`: Número máximo de resultados (máx: 500)

    **Ejemplo de uso:**
    ```
    GET /instituciones/buscar?tipo_institucion=universidad&modalidad_ensenanza=hibrida&limit=20
    ```

    **Respuesta:**
    ```json
    [
        {
            "institucion_id": "uuid",
            "nombre": "Universidad ARP",
            "logo_url": "https://...",
            "tipo_institucion": "universidad",
            "modalidad_ensenanza": "hibrida",
            "numero_estudiantes_actual": 1500
        }
    ]
    ```
    """
    logger.info(
        f"Búsqueda de instituciones con filtros: tipo={tipo_institucion}, modalidad={modalidad_ensenanza}"
    )

    try:
        instituciones = institucion_crud.get_by_filtros(
            db=db,
            tipo_institucion=tipo_institucion,
            nivel_educativo=nivel_educativo,
            modalidad_ensenanza=modalidad_ensenanza,
            sector=sector,
            estado=estado,
            skip=skip,
            limit=min(limit, 500),  # Máximo 500 resultados
        )

        # Convertir a dict con información relevante
        resultados = []
        for inst in instituciones:
            resultados.append(
                {
                    "institucion_id": str(inst.institucion_id),
                    "nombre": inst.nombre,
                    "sigla": inst.sigla,
                    "logo_url": inst.logo_url,
                    "tipo_institucion": (
                        inst.tipo_institucion.value if inst.tipo_institucion else None
                    ),
                    "nivel_educativo": (
                        inst.nivel_educativo.value if inst.nivel_educativo else None
                    ),
                    "modalidad_ensenanza": (
                        inst.modalidad_ensenanza.value
                        if inst.modalidad_ensenanza
                        else None
                    ),
                    "sector": inst.sector.value if inst.sector else None,
                    "ciudad": inst.ciudad,
                    "pais": inst.pais,
                    "website": inst.website,
                    "numero_estudiantes_actual": inst.numero_estudiantes_actual or 0,
                    "numero_docentes": inst.numero_docentes or 0,
                }
            )

        logger.info(f"Se encontraron {len(resultados)} instituciones")
        return resultados

    except Exception as e:
        logger.exception(f"Error al buscar instituciones: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al buscar instituciones",
        ) from e


@router.get("/{institucion_id}/estadisticas", response_model=dict[str, Any])
def obtener_estadisticas_institucion(
    institucion_id: str, db: Session = Depends(get_db)
):
    """Obtiene estadísticas públicas de una institución.

    **Público** - No requiere autenticación.

    Retorna información estadística sobre una institución:
    - Número de programas, cursos, estudiantes, docentes
    - Capacidad y ocupación
    - Información general

    **Ejemplo de respuesta:**
    ```json
    {
        "institucion_id": "uuid",
        "nombre": "Universidad ARP",
        "logo_url": "https://...",
        "total_programas": 25,
        "total_cursos": 150,
        "numero_estudiantes_actual": 1500,
        "capacidad_estudiantes": 2000,
        "porcentaje_ocupacion": 75.0
    }
    ```
    """
    logger.info(f"Solicitando estadísticas para institución: {institucion_id}")

    try:
        from uuid import UUID

        estadisticas = institucion_crud.get_estadisticas_institucion(
            db=db, institucion_id=UUID(institucion_id)
        )

        if not estadisticas:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institución no encontrada",
            )

        # Calcular porcentaje de ocupación si hay capacidad definida
        if estadisticas.get("capacidad_estudiantes"):
            ocupacion = (
                estadisticas["numero_estudiantes_actual"]
                / estadisticas["capacidad_estudiantes"]
            ) * 100
            estadisticas["porcentaje_ocupacion"] = round(ocupacion, 2)
        else:
            estadisticas["porcentaje_ocupacion"] = None

        return estadisticas

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ID de institución inválido"
        ) from None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error al obtener estadísticas: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas de la institución",
        ) from e
