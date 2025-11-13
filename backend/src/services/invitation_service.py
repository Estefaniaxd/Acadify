from datetime import UTC, datetime, timedelta
import logging
import random
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.enums.academic.institucion_enums import EstadoInstitucion
from src.enums.users.coordinador_enums import EstadoCoordinador
from src.enums.users.usuario_enums import EstadoCuentaUsuario, TipoDocumentoUsuario
from src.models.academic.institucion import Institucion
from src.models.auth.invitation_token import EstadoInvitacion, InvitationToken
from src.models.users.coordinador import Coordinador
from src.models.users.institucion_coordinador import InstitucionCoordinador
from src.models.users.usuario import RolUsuario, Usuario
from src.services.email_service import enviar_email
from src.utils.security import SecurityManager


logger = logging.getLogger(__name__)
security_manager = SecurityManager()


class InvitationService:
    @staticmethod
    def generar_codigo_unico(db: Session) -> str:
        """Genera un código único de 6 dígitos."""
        while True:
            codigo = f"{random.randint(100000, 999999)}"
            existe = db.query(InvitationToken).filter_by(codigo=codigo).first()
            if not existe:
                return codigo

    @staticmethod
    def crear_invitacion(
        db: Session, email_destino: str, institucion_id, fecha_expiracion=None
    ) -> InvitationToken:
        codigo = InvitationService.generar_codigo_unico(db)
        if not fecha_expiracion:
            ahora = datetime.now(UTC)
            fecha_expiracion = ahora + timedelta(hours=72)  # 3 días

        invitacion = InvitationToken(
            codigo=codigo,
            email_destino=email_destino,
            institucion_id=institucion_id,
            estado=EstadoInvitacion.pendiente,
            fecha_expiracion=fecha_expiracion,
        )
        db.add(invitacion)
        db.commit()
        db.refresh(invitacion)
        return invitacion

    @staticmethod
    def enviar_invitacion_email(invitacion: InvitationToken, db: Session) -> None:
        institucion = (
            db.query(Institucion)
            .filter_by(institucion_id=invitacion.institucion_id)
            .first()
        )
        asunto = f"Invitación para ser coordinador en {institucion.nombre}"
        cuerpo = f"""
        Hola,
        Has sido invitado como coordinador principal de la institución {institucion.nombre}.
        Tu código de invitación es: {invitacion.codigo}
        Este código expira el {invitacion.fecha_expiracion.strftime('%Y-%m-%d %H:%M')} UTC.
        Ingresa al sistema y completa tu registro usando este código.
        """
        enviar_email(
            destinatario=invitacion.email_destino, asunto=asunto, cuerpo=cuerpo
        )

    @staticmethod
    def validar_codigo(db: Session, codigo: str) -> InvitationToken:
        invitacion = db.query(InvitationToken).filter_by(codigo=codigo).first()
        if not invitacion:
            msg = "Código inválido"
            raise ValueError(msg)
        if invitacion.estado != EstadoInvitacion.pendiente:
            msg = "El código ya fue usado o expiró"
            raise ValueError(msg)

        # Debug: imprimir fechas para verificar
        ahora = datetime.now(UTC)

        if invitacion.fecha_expiracion < ahora:
            invitacion.estado = EstadoInvitacion.expirado
            db.commit()
            msg = f"El código ha expirado. Expiró el {invitacion.fecha_expiracion.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            raise ValueError(msg)
        return invitacion

    @staticmethod
    def marcar_usado(db: Session, invitacion: InvitationToken, coordinador_id) -> None:
        invitacion.estado = EstadoInvitacion.usado
        invitacion.coordinador_id = coordinador_id
        invitacion.usado_en = datetime.now(UTC)
        db.commit()
        db.refresh(invitacion)

    @staticmethod
    def validar_y_obtener_info(db: Session, codigo: str) -> dict[str, Any]:
        """Valida un código de invitación y devuelve información completa.

        Principio: Single Responsibility - Solo valida y obtiene info, no modifica.

        Args:
            db: Sesión de base de datos
            codigo: Código de invitación de 6 dígitos

        Returns:
            Dict con información de la invitación y la institución

        Raises:
            HTTPException: Si el código es inválido, usado o expirado
        """
        try:
            invitacion = InvitationService.validar_codigo(db, codigo)

            # Obtener información de la institución
            institucion = (
                db.query(Institucion)
                .filter(Institucion.institucion_id == invitacion.institucion_id)
                .first()
            )

            if not institucion:
                logger.error(
                    f"Institución no encontrada para invitación {invitacion.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Institución no encontrada",
                )

            return {
                "valido": True,
                "invitacion": {
                    "id": str(invitacion.id),
                    "codigo": invitacion.codigo,
                    "email_destino": invitacion.email_destino,
                    "fecha_expiracion": invitacion.fecha_expiracion.isoformat(),
                },
                "institucion": {
                    "id": str(institucion.institucion_id),
                    "nombre": institucion.nombre,
                    "sigla": institucion.sigla,
                    "tipo_institucion": (
                        institucion.tipo_institucion.value
                        if institucion.tipo_institucion
                        else None
                    ),
                    "nivel_educativo": (
                        institucion.nivel_educativo.value
                        if institucion.nivel_educativo
                        else None
                    ),
                    "ciudad": institucion.ciudad,
                    "pais": institucion.pais,
                },
            }

        except ValueError as e:
            logger.warning(f"Validación de código fallida: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
        except Exception as e:
            logger.exception(f"Error inesperado al validar código: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al validar el código de invitación",
            ) from e

    @staticmethod
    def _crear_usuario_coordinador(
        db: Session, email: str, nombre: str, apellido: str, password: str
    ) -> Usuario:
        """Crea un nuevo usuario con rol coordinador.

        Principio: Single Responsibility - Solo crea el usuario.
        Principio: Dependency Inversion - Recibe dependencias como parámetros.

        Args:
            db: Sesión de base de datos
            email: Email del coordinador
            nombre: Nombre del coordinador
            apellido: Apellido del coordinador
            password: Contraseña sin hashear

        Returns:
            Usuario creado

        Raises:
            HTTPException: Si el email ya está registrado
        """
        # Verificar si el usuario ya existe
        usuario_existente = (
            db.query(Usuario).filter(Usuario.correo_institucional == email).first()
        )

        if usuario_existente:
            logger.warning(f"Intento de registro con email existente: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este correo electrónico ya está registrado",
            )

        # Crear usuario
        # Generar un número de documento único temporal (puede actualizarse después)
        import random

        numero_doc_temporal = str(random.randint(10000000, 99999999))

        # Generar username a partir del email (para recuperación de contraseña)
        # Ejemplo: coord.test@gmail.com -> coord_test
        username_generado = email.split("@")[0].replace(".", "_")

        usuario = Usuario(
            correo_institucional=email,
            username=username_generado,  # Todos los usuarios tienen username para recuperación
            nombres=nombre,
            apellidos=apellido,
            tipo_documento=TipoDocumentoUsuario.cc,  # Por defecto CC, puede cambiarse después
            numero_documento=numero_doc_temporal,  # Temporal único
            password_hash=security_manager.get_password_hash(password),
            rol=RolUsuario.coordinador,
            estado_cuenta=EstadoCuentaUsuario.activo,
        )

        db.add(usuario)
        db.flush()  # Flush para obtener el ID sin hacer commit

        logger.info(f"Usuario coordinador creado: {usuario.usuario_id}")
        return usuario

    @staticmethod
    def _crear_perfil_coordinador(
        db: Session, usuario_id: str, fecha_inicio_carrera: datetime | None = None
    ) -> Coordinador:
        """Crea el perfil de coordinador vinculado al usuario.

        Principio: Single Responsibility - Solo crea el perfil.

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            fecha_inicio_carrera: Fecha de inicio (default: hoy)

        Returns:
            Coordinador creado
        """
        if not fecha_inicio_carrera:
            fecha_inicio_carrera = datetime.now(UTC).date()

        coordinador = Coordinador(
            coordinador_id=usuario_id, fecha_inicio_carrera=fecha_inicio_carrera
        )

        db.add(coordinador)
        db.flush()

        logger.info(f"Perfil coordinador creado: {coordinador.coordinador_id}")
        return coordinador

    @staticmethod
    def _vincular_institucion_coordinador(
        db: Session, institucion_id: str, coordinador_id: str
    ) -> InstitucionCoordinador:
        """Vincula un coordinador a una institución.

        Principio: Single Responsibility - Solo crea la vinculación.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución
            coordinador_id: ID del coordinador

        Returns:
            InstitucionCoordinador creado
        """
        vinculacion = InstitucionCoordinador(
            institucion_id=institucion_id,
            coordinador_id=coordinador_id,
            fecha_asignacion=datetime.now(UTC).date(),
            estado=EstadoCoordinador.activo,
        )

        db.add(vinculacion)
        db.flush()

        logger.info(
            f"Coordinador {coordinador_id} vinculado a institución {institucion_id}"
        )
        return vinculacion

    @staticmethod
    def _activar_institucion(db: Session, institucion_id: str) -> Institucion:
        """Activa una institución y registra la fecha de activación.

        Principio: Single Responsibility - Solo activa la institución.

        Args:
            db: Sesión de base de datos
            institucion_id: ID de la institución

        Returns:
            Institución actualizada
        """
        institucion = (
            db.query(Institucion)
            .filter(Institucion.institucion_id == institucion_id)
            .first()
        )

        if not institucion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institución no encontrada",
            )

        institucion.estado = EstadoInstitucion.activa
        institucion.fecha_activacion = datetime.now(UTC)

        db.flush()

        logger.info(f"Institución {institucion_id} activada")
        return institucion

    @staticmethod
    def aceptar_invitacion(
        db: Session, codigo: str, nombre: str, apellido: str, password: str
    ) -> dict[str, Any]:
        """Procesa la aceptación de una invitación completa.

        Principio: Open/Closed - Extensible sin modificar código existente.
        Principio: Interface Segregation - Métodos específicos y pequeños.

        Este método orquesta todo el proceso:
        1. Valida la invitación
        2. Crea el usuario coordinador
        3. Crea el perfil de coordinador
        4. Vincula coordinador con institución
        5. Activa la institución
        6. Marca la invitación como usada

        Args:
            db: Sesión de base de datos
            codigo: Código de invitación
            nombre: Nombre del coordinador
            apellido: Apellido del coordinador
            password: Contraseña del coordinador

        Returns:
            Dict con información del usuario y la institución

        Raises:
            HTTPException: Si hay algún error en el proceso
        """
        try:
            # 1. Validar invitación
            logger.info(f"Iniciando aceptación de invitación: {codigo}")
            invitacion = InvitationService.validar_codigo(db, codigo)

            # 2. Crear usuario coordinador
            usuario = InvitationService._crear_usuario_coordinador(
                db=db,
                email=invitacion.email_destino,
                nombre=nombre,
                apellido=apellido,
                password=password,
            )

            # 3. Crear perfil coordinador
            coordinador = InvitationService._crear_perfil_coordinador(
                db=db, usuario_id=usuario.usuario_id
            )

            # 4. Vincular con institución
            InvitationService._vincular_institucion_coordinador(
                db=db,
                institucion_id=invitacion.institucion_id,
                coordinador_id=coordinador.coordinador_id,
            )

            # 5. Activar institución
            institucion = InvitationService._activar_institucion(
                db=db, institucion_id=invitacion.institucion_id
            )

            # 6. Marcar invitación como usada
            InvitationService.marcar_usado(
                db=db, invitacion=invitacion, coordinador_id=usuario.usuario_id
            )

            # Commit de toda la transacción
            db.commit()
            db.refresh(usuario)
            db.refresh(institucion)

            logger.info(
                f"Invitación aceptada exitosamente. "
                f"Usuario: {usuario.usuario_id}, Institución: {institucion.institucion_id}"
            )

            # Convertir enums a strings de forma segura
            rol_str = (
                usuario.rol.value if hasattr(usuario.rol, "value") else str(usuario.rol)
            )
            estado_str = (
                institucion.estado.value
                if hasattr(institucion.estado, "value")
                else str(institucion.estado)
            )

            return {
                "success": True,
                "message": "Invitación aceptada exitosamente",
                "usuario": {
                    "id": str(usuario.usuario_id),
                    "email": usuario.correo_institucional,
                    "username": usuario.username,
                    "nombre": usuario.nombres,
                    "apellido": usuario.apellidos,
                    "rol": rol_str,
                },
                "institucion": {
                    "id": str(institucion.institucion_id),
                    "nombre": institucion.nombre,
                    "sigla": institucion.sigla,
                    "estado": estado_str,
                    "fecha_activacion": (
                        institucion.fecha_activacion.isoformat()
                        if institucion.fecha_activacion
                        else None
                    ),
                },
            }

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.exception(f"Error de integridad al aceptar invitación: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad de datos. Posiblemente email duplicado.",
            ) from e
        except Exception as e:
            db.rollback()
            logger.exception(f"Error inesperado al aceptar invitación: {e!s}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al procesar la invitación",
            ) from e

    @staticmethod
    def buscar_institucion_por_email(db: Session, email: str) -> dict[str, Any] | None:
        """Busca si un email pertenece a alguna institución registrada.
        Verifica contra dominio_principal y dominios_adicionales.

        Args:
            db: Sesión de base de datos
            email: Email completo a verificar (ej: "estudiante@arp.edu.co")

        Returns:
            Dict con información de la institución si se encuentra, None si no
        """
        if not email or "@" not in email:
            return None

        dominio_email = email.split("@")[1].lower()
        logger.info(f"Buscando institución para dominio: {dominio_email}")

        # Buscar por dominio_principal
        institucion = (
            db.query(Institucion)
            .filter(
                Institucion.dominio_principal == dominio_email,
                Institucion.estado == "activa",  # Solo instituciones activas
            )
            .first()
        )

        if not institucion:
            # Buscar en dominios_adicionales
            # PostgreSQL: ANY para buscar en array
            from sqlalchemy import any_, func

            institucion = (
                db.query(Institucion)
                .filter(
                    dominio_email == any_(func.lower(Institucion.dominios_adicionales)),
                    Institucion.estado == "activa",
                )
                .first()
            )

        if not institucion:
            logger.info(f"No se encontró institución para dominio: {dominio_email}")
            return None

        logger.info(f"Institución encontrada: {institucion.nombre}")

        # Retornar información relevante
        return {
            "institucion_id": str(institucion.institucion_id),
            "nombre": institucion.nombre,
            "sigla": institucion.sigla,
            "logo_url": institucion.logo_url,
            "tipo_institucion": (
                institucion.tipo_institucion.value
                if institucion.tipo_institucion
                else None
            ),
            "nivel_educativo": (
                institucion.nivel_educativo.value
                if institucion.nivel_educativo
                else None
            ),
            "modalidad_ensenanza": (
                institucion.modalidad_ensenanza.value
                if institucion.modalidad_ensenanza
                else None
            ),
            "dominio_coincidente": dominio_email,
            "permite_registro_automatico": True,
            "mensaje": f"Tu email pertenece a {institucion.nombre}. Puedes registrarte directamente.",
        }

    @staticmethod
    def registrar_usuario_por_dominio(
        db: Session,
        email: str,
        nombre: str,
        apellido: str,
        password: str,
        rol: RolUsuario = RolUsuario.estudiante,
    ) -> dict[str, Any]:
        """Registra un usuario automáticamente en una institución basándose en su dominio de email.

        Flujo:
        1. Extrae el dominio del email
        2. Busca la institución que tenga ese dominio
        3. Crea el usuario con el rol especificado
        4. Lo vincula automáticamente a la institución

        Args:
            db: Sesión de base de datos
            email: Email institucional del usuario
            nombre: Nombre(s) del usuario
            apellido: Apellido(s) del usuario
            password: Contraseña en texto plano (se hasheará)
            rol: Rol del usuario (estudiante, docente, etc.)

        Returns:
            Dict con información del usuario creado y la institución

        Raises:
            HTTPException: Si no se encuentra institución o hay errores en el registro
        """
        try:
            # 1. Buscar institución por dominio
            info_institucion = InvitationService.buscar_institucion_por_email(db, email)
            if not info_institucion:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró ninguna institución activa para el dominio de email proporcionado",
                )

            info_institucion["institucion_id"]

            # 2. Verificar que el email no esté ya registrado
            usuario_existente = (
                db.query(Usuario).filter(Usuario.correo_institucional == email).first()
            )

            if usuario_existente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado en el sistema",
                )

            # 3. Crear usuario
            username_generado = email.split("@")[0].replace(".", "_")

            # Verificar unicidad del username
            username_base = username_generado
            contador = 1
            while (
                db.query(Usuario).filter(Usuario.username == username_generado).first()
            ):
                username_generado = f"{username_base}{contador}"
                contador += 1

            usuario = Usuario(
                correo_institucional=email,
                username=username_generado,
                nombres=nombre,
                apellidos=apellido,
                tipo_documento=TipoDocumentoUsuario.cc,  # Por defecto, puede actualizarse después
                numero_documento=str(random.randint(10000000, 99999999)),  # Temporal
                password_hash=security_manager.get_password_hash(password),
                rol=rol,
                estado_cuenta=EstadoCuentaUsuario.activo,
            )

            db.add(usuario)
            db.flush()

            logger.info(
                f"Usuario creado exitosamente vía dominio: {usuario.correo_institucional}"
            )

            # 4. Vincular a la institución según el rol
            # TODO: Crear las relaciones apropiadas según el rol
            # - Si es estudiante: crear Estudiante y vincular a programa
            # - Si es docente: crear Docente
            # - Si es coordinador: crear Coordinador e InstitucionCoordinador

            db.commit()
            db.refresh(usuario)

            return {
                "success": True,
                "message": f"Usuario registrado exitosamente en {info_institucion['nombre']}",
                "usuario": {
                    "id": str(usuario.usuario_id),
                    "email": usuario.correo_institucional,
                    "username": usuario.username,
                    "nombre": usuario.nombres,
                    "apellido": usuario.apellidos,
                    "rol": (
                        usuario.rol.value
                        if hasattr(usuario.rol, "value")
                        else str(usuario.rol)
                    ),
                },
                "institucion": info_institucion,
            }

        except HTTPException:
            db.rollback()
            raise
        except IntegrityError as e:
            db.rollback()
            logger.exception(
                f"Error de integridad al registrar usuario por dominio: {e!s}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad de datos. El usuario podría estar duplicado.",
            ) from e
        except Exception as e:
            db.rollback()
            logger.exception(
                f"Error inesperado al registrar usuario por dominio: {e!s}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno al procesar el registro",
            ) from e
