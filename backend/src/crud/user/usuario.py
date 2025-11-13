# src/crud/user/usuario.py

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.crud.base import CRUDBase
from src.enums.users.usuario_enums import EstadoCuentaUsuario, RolUsuario
from src.models.users.usuario import Usuario
from src.schemas.users.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """CRUD operations for Usuario model."""

    # ===============================
    # Override Base Methods for usuario_id
    # ===============================

    def get(self, db: Session, id: UUID) -> Usuario | None:
        """Get user by usuario_id (override base method)."""
        return db.query(Usuario).filter(Usuario.usuario_id == id).first()

    def exists(self, db: Session, *, id: UUID) -> bool:
        """Check if user exists by usuario_id."""
        return db.query(Usuario).filter(Usuario.usuario_id == id).first() is not None

    # ===============================
    # Basic CRUD Operations
    # ===============================

    def create(self, db: Session, *, obj_in: dict[str, Any]) -> Usuario:
        """Create new user with proper constraint validation."""
        try:
            db_obj = Usuario(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise

    def get_by_email(self, db: Session, *, email: str) -> Usuario | None:
        """Get user by institutional email (case-insensitive search)."""
        return (
            db.query(Usuario)
            .filter(Usuario.correo_institucional.ilike(email.strip()))
            .first()
        )

    def get_by_username(self, db: Session, *, username: str) -> Usuario | None:
        """Get user by username (case-insensitive search)."""
        return (
            db.query(Usuario).filter(Usuario.username.ilike(username.strip())).first()
        )

    def get_by_document(self, db: Session, *, numero_documento: str) -> Usuario | None:
        """Get user by document number."""
        return (
            db.query(Usuario)
            .filter(Usuario.numero_documento == numero_documento)
            .first()
        )

    def get_by_identifier(self, db: Session, *, identifier: str) -> Usuario | None:
        """Get user by email or username (case-insensitive search)."""
        identifier = identifier.strip()
        return (
            db.query(Usuario)
            .filter(
                or_(
                    Usuario.correo_institucional.ilike(identifier),
                    Usuario.username.ilike(identifier),
                )
            )
            .first()
        )

    def get_active_users(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[Usuario]:
        """Get active users with pagination."""
        return (
            db.query(Usuario)
            .filter(Usuario.estado_cuenta == EstadoCuentaUsuario.activo)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_users_by_role(
        self, db: Session, *, rol: RolUsuario, skip: int = 0, limit: int = 100
    ) -> list[Usuario]:
        """Get users by role with pagination."""
        return (
            db.query(Usuario)
            .filter(
                Usuario.rol == rol, Usuario.estado_cuenta == EstadoCuentaUsuario.activo
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_users(
        self,
        db: Session,
        *,
        query: str,
        role: RolUsuario | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Usuario]:
        """Search users by name, email or document."""
        search_term = f"%{query.lower()}%"

        filters = [
            or_(
                Usuario.nombres.ilike(search_term),
                Usuario.apellidos.ilike(search_term),
                Usuario.correo_institucional.ilike(search_term),
                Usuario.numero_documento.ilike(search_term),
            ),
            Usuario.estado_cuenta == EstadoCuentaUsuario.activo,
        ]

        if role:
            filters.append(Usuario.rol == role)

        return db.query(Usuario).filter(*filters).offset(skip).limit(limit).all()

    def count_users_by_role(self, db: Session, *, rol: RolUsuario) -> int:
        """Count users by role."""
        return (
            db.query(Usuario)
            .filter(
                Usuario.rol == rol, Usuario.estado_cuenta == EstadoCuentaUsuario.activo
            )
            .count()
        )

    # ===============================
    # Authentication Related Operations
    # ===============================

    def update_password_hash(
        self, db: Session, *, user_id: UUID, new_hash: str
    ) -> Usuario:
        """Update user password hash."""
        user = self.get(db, id=user_id)
        if user:
            user.password_hash = new_hash
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def update_last_access(self, db: Session, *, user_id: UUID) -> Usuario:
        """Update user last access timestamp."""
        user = self.get(db, id=user_id)
        if user:
            user.ultimo_acceso = datetime.now(UTC)
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def increment_failed_login_attempts(self, db: Session, *, user_id: UUID) -> Usuario:
        """Increment failed login attempts counter."""
        user = self.get(db, id=user_id)
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def reset_failed_login_attempts(self, db: Session, *, user_id: UUID) -> Usuario:
        """Reset failed login attempts counter."""
        user = self.get(db, id=user_id)
        if user:
            user.failed_login_attempts = 0
            user.locked_until = None
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def lock_user_account(
        self, db: Session, *, user_id: UUID, locked_until: datetime
    ) -> Usuario:
        """Lock user account until specific datetime."""
        user = self.get(db, id=user_id)
        if user:
            user.locked_until = locked_until
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def verify_email(self, db: Session, *, user_id: UUID) -> Usuario:
        """Mark user email as verified."""
        user = self.get(db, id=user_id)
        if user:
            user.email_verified = True
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # ===============================
    # Two-Factor Authentication Operations
    # ===============================

    def enable_2fa(
        self, db: Session, *, user_id: UUID, method: str = "email"
    ) -> Usuario:
        """Enable 2FA for user."""
        user = self.get(db, id=user_id)
        if user:
            user.twofa_enabled = True
            # Si existe campo twofa_method en el modelo
            if hasattr(user, "twofa_method"):
                user.twofa_method = method
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def disable_2fa(self, db: Session, *, user_id: UUID) -> Usuario:
        """Disable 2FA for user."""
        user = self.get(db, id=user_id)
        if user:
            user.twofa_enabled = False
            user.twofa_secret = None
            if hasattr(user, "twofa_method"):
                user.twofa_method = None
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def update_2fa_secret(self, db: Session, *, user_id: UUID, secret: str) -> Usuario:
        """Update 2FA secret for TOTP."""
        user = self.get(db, id=user_id)
        if user:
            user.twofa_secret = secret
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # ===============================
    # Account State Management
    # ===============================

    def activate_account(self, db: Session, *, user_id: UUID) -> Usuario:
        """Activate user account."""
        user = self.get(db, id=user_id)
        if user:
            user.estado_cuenta = EstadoCuentaUsuario.activo
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def deactivate_account(self, db: Session, *, user_id: UUID) -> Usuario:
        """Deactivate user account."""
        user = self.get(db, id=user_id)
        if user:
            user.estado_cuenta = EstadoCuentaUsuario.inactivo
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def suspend_account(self, db: Session, *, user_id: UUID) -> Usuario:
        """Suspend user account."""
        user = self.get(db, id=user_id)
        if user:
            user.estado_cuenta = EstadoCuentaUsuario.suspendido
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def delete_account(self, db: Session, *, user_id: UUID) -> Usuario:
        """Soft delete user account."""
        user = self.get(db, id=user_id)
        if user:
            user.estado_cuenta = EstadoCuentaUsuario.eliminado
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # ===============================
    # Profile Management
    # ===============================

    def update_profile_urls(
        self,
        db: Session,
        *,
        user_id: UUID,
        perfil_url: str | None = None,
        portada_url: str | None = None,
    ) -> Usuario:
        """Update profile and cover image URLs."""
        user = self.get(db, id=user_id)
        if user:
            if perfil_url is not None:
                user.perfil_url = perfil_url
            if portada_url is not None:
                user.portada_url = portada_url
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    def update_contact_info(
        self,
        db: Session,
        *,
        user_id: UUID,
        telefono: str | None = None,
        descripcion: str | None = None,
    ) -> Usuario:
        """Update user contact information."""
        user = self.get(db, id=user_id)
        if user:
            if telefono is not None:
                user.telefono = telefono
            if descripcion is not None:
                user.descripcion = descripcion
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    # ===============================
    # Admin Operations
    # ===============================

    def create_admin_user(self, db: Session, *, obj_in: dict[str, Any]) -> Usuario:
        """Create admin user with proper constraint validation."""
        # Ensure admin constraints
        obj_in["rol"] = RolUsuario.administrador
        obj_in["correo_institucional"] = None

        if not obj_in.get("username"):
            msg = "Admin user must have username"
            raise ValueError(msg)

        return self.create(db, obj_in=obj_in)

    def create_regular_user(self, db: Session, *, obj_in: dict[str, Any]) -> Usuario:
        """Create regular user with proper constraint validation."""
        # Ensure regular user constraints
        if obj_in.get("rol") == RolUsuario.administrador:
            msg = "Use create_admin_user for admin users"
            raise ValueError(msg)

        obj_in["username"] = None

        if not obj_in.get("correo_institucional"):
            msg = "Regular user must have correo_institucional"
            raise ValueError(msg)

        return self.create(db, obj_in=obj_in)

    def get_users_with_stats(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get users with additional stats for admin dashboard."""
        users = self.get_multi(db, skip=skip, limit=limit)

        result = []
        for user in users:
            user_dict = {
                "usuario_id": user.usuario_id,
                "correo_institucional": user.correo_institucional,
                "username": user.username,
                "nombres": user.nombres,
                "apellidos": user.apellidos,
                "rol": user.rol.value,
                "estado_cuenta": user.estado_cuenta.value,
                "email_verified": user.email_verified,
                "twofa_enabled": user.twofa_enabled,
                "fecha_creacion": user.fecha_creacion,
                "ultimo_acceso": user.ultimo_acceso,
                "failed_login_attempts": user.failed_login_attempts,
                "locked_until": user.locked_until,
            }
            result.append(user_dict)

        return result

    # ===============================
    # Bulk Operations
    # ===============================

    def bulk_activate_users(self, db: Session, *, user_ids: list[UUID]) -> int:
        """Bulk activate multiple users."""
        count = (
            db.query(Usuario)
            .filter(Usuario.usuario_id.in_(user_ids))
            .update(
                {Usuario.estado_cuenta: EstadoCuentaUsuario.activo},
                synchronize_session=False,
            )
        )
        db.commit()
        return count

    def bulk_deactivate_users(self, db: Session, *, user_ids: list[UUID]) -> int:
        """Bulk deactivate multiple users."""
        count = (
            db.query(Usuario)
            .filter(Usuario.usuario_id.in_(user_ids))
            .update(
                {Usuario.estado_cuenta: EstadoCuentaUsuario.inactivo},
                synchronize_session=False,
            )
        )
        db.commit()
        return count

    def bulk_reset_failed_attempts(self, db: Session, *, user_ids: list[UUID]) -> int:
        """Bulk reset failed login attempts."""
        count = (
            db.query(Usuario)
            .filter(Usuario.usuario_id.in_(user_ids))
            .update(
                {Usuario.failed_login_attempts: 0, Usuario.locked_until: None},
                synchronize_session=False,
            )
        )
        db.commit()
        return count

    # ===============================
    # Validation Helpers
    # ===============================

    def validate_unique_email(
        self, db: Session, *, email: str, exclude_user_id: UUID | None = None
    ) -> bool:
        """Check if email is unique."""
        query = db.query(Usuario).filter(
            Usuario.correo_institucional == email.lower().strip()
        )

        if exclude_user_id:
            query = query.filter(Usuario.usuario_id != exclude_user_id)

        return query.first() is None

    def validate_unique_username(
        self, db: Session, *, username: str, exclude_user_id: UUID | None = None
    ) -> bool:
        """Check if username is unique."""
        query = db.query(Usuario).filter(Usuario.username == username.lower().strip())

        if exclude_user_id:
            query = query.filter(Usuario.usuario_id != exclude_user_id)

        return query.first() is None

    def validate_unique_document(
        self, db: Session, *, numero_documento: str, exclude_user_id: UUID | None = None
    ) -> bool:
        """Check if document number is unique."""
        query = db.query(Usuario).filter(Usuario.numero_documento == numero_documento)

        if exclude_user_id:
            query = query.filter(Usuario.usuario_id != exclude_user_id)

        return query.first() is None

    def validate_constraint_compliance(self, user_data: dict[str, Any]) -> bool:
        """Validate that user data complies with chk_login constraint."""
        rol = user_data.get("rol")
        correo = user_data.get("correo_institucional")
        username = user_data.get("username")

        if rol == RolUsuario.administrador:
            # Admin: debe tener username y NO tener correo
            return username is not None and correo is None
        # No-admin: debe tener correo y NO tener username
        return correo is not None and username is None


# Create instance
usuario_crud = CRUDUsuario(Usuario)
