import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.deps import get_current_user, get_db
from src.models.academic.institucion import Institucion
from src.models.users.usuario import RolUsuario, Usuario
from src.schemas.institucion import InstitucionCreate, InstitucionResponse
from src.schemas.invitacion import InvitacionCreate, InvitacionResponse
from src.services.email_templates import enviar_invitacion_coordinador
from src.services.invitation_service import InvitationService
from src.enums.academic.institucion_enums import EstadoInstitucion


logger = logging.getLogger(__name__)

# El router NO debe tener prefijo aquí porque se monta con prefijo /admin en __init__.py
router = APIRouter(tags=["Administrador"])


@router.post("/instituciones", response_model=InstitucionResponse)
def registrar_institucion(
    request: Request,
    data: InstitucionCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    """Registrar nueva institución (solo administradores).

    Crea una nueva institución en el sistema con estado 'pendiente'.
    La institución se activará cuando un coordinador acepte la invitación.
    """
    # Log de información de autenticación para debug
    auth_header = request.headers.get("Authorization", "No hay header de autorización")
    logger.debug(f"Header de autorización: {auth_header}")
    logger.debug(f"Usuario autenticado: {user.usuario_id} - Rol: {user.rol}")

    if user.rol != RolUsuario.administrador:
        logger.warning(
            f"Intento de acceso no autorizado: Usuario {user.usuario_id} con rol {user.rol}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede registrar instituciones",
        )

    try:
        # Crear datos del modelo usando los valores del enum
        institucion_data = {
            "administrador_id_creador": user.usuario_id,
            "nombre": data.nombre,
            "sigla": data.sigla,
            "lema": data.lema,
            "tipo_institucion": data.tipo_institucion,  # Ya es un enum
            "usa_programas": data.usa_programas,
            "nivel_educativo": data.nivel_educativo,  # Ya es un enum
            "sector": data.sector,  # Ya es un enum
            "direccion": data.direccion,
            "ciudad": data.ciudad,
            "pais": data.pais,
            "correo_institucional": data.correo_institucional,
            "telefono": data.telefono,
            "nit": data.nit,
            "estado": EstadoInstitucion.pendiente,  # Usar enum directamente
        }

        logger.debug(f"Creando institución con datos: {institucion_data}")

        institucion = Institucion(**institucion_data)
        db.add(institucion)
        db.commit()
        db.refresh(institucion)

        logger.info(
            f"Institución registrada correctamente: {institucion.institucion_id}"
        )
        return institucion

    except IntegrityError as e:
        logger.exception(f"Error de integridad al registrar institución: {e!s}")
        db.rollback()

        # Análisis específico del error de integridad
        error_msg = str(e.orig)
        if "unique constraint" in error_msg.lower():
            if "nombre" in error_msg:
                detail = "Ya existe una institución con este nombre"
            elif "sigla" in error_msg:
                detail = "Ya existe una institución con esta sigla"
            elif "correo_institucional" in error_msg:
                detail = "Ya existe una institución con este correo"
            elif "nit" in error_msg:
                detail = "Ya existe una institución con este NIT"
            else:
                detail = "Ya existe una institución con algunos de estos datos"
        else:
            detail = "Error de integridad en los datos"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from None

    except Exception as e:
        logger.exception(f"Error inesperado al registrar institución: {e!s}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al registrar la institución",
        ) from e


@router.post(
    "/instituciones/{institucion_id}/invitar-coordinador",
    response_model=InvitacionResponse,
)
def invitar_coordinador(
    request: Request,
    institucion_id: UUID,
    invitacion: InvitacionCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    """Invitar coordinador a una institución (solo administradores).

    Envía una invitación por email al coordinador para que complete
    su perfil y active la institución.
    """
    # Log de información de autenticación para debug
    auth_header = request.headers.get("Authorization", "No hay header de autorización")
    logger.debug(f"Header de autorización: {auth_header}")
    logger.debug(f"Usuario autenticado: {user.usuario_id} - Rol: {user.rol}")

    if user.rol != RolUsuario.administrador:
        logger.warning(
            f"Intento de acceso no autorizado: Usuario {user.usuario_id} con rol {user.rol}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el administrador puede invitar coordinadores",
        )

    try:
        # Verificar que la institución existe
        institucion = (
            db.query(Institucion).filter_by(institucion_id=institucion_id).first()
        )
        if not institucion:
            logger.warning(f"Institución no encontrada: {institucion_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institución no encontrada",
            )

        # Verificar que la institución está en estado pendiente
        if institucion.estado != EstadoInstitucion.pendiente:
            logger.warning(
                f"Institución {institucion_id} no está en estado pendiente: {institucion.estado}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La institución debe estar en estado 'pendiente' para invitar coordinadores. Estado actual: {institucion.estado}",
            )

        logger.info(
            f"Creando invitación para institución {institucion_id} y email {invitacion.email_destino}"
        )

        invitacion_db = InvitationService.crear_invitacion(
            db=db,
            email_destino=invitacion.email_destino,
            institucion_id=institucion_id,
            # No pasamos fecha_expiracion para que use el defecto (72 horas)
        )

        # URL para el registro del coordinador
        url_registro = (
            "https://acadify.app/registro-coordinador"  # Puedes personalizar esta URL
        )

        # Enviar email de invitación
        enviar_invitacion_coordinador(
            destinatario=invitacion_db.email_destino,
            institucion_nombre=institucion.nombre,
            codigo=invitacion_db.codigo,
            fecha_expiracion=invitacion_db.fecha_expiracion,
            url_registro=url_registro,
        )

        logger.info(
            f"Invitación enviada correctamente: {invitacion_db.id} para institución {institucion_id}"
        )
        return invitacion_db

    except HTTPException:
        raise
    except IntegrityError as e:
        logger.exception(f"Error de integridad al crear invitación: {e!s}")
        db.rollback()

        error_msg = str(e.orig)
        if "unique constraint" in error_msg.lower():
            detail = (
                "Ya existe una invitación pendiente para este email en esta institución"
            )
        else:
            detail = "Error de integridad en los datos de la invitación"

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        ) from e
    except Exception as e:
        logger.exception(f"Error inesperado al enviar invitación: {e!s}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar la invitación",
        ) from e


@router.post("/invitaciones/validar", response_model=dict)
def validar_codigo_invitacion(codigo: str, db: Session = Depends(get_db)):
    """Valida un código de invitación sin usarlo.

    Endpoint público que permite verificar si un código es válido
    antes de que el coordinador complete su registro.

    Returns:
        - valido: boolean
        - invitacion: datos de la invitación
        - institucion: información de la institución
    """
    logger.info(f"Validando código de invitación: {codigo}")
    return InvitationService.validar_y_obtener_info(db, codigo)


@router.post("/invitaciones/aceptar", response_model=dict)
def aceptar_invitacion_coordinador(
    codigo: str,
    nombre: str,
    apellido: str,
    password: str,
    db: Session = Depends(get_db),
):
    """Acepta una invitación y completa el registro del coordinador.

    Este endpoint realiza el proceso completo:
    1. Valida el código de invitación
    2. Crea el usuario coordinador
    3. Crea el perfil de coordinador
    4. Vincula el coordinador con la institución
    5. Activa la institución
    6. Marca la invitación como usada

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
    """
    # Validación básica de contraseña
    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres",
        )

    logger.info(f"Procesando aceptación de invitación: {codigo}")

    resultado = InvitationService.aceptar_invitacion(
        db=db, codigo=codigo, nombre=nombre, apellido=apellido, password=password
    )

    logger.info(
        f"Invitación aceptada exitosamente para usuario: {resultado['usuario']['email']}"
    )

    return resultado
