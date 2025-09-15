# src/services/auth_service.py

from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import redis.asyncio as redis
import logging
from uuid import UUID

from src.models.users.usuario import Usuario
from src.schemas.auth.auth_schemas import (
    LoginRequest, TokenResponse, PasswordResetRequest, PasswordResetConfirm,
    TwoFASetupRequest, TwoFAVerifyRequest, UserCurrentResponse, UserProfileUpdate,
    PasswordChangeRequest, TwoFASetupResponse, LoginStepResponse, LoginAttemptResponse
)
from src.schemas.users.usuario import UsuarioCreate
from src.utils.security import (
    security_manager, get_token_blacklist, get_login_attempt_manager,
    get_email_service, generate_reset_token, is_strong_password
)
from src.crud.user.usuario import usuario_crud
from src.core.config import get_settings
from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario


logger = logging.getLogger(__name__)
settings = get_settings()

# Constantes para mensajes
USER_NOT_FOUND = "Usuario no encontrado"

# ===============================
# Authentication Service
# ===============================

class AuthService:
    """Servicio principal de autenticación"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.token_blacklist = get_token_blacklist(redis_client)
        self.login_attempts = get_login_attempt_manager(redis_client)
        self.email_service = get_email_service()
    
    # ===============================
    # User Registration
    # ===============================
    
    async def register_user(self, db: Session, user_data: UsuarioCreate) -> Usuario:
        """Registrar nuevo usuario respetando constraints chk_login"""
        try:
            self._validate_user_registration(user_data)
            self._validate_password_strength(user_data.password)
            hashed_password = security_manager.get_password_hash(user_data.password)
            user_dict = user_data.model_dump(exclude={'password'})
            user_dict['password_hash'] = hashed_password
            if user_data.rol == RolUsuario.administrador:
                user_dict['correo_institucional'] = None
            else:
                user_dict['username'] = None
            new_user = usuario_crud.create(db=db, obj_in=user_dict)
            await self._send_welcome_email_if_needed(new_user)
            return new_user
        except IntegrityError as e:
            db.rollback()
            self._handle_integrity_error(e)

    def _validate_user_registration(self, user_data: UsuarioCreate) -> None:
        if user_data.rol == RolUsuario.administrador:
            if not user_data.username or user_data.correo_institucional:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Administrador debe tener username y NO debe tener correo_institucional"
                )
        else:
            if not user_data.correo_institucional or user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Usuario no-administrador debe tener correo_institucional y NO debe tener username"
                )

    def _validate_password_strength(self, password: str) -> None:
        is_strong, message = is_strong_password(password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )

    async def _send_welcome_email_if_needed(self, user: Usuario) -> None:
        if user.correo_institucional:
            try:
                await self.email_service.send_template_email(
                    to_email=user.correo_institucional,
                    subject="Bienvenido a Acadify",
                    template_name="welcome.html",
                    context={
                        "nombre": f"{user.nombres} {user.apellidos}",
                        "rol": user.rol.value
                    }
                )
            except Exception as e:
                logger.error(f"Error enviando email de bienvenida: {e}")

    def _handle_integrity_error(self, e: IntegrityError) -> None:
        msg = str(e)
        if "correo_institucional" in msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo institucional ya está registrado"
            )
        elif "username" in msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está registrado"
            )
        elif "numero_documento" in msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El número de documento ya está registrado"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    # ===============================
    # User Authentication
    # ===============================
    
    async def authenticate_user(
        self, 
        db: Session, 
        login_data: LoginRequest
    ) -> Dict[str, Any]:
        """
        Autenticar usuario con flujo completo incluyendo 2FA
        Retorna tokens o estado intermedio si requiere OTP
        """
        raw_identifier = login_data.identifier.strip()

        # Normalizar identifier:
        # - Si parece un email (contiene '@') lo normalizamos a minúsculas
        # - Si es un username, preservamos mayúsculas/minúsculas porque los
        #   usernames pueden ser case-sensitive en la base de datos
        if "@" in raw_identifier:
            identifier = raw_identifier.lower()
            id_type = "email"
        else:
            identifier = raw_identifier
            id_type = "username"

        # 1. Verificar lockout
        lockout_info = await self.login_attempts.is_account_locked(identifier)
        if lockout_info:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=lockout_info["message"]
            )

        # 2. Buscar usuario por identifier (preferir búsqueda por tipo detectado)
        logger.info(f"Buscando usuario con identifier: '{identifier}' (tipo: {id_type})")
        user = self._get_user_by_identifier(db, identifier)
        if not user:
            logger.warning(f"Usuario no encontrado con identifier: '{identifier}' (tipo: {id_type})")
            await self.login_attempts.record_failed_attempt(identifier)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        logger.info(f"Usuario encontrado: {user.usuario_id} - username: '{user.username}' - email: '{user.correo_institucional}'")

        # 3. Verificar que usuarios no-admin usen email para login
        # Si el identificador provino de un username (id_type == 'username') y
        # el usuario NO es administrador, rechazamos el intento.
        if user.rol != RolUsuario.administrador and id_type == "username":
            await self.login_attempts.record_failed_attempt(identifier)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Los usuarios deben iniciar sesión con email"
            )

        # 4. Verificar estado de cuenta
        if user.estado_cuenta != EstadoCuentaUsuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta inactiva o suspendida"
            )

        # 5. Verificar contraseña
        if not security_manager.verify_password(login_data.password, user.password_hash):
            attempt_result = await self.login_attempts.record_failed_attempt(identifier)

            if attempt_result["locked"]:
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=attempt_result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=attempt_result["message"]
                )

        # 6. Verificar si necesita rehash de contraseña
        if security_manager.needs_update(user.password_hash):
            new_hash = security_manager.get_password_hash(login_data.password)
            usuario_crud.update_password_hash(db, user_id=user.usuario_id, new_hash=new_hash)

        # LOG para depuración: mostrar si el usuario tiene 2FA activado
        logger.info(f"Login para usuario {user.usuario_id} ({user.username or user.correo_institucional}), twofa_enabled={user.twofa_enabled}")

        # 7. Verificar 2FA si está habilitado
        if user.twofa_enabled:
            logger.info(f"Usuario {user.usuario_id} requiere 2FA para login")
            return await self._handle_2fa_login(db, user, login_data.otp_code)

        # 8. Login exitoso sin 2FA
        logger.info(f"Usuario {user.usuario_id} inicia sesión SIN 2FA")
        await self.login_attempts.clear_attempts(identifier)
        return self._complete_login(db, user)
    
    async def _handle_2fa_login(
        self, 
        db: Session, 
        user: Usuario, 
        otp_code: Optional[str]
    ) -> Dict[str, Any]:
        """Manejar flujo de 2FA en login"""
        twofa_method = getattr(user, 'twofa_method', 'email')  # default email si no existe campo
        
        if twofa_method == "email":
            return await self._handle_email_2fa_login(db, user, otp_code)
        elif twofa_method == "totp":
            return await self._handle_totp_2fa_login(db, user, otp_code)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Método 2FA no soportado"
            )
    
    async def _handle_email_2fa_login(
        self, 
        db: Session, 
        user: Usuario, 
        otp_code: Optional[str]
    ) -> Dict[str, Any]:
        """Manejar 2FA por email en login"""
        identifier = user.correo_institucional or user.username
        otp_key = f"login_otp:{identifier}"
        
        if not otp_code:
            # Primer paso: generar y enviar OTP
            otp = security_manager.generate_otp_code()
            await self.redis.setex(otp_key, 300, otp)  # 5 minutos TTL
            
            try:
                await self.email_service.send_template_email(
                    to_email=user.correo_institucional,
                    subject="Código de verificación - Acadify",
                    template_name="login_otp.html",
                    context={
                        "nombre": f"{user.nombres} {user.apellidos}",
                        "codigo": otp,
                        "valido_hasta": "5 minutos"
                    }
                )
            except Exception as e:
                logger.error(f"Error enviando OTP por email: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error enviando código de verificación"
                )
            
            return {
                "status": "otp_required",
                "message": "Se envió un código de verificación a su correo. Reenvíe la solicitud incluyendo el código.",
                "requires_otp": True,
                "otp_method": "email"
            }
        
        else:
            # Segundo paso: verificar OTP
            stored_otp = await self.redis.get(otp_key)
            if not stored_otp or stored_otp != otp_code:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Código de verificación inválido o expirado"
                )
            
            # OTP válido, limpiar y completar login
            await self.redis.delete(otp_key)
            await self.login_attempts.clear_attempts(identifier)
            return self._complete_login(db, user)
    
    async def _handle_totp_2fa_login(
        self, 
        db: Session, 
        user: Usuario, 
        otp_code: Optional[str]
    ) -> Dict[str, Any]:
        """Manejar 2FA por TOTP en login"""
        if not otp_code:
            return {
                "status": "otp_required",
                "message": "Se requiere código de autenticación TOTP",
                "requires_otp": True,
                "otp_method": "totp"
            }
        
        if not user.twofa_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Secret TOTP no configurado"
            )
        
        if not security_manager.verify_totp_code(user.twofa_secret, otp_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Código TOTP inválido"
            )
        
        # TOTP válido, completar login
        identifier = user.correo_institucional or user.username
        await self.login_attempts.clear_attempts(identifier)
        return self._complete_login(db, user)
    
    def _complete_login(self, db: Session, user: Usuario) -> Dict[str, Any]:
        """Completar login exitoso generando tokens"""
        # Actualizar último acceso
        usuario_crud.update_last_access(db, user_id=user.usuario_id)
        # Generar tokens
        access_token = security_manager.create_access_token(
            subject=str(user.usuario_id),
            additional_claims={
                "rol": user.rol.value,
                "email": user.correo_institucional,
                "username": user.username
            }
        )
        refresh_token, _ = security_manager.create_refresh_token(
            subject=str(user.usuario_id)
        )
        return {
            "status": "success",
            "tokens": TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ).model_dump()
        }
    
    def _get_user_by_identifier(self, db: Session, identifier: str) -> Optional[Usuario]:
        """Buscar usuario por email o username (case-insensitive)"""
        # Si el identifier contiene '@' asumimos que es un email
        if "@" in identifier:
            user = usuario_crud.get_by_email(db, email=identifier)
            if user:
                return user

        # Intentar por username (now case-insensitive in CRUD)
        return usuario_crud.get_by_username(db, username=identifier)
    
    # ===============================
    # Token Management
    # ===============================
    
    async def refresh_token(self, db: Session, refresh_token: str) -> TokenResponse:
        """Refrescar access token usando refresh token"""
        try:
            # Decodificar y validar refresh token
            payload = security_manager.decode_token(refresh_token)
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token tipo inválido"
                )
            
            # Verificar blacklist
            if await self.token_blacklist.is_blacklisted(refresh_token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token inválido"
                )
            
            # Obtener usuario
            user_id = UUID(payload.get("sub"))
            user = usuario_crud.get(db, id=user_id)
            
            if not user or user.estado_cuenta != EstadoCuentaUsuario.activo:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no válido"
                )
            
            # Generar nuevo access token
            access_token = security_manager.create_access_token(
                subject=str(user.usuario_id),
                additional_claims={
                    "rol": user.rol.value,
                    "email": user.correo_institucional,
                    "username": user.username
                }
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,  # Mantener el mismo refresh token
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Error refrescando token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
    
    async def logout(self, access_token: str, refresh_token: str) -> Dict[str, str]:
        """Logout añadiendo tokens a blacklist"""
        try:
            # Decodificar tokens para obtener expiración
            access_payload = security_manager.decode_token(access_token)
            refresh_payload = security_manager.decode_token(refresh_token)
            
            # Añadir a blacklist con TTL hasta expiración
            access_exp = datetime.fromtimestamp(access_payload["exp"])
            refresh_exp = datetime.fromtimestamp(refresh_payload["exp"])
            
            await self.token_blacklist.add_token(access_token, access_exp)
            await self.token_blacklist.add_token(refresh_token, refresh_exp)
            
            return {"message": "Logout exitoso"}
            
        except Exception as e:
            logger.error(f"Error en logout: {e}")
            # Aún así consideramos logout exitoso
            return {"message": "Logout exitoso"}
    
    # ===============================
    # Password Reset
    # ===============================
    
    async def request_password_reset(
        self, 
        db: Session, 
        reset_request: PasswordResetRequest
    ) -> Dict[str, str]:
        """Solicitar reset de contraseña"""
        email = reset_request.correo_institucional.lower().strip()
        user = usuario_crud.get_by_email(db, email=email)
        
        # Por seguridad, siempre devolver el mismo mensaje
        message = "Si el email existe, se envió un código de recuperación"
        
        if user:
            try:
                # Generar código de reset (6 dígitos)
                reset_code = security_manager.generate_otp_code()
                reset_key = f"reset_token:{user.usuario_id}"
                
                # Guardar en Redis con TTL de 15 minutos
                await self.redis.setex(reset_key, 900, reset_code)
                
                # Enviar email
                await self.email_service.send_template_email(
                    to_email=email,
                    subject="Recuperación de contraseña - Acadify",
                    template_name="reset_password.html",
                    context={
                        "nombre": f"{user.nombres} {user.apellidos}",
                        "codigo": reset_code,
                        "valido_hasta": "15 minutos"
                    }
                )
                
            except Exception as e:
                logger.error(f"Error enviando reset email: {e}")
                # No revelamos el error al usuario
        
        return {"message": message}
    
    async def reset_password(
        self, 
        db: Session, 
        reset_confirm: PasswordResetConfirm
    ) -> Dict[str, str]:
        """Confirmar reset de contraseña"""
        email = reset_confirm.correo_institucional.lower().strip()
        user = usuario_crud.get_by_email(db, email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        # Verificar código de reset
        reset_key = f"reset_token:{user.usuario_id}"
        stored_code = await self.redis.get(reset_key)
        if not stored_code or stored_code != reset_confirm.reset_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código de recuperación inválido o expirado"
            )
        # Cambiar contraseña
        new_hash = security_manager.get_password_hash(reset_confirm.new_password)
        usuario_crud.update_password_hash(db, user_id=user.usuario_id, new_hash=new_hash)
        # Limpiar código de reset
        await self.redis.delete(reset_key)
        # Notificar cambio por email
        try:
            await self.email_service.send_template_email(
                to_email=email,
                subject="Contraseña actualizada - Acadify",
                template_name="password_changed.html",
                context={
                    "nombre": f"{user.nombres} {user.apellidos}",
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            )
        except Exception as e:
            logger.error(f"Error enviando confirmación de cambio: {e}")
        return {"message": "Contraseña actualizada exitosamente"}
    
    def change_password(
        self, 
        db: Session, 
        user_id: UUID, 
        change_request: PasswordChangeRequest
    ) -> Dict[str, str]:
        """Cambiar contraseña (usuario autenticado)"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        # Verificar contraseña actual
        if not security_manager.verify_password(change_request.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta"
            )
        # Cambiar contraseña
        new_hash = security_manager.get_password_hash(change_request.new_password)
        usuario_crud.update_password_hash(db, user_id=user_id, new_hash=new_hash)
        return {"message": "Contraseña actualizada exitosamente"}
    
    # ===============================
    # Two-Factor Authentication
    # ===============================
    
    async def setup_2fa(
        self, 
        db: Session, 
        user_id: UUID, 
        setup_request: TwoFASetupRequest
    ) -> TwoFASetupResponse:
        """Iniciar configuración de 2FA"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        if setup_request.method == "email":
            return await self._setup_email_2fa(user)
        elif setup_request.method == "totp":
            return await self._setup_totp_2fa(user)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Método 2FA no soportado"
            )
    
    async def _setup_email_2fa(self, user: Usuario) -> TwoFASetupResponse:
        """Configurar 2FA por email"""
        if not user.correo_institucional:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Usuario debe tener correo institucional para 2FA por email"
            )
        
        # Generar código de verificación
        verification_code = security_manager.generate_otp_code()
        setup_key = f"2fa_setup:{user.usuario_id}"
        
        # Guardar configuración temporal
        setup_data = {
            "method": "email",
            "code": verification_code
        }
        await self.redis.setex(setup_key, 600, str(setup_data))  # 10 minutos
        
        # Enviar código por email
        try:
            await self.email_service.send_template_email(
                to_email=user.correo_institucional,
                subject="Activar autenticación de dos factores - Acadify",
                template_name="2fa_setup.html",
                context={
                    "nombre": f"{user.nombres} {user.apellidos}",
                    "codigo": verification_code,
                    "metodo": "email"
                }
            )
        except Exception as e:
            logger.error(f"Error enviando email 2FA setup: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error enviando código de verificación"
            )
        
        return TwoFASetupResponse(
            method="email",
            message="Se envió un código de verificación al correo para activar 2FA"
        )
    
    async def _setup_totp_2fa(self, user: Usuario) -> TwoFASetupResponse:
        """Configurar 2FA por TOTP"""
        # Generar secret
        secret = security_manager.generate_totp_secret()
        
        # Generar URI de provisioning
        email = user.correo_institucional or user.username
        qr_url = security_manager.get_totp_provisioning_uri(email, secret)
        
        # Generar códigos de respaldo
        backup_codes = [security_manager.generate_otp_code(8) for _ in range(10)]
        
        # Guardar configuración temporal
        setup_key = f"2fa_setup:{user.usuario_id}"
        setup_data = {
            "method": "totp",
            "secret": secret,
            "backup_codes": backup_codes
        }
        await self.redis.setex(setup_key, 600, str(setup_data))  # 10 minutos
        
        return TwoFASetupResponse(
            method="totp",
            message="Escanea el código QR con tu app de autenticación y confirma con un código",
            secret=secret,
            qr_code_url=qr_url,
            backup_codes=backup_codes
        )
    
    async def verify_2fa_setup(
        self, 
        db: Session, 
        user_id: UUID, 
        verify_request: TwoFAVerifyRequest
    ) -> Dict[str, Any]:
        """Verificar configuración de 2FA"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        
        # Obtener datos de configuración temporal
        setup_key = f"2fa_setup:{user_id}"
        setup_data_str = await self.redis.get(setup_key)
        
        if not setup_data_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuración de 2FA expirada o no encontrada"
            )
        
        # Parse setup data (en producción usar JSON)
        setup_data = eval(setup_data_str)  # Simplificado para el ejemplo
        
        code = verify_request.verification_code
        method = setup_data["method"]
        
        if method == "email":
            stored_code = setup_data["code"]
            if stored_code != code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código de verificación incorrecto"
                )
        
        elif method == "totp":
            secret = setup_data["secret"]
            if not security_manager.verify_totp_code(secret, code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Código TOTP incorrecto"
                )
            
            # Guardar secret en usuario
            usuario_crud.update_2fa_secret(db, user_id=user_id, secret=secret)
        
        # Activar 2FA
        usuario_crud.enable_2fa(db, user_id=user_id, method=method)
        
        # Limpiar configuración temporal
        await self.redis.delete(setup_key)
        
        return {
            "success": True,
            "message": f"2FA por {method} activado exitosamente",
            "twofa_enabled": True
        }
    
    def disable_2fa(
        self, 
        db: Session, 
        user_id: UUID, 
        current_password: str
    ) -> Dict[str, str]:
        """Desactivar 2FA"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        # Verificar contraseña actual
        if not security_manager.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña incorrecta"
            )
        # Desactivar 2FA
        usuario_crud.disable_2fa(db, user_id=user_id)
        return {"message": "2FA desactivado exitosamente"}
    
    # ===============================
    # User Profile Management
    # ===============================
    
    def get_current_user_profile(self, db: Session, user_id: UUID) -> UserCurrentResponse:
        """Obtener perfil del usuario actual"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        return UserCurrentResponse.model_validate(user)
    
    def update_user_profile(
        self, 
        db: Session, 
        user_id: UUID, 
        update_data: UserProfileUpdate
    ) -> UserCurrentResponse:
        """Actualizar perfil de usuario"""
        user = usuario_crud.get(db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=USER_NOT_FOUND
            )
        # Actualizar solo los campos proporcionados
        update_dict = update_data.model_dump(exclude_unset=True)
        updated_user = usuario_crud.update(db, db_obj=user, obj_in=update_dict)
        return UserCurrentResponse.model_validate(updated_user)