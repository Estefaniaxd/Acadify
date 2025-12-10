"""
CRUD operations para OAuth Providers.

Maneja las operaciones de base de datos para vincular proveedores OAuth
(Google, Microsoft, etc.) con usuarios de Acadify.
"""

from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.users.oauth_provider import OAuthProvider
from src.models.users.usuario import Usuario


class OAuthCRUD:
    """CRUD para manejar proveedores OAuth."""

    @staticmethod
    def create_or_update(
        db: Session,
        usuario_id: UUID,
        provider: str,
        provider_user_id: str,
        provider_email: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None
    ) -> OAuthProvider:
        """
        Crea o actualiza un proveedor OAuth para un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario de Acadify
            provider: Nombre del proveedor ('google', 'microsoft', etc.)
            provider_user_id: ID del usuario en el proveedor
            provider_email: Email del usuario en el proveedor
            access_token: Token de acceso (opcional, para almacenamiento futuro)
            refresh_token: Token de actualización (opcional)
            token_expiry: Fecha de expiración del token (opcional)
            
        Returns:
            OAuthProvider: Registro del proveedor OAuth
            
        Raises:
            IntegrityError: Si hay conflicto de unicidad
        """
        # Buscar si ya existe
        existing = db.query(OAuthProvider).filter(
            OAuthProvider.provider == provider,
            OAuthProvider.provider_user_id == provider_user_id
        ).first()
        
        if existing:
            # Actualizar el registro existente
            existing.usuario_id = usuario_id
            existing.provider_email = provider_email
            if access_token:
                existing.access_token = access_token
            if refresh_token:
                existing.refresh_token = refresh_token
            if token_expiry:
                existing.token_expiry = token_expiry
            db.commit()
            db.refresh(existing)
            return existing
        
        # Crear nuevo registro
        oauth_provider = OAuthProvider(
            usuario_id=usuario_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expiry=token_expiry
        )
        
        db.add(oauth_provider)
        db.commit()
        db.refresh(oauth_provider)
        
        return oauth_provider

    @staticmethod
    def get_by_provider_and_user_id(
        db: Session,
        provider: str,
        provider_user_id: str
    ) -> OAuthProvider | None:
        """
        Obtiene un proveedor OAuth por nombre de proveedor y ID de usuario del proveedor.
        
        Args:
            db: Sesión de base de datos
            provider: Nombre del proveedor
            provider_user_id: ID del usuario en el proveedor
            
        Returns:
            OAuthProvider | None: Registro del proveedor o None si no existe
        """
        return db.query(OAuthProvider).filter(
            OAuthProvider.provider == provider,
            OAuthProvider.provider_user_id == provider_user_id
        ).first()

    @staticmethod
    def get_by_usuario_and_provider(
        db: Session,
        usuario_id: UUID,
        provider: str
    ) -> OAuthProvider | None:
        """
        Obtiene un proveedor OAuth por ID de usuario de Acadify y proveedor.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario de Acadify
            provider: Nombre del proveedor
            
        Returns:
            OAuthProvider | None: Registro del proveedor o None si no existe
        """
        return db.query(OAuthProvider).filter(
            OAuthProvider.usuario_id == usuario_id,
            OAuthProvider.provider == provider
        ).first()

    @staticmethod
    def get_all_by_usuario(
        db: Session,
        usuario_id: UUID
    ) -> list[OAuthProvider]:
        """
        Obtiene todos los proveedores OAuth de un usuario.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario de Acadify
            
        Returns:
            list[OAuthProvider]: Lista de proveedores OAuth del usuario
        """
        return db.query(OAuthProvider).filter(
            OAuthProvider.usuario_id == usuario_id
        ).all()

    @staticmethod
    def delete(
        db: Session,
        oauth_provider_id: UUID
    ) -> bool:
        """
        Elimina un proveedor OAuth.
        
        Args:
            db: Sesión de base de datos
            oauth_provider_id: ID del proveedor OAuth
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        oauth_provider = db.query(OAuthProvider).filter(
            OAuthProvider.oauth_provider_id == oauth_provider_id
        ).first()
        
        if not oauth_provider:
            return False
        
        db.delete(oauth_provider)
        db.commit()
        
        return True

    @staticmethod
    def delete_by_usuario_and_provider(
        db: Session,
        usuario_id: UUID,
        provider: str
    ) -> bool:
        """
        Elimina un proveedor OAuth por usuario y proveedor.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario de Acadify
            provider: Nombre del proveedor
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        oauth_provider = OAuthCRUD.get_by_usuario_and_provider(
            db, usuario_id, provider
        )
        
        if not oauth_provider:
            return False
        
        db.delete(oauth_provider)
        db.commit()
        
        return True

    @staticmethod
    def is_linked(
        db: Session,
        usuario_id: UUID,
        provider: str
    ) -> bool:
        """
        Verifica si un usuario tiene vinculado un proveedor OAuth.
        
        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario de Acadify
            provider: Nombre del proveedor
            
        Returns:
            bool: True si está vinculado, False si no
        """
        return OAuthCRUD.get_by_usuario_and_provider(
            db, usuario_id, provider
        ) is not None


# Instancia global del CRUD
crud_oauth_provider = OAuthCRUD()
