from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid

from src.models.users.oauth_provider import OAuthProvider
from src.models.users.usuario import Usuario


class OAuthCRUD:
    """CRUD operations para OAuth providers"""
    
    def get_by_provider_and_user_id(
        self, 
        db: Session, 
        provider: str, 
        provider_user_id: str
    ) -> Optional[OAuthProvider]:
        """Obtener provider por nombre y ID de usuario del proveedor"""
        return db.query(OAuthProvider).filter(
            and_(
                OAuthProvider.provider == provider,
                OAuthProvider.provider_user_id == provider_user_id
            )
        ).first()
    
    def get_by_user_id(self, db: Session, user_id: str) -> List[OAuthProvider]:
        """Obtener todos los providers de un usuario"""
        return db.query(OAuthProvider).filter(
            OAuthProvider.usuario_id == user_id
        ).all()
    
    def create_oauth_link(
        self,
        db: Session,
        user_id: str,
        provider: str,
        provider_user_id: str,
        provider_email: str
    ) -> OAuthProvider:
        """Crear vinculación OAuth"""
        oauth_provider = OAuthProvider(
            oauth_provider_id=uuid.uuid4(),
            usuario_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email
        )
        
        db.add(oauth_provider)
        db.commit()
        db.refresh(oauth_provider)
        
        return oauth_provider
    
    def remove_oauth_link(
        self, 
        db: Session, 
        user_id: str, 
        provider: str
    ) -> bool:
        """Eliminar vinculación OAuth"""
        oauth_provider = db.query(OAuthProvider).filter(
            and_(
                OAuthProvider.usuario_id == user_id,
                OAuthProvider.provider == provider
            )
        ).first()
        
        if oauth_provider:
            db.delete(oauth_provider)
            db.commit()
            return True
        
        return False