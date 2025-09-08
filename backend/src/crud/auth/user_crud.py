from datetime import timedelta, datetime
from src.utils.datetime_utils import utcnow_aware
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import uuid

from src.models.users.usuario import Usuario
from src.models.users.oauth_provider import OAuthProvider
from src.schemas.auth.user_auth_schemas import UserRegisterRequest, UserProfileUpdate
from src.schemas.users.usuario import UsuarioCreate, UsuarioUpdate
from src.services.auth.password_service import PasswordService
from src.enums.users.usuario_enums import RolUsuario, EstadoCuentaUsuario


class UserCRUD:
    """CRUD operations para usuarios"""
    
    def __init__(self, password_service: PasswordService):
        self.password_service = password_service
    
    def get_by_id(self, db: Session, user_id: str) -> Optional[Usuario]:
        """Obtener usuario por ID"""
        return db.query(Usuario).filter(Usuario.usuario_id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        """Obtener usuario por email institucional"""
        return db.query(Usuario).filter(
            Usuario.correo_institucional == email.lower()
        ).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        """Obtener usuario por username (solo administradores)"""
        return db.query(Usuario).filter(Usuario.username == username).first()
    
    def get_by_document(self, db: Session, tipo_documento: str, numero_documento: str) -> Optional[Usuario]:
        """Obtener usuario por documento"""
        return db.query(Usuario).filter(
            and_(
                Usuario.tipo_documento == tipo_documento,
                Usuario.numero_documento == numero_documento
            )
        ).first()
    
    def create_user(self, db: Session, user_create: UserRegisterRequest) -> Usuario:
        """
        Crear nuevo usuario con validaciones de seguridad
        
        Args:
            db: Sesión de base de datos
            user_create: Datos del usuario a crear
        
        Returns:
            Usuario: Usuario creado
        
        Raises:
            ValueError: Si el usuario ya existe o datos inválidos
        """
        # Verificar si el usuario ya existe
        if user_create.correo_institucional:
            existing_user = self.get_by_email(db, user_create.correo_institucional)
            if existing_user:
                raise ValueError("Ya existe un usuario con este email institucional")
        
        if user_create.username:
            existing_user = self.get_by_username(db, user_create.username)
            if existing_user:
                raise ValueError("Ya existe un usuario con este nombre de usuario")
        
        # Verificar documento
        existing_user = self.get_by_document(
            db, user_create.tipo_documento, user_create.numero_documento
        )
        if existing_user:
            raise ValueError("Ya existe un usuario con este documento")
        
        # Validar política de contraseñas
        is_valid, errors = self.password_service.validate_password_policy(user_create.password)
        if not is_valid:
            raise ValueError(f"Contraseña no cumple políticas: {', '.join(errors)}")
        
        # Crear usuario
        hashed_password = self.password_service.hash_password(user_create.password)
        
        db_user = Usuario(
            usuario_id=uuid.uuid4(),
            correo_institucional=user_create.correo_institucional.lower() if user_create.correo_institucional else None,
            username=user_create.username,
            nombres=user_create.nombres,
            apellidos=user_create.apellidos,
            tipo_documento=user_create.tipo_documento,
            numero_documento=user_create.numero_documento,
            rol=user_create.rol,
            password_hash=hashed_password,
            telefono=user_create.telefono,
            descripcion=user_create.descripcion,
            estado_cuenta=EstadoCuentaUsuario.activo,
            email_verified=False,  # Por defecto no verificado
            failed_login_attempts=0,
            twofa_enabled=False,
            fecha_creacion=utcnow_aware(),
            ultimo_acceso=None
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def update_user(
        self, 
        db: Session, 
        user_id: str, 
        user_update: UserProfileUpdate, 
        current_user: Usuario = None
    ) -> Optional[Usuario]:
        """
        Actualizar usuario (solo campos permitidos según rol)
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario a actualizar
            user_update: Datos a actualizar
            current_user: Usuario que realiza la actualización
        
        Returns:
            Usuario actualizado o None si no existe
        """
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        # Verificar permisos: solo el propio usuario o admin puede actualizar
        if current_user:
            if str(current_user.usuario_id) != user_id and current_user.rol != RolUsuario.administrador:
                raise ValueError("No tiene permisos para actualizar este usuario")
        
        # Actualizar campos permitidos
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update_password(
        self, 
        db: Session, 
        user_id: str, 
        new_password: str,
        verify_current: bool = True,
        current_password: str = None
    ) -> bool:
        """
        Actualizar contraseña de usuario
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_password: Nueva contraseña
            verify_current: Si verificar contraseña actual
            current_password: Contraseña actual (si verify_current=True)
        
        Returns:
            bool: True si se actualizó correctamente
        """
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        # Verificar contraseña actual si es necesario
        if verify_current and current_password:
            if not self.password_service.verify_password(current_password, db_user.password_hash):
                raise ValueError("Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        is_valid, errors = self.password_service.validate_password_policy(new_password)
        if not is_valid:
            raise ValueError(f"Nueva contraseña no cumple políticas: {', '.join(errors)}")
        
        # Actualizar contraseña
        hashed_password = self.password_service.hash_password(new_password)
        db_user.password_hash = hashed_password
        
        # Resetear intentos de login fallidos
        db_user.failed_login_attempts = 0
        db_user.locked_until = None
        
        db.commit()
        return True
    
    def verify_password(self, db: Session, user_id: str, password: str) -> bool:
        """Verificar contraseña de usuario"""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        return self.password_service.verify_password(password, db_user.password_hash)
    
    def increment_failed_attempts(self, db: Session, user_id: str) -> int:
        """Incrementar contador de intentos fallidos"""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return 0
        
        db_user.failed_login_attempts += 1
        
        # Bloquear cuenta si supera el límite
        if db_user.failed_login_attempts >= 5:  # settings.MAX_LOGIN_ATTEMPTS
            lockout_duration = timedelta(minutes=15)  # settings.LOCKOUT_DURATION_MINUTES
            db_user.locked_until = utcnow_aware() + lockout_duration
        
        db.commit()
        return db_user.failed_login_attempts
    
    def reset_failed_attempts(self, db: Session, user_id: str):
        """Resetear contador de intentos fallidos (login exitoso)"""
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.failed_login_attempts = 0
            db_user.locked_until = None
            db_user.ultimo_acceso = utcnow_aware()
            db.commit()
    
    def is_account_locked(self, db: Session, user_id: str) -> tuple[bool, Optional[datetime]]:
        """Verificar si la cuenta está bloqueada"""
        db_user = self.get_by_id(db, user_id)
        if not db_user or not db_user.locked_until:
            return False, None
        if utcnow_aware() >= db_user.locked_until:
            # El bloqueo expiró, limpiarlo
            db_user.locked_until = None
            db_user.failed_login_attempts = 0
            db.commit()
            return False, None
        return True, db_user.locked_until
    
    def set_email_verified(self, db: Session, user_id: str, verified: bool = True):
        """Marcar email como verificado"""
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.email_verified = verified
            db.commit()
    
    def enable_2fa(self, db: Session, user_id: str, secret: str):
        """Habilitar 2FA para usuario"""
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.twofa_enabled = True
            db_user.twofa_secret = secret
            db.commit()
    
    def disable_2fa(self, db: Session, user_id: str):
        """Deshabilitar 2FA para usuario"""
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.twofa_enabled = False
            db_user.twofa_secret = None
            db.commit()
    
    def get_users_paginated(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        role_filter: Optional[RolUsuario] = None,
        search: Optional[str] = None
    ) -> tuple[List[Usuario], int]:
        """
        Obtener usuarios con paginación y filtros
        
        Returns:
            tuple: (usuarios, total_count)
        """
        query = db.query(Usuario)
        
        # Filtrar por rol
        if role_filter:
            query = query.filter(Usuario.rol == role_filter)
        
        # Búsqueda por texto
        if search:
            search_filter = or_(
                Usuario.nombres.ilike(f"%{search}%"),
                Usuario.apellidos.ilike(f"%{search}%"),
                Usuario.correo_institucional.ilike(f"%{search}%"),
                Usuario.numero_documento.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total_count = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total_count
    
    def delete_user(self, db: Session, user_id: str) -> bool:
        """Eliminar usuario (soft delete cambiando estado)"""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db_user.estado_cuenta = EstadoCuentaUsuario.inactivo
        db.commit()
        return True
    
    def lock_user_account(self, db: Session, user_id: str, duration_minutes: int = None):
        """Bloquear cuenta de usuario (admin action)"""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        if duration_minutes:
            db_user.locked_until = utcnow_aware() + timedelta(minutes=duration_minutes)
        else:
            # Bloqueo indefinido
            db_user.estado_cuenta = EstadoCuentaUsuario.bloqueado
        
        db.commit()
        return True