"""
CRUD para user avatars.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from src.crud.base import CRUDBase
from src.models.avatar.user_avatar import UserAvatar


class CRUDUserAvatar(CRUDBase[UserAvatar, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations para UserAvatar."""

    def get_by_user(
        self, 
        db: Session, 
        *, 
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserAvatar]:
        """
        Obtiene avatars de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de UserAvatar del usuario
        """
        return (
            db.query(UserAvatar)
            .filter(UserAvatar.user_id == user_id)
            .order_by(desc(UserAvatar.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_avatar(self, db: Session, *, user_id: UUID) -> Optional[UserAvatar]:
        """
        Obtiene el avatar activo de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            UserAvatar activo o None si no tiene
        """
        return (
            db.query(UserAvatar)
            .filter(
                and_(
                    UserAvatar.user_id == user_id,
                    UserAvatar.is_active == True
                )
            )
            .first()
        )

    def get_by_hash(self, db: Session, *, layers_hash: str) -> Optional[UserAvatar]:
        """
        Obtiene un avatar por su hash de capas.
        
        Args:
            db: Sesión de base de datos
            layers_hash: Hash SHA256 de las capas
            
        Returns:
            UserAvatar con ese hash o None
        """
        return (
            db.query(UserAvatar)
            .filter(UserAvatar.layers_hash == layers_hash)
            .first()
        )

    def get_public_avatars(
        self, 
        db: Session, 
        *, 
        skip: int = 0,
        limit: int = 100
    ) -> List[UserAvatar]:
        """
        Obtiene avatars públicos de todos los usuarios.
        
        Args:
            db: Sesión de base de datos
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de UserAvatar públicos
        """
        return (
            db.query(UserAvatar)
            .filter(UserAvatar.is_public == True)
            .order_by(desc(UserAvatar.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_avatar(
        self, 
        db: Session, 
        *, 
        user_id: UUID,
        name: str,
        base_gender: str,
        layers: List[Dict[str, Any]],
        image_url: str,
        layers_hash: str,
        is_active: bool = False,
        is_public: bool = True
    ) -> UserAvatar:
        """
        Crea un nuevo avatar de usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            name: Nombre del avatar
            base_gender: Género base del avatar (male/female)
            layers: Lista de capas del avatar
            image_url: URL de la imagen compuesta
            layers_hash: Hash de las capas
            is_active: Si será el avatar activo
            is_public: Si será público
            
        Returns:
            UserAvatar creado
        """
        avatar_data = {
            "user_id": user_id,
            "name": name,
            "base_gender": base_gender,
            "layers": layers,
            "image_url": image_url,
            "layers_hash": layers_hash,
            "is_active": is_active,
            "is_public": is_public
        }
        
        created_avatar = self.create(db, obj_in=avatar_data)
        
        # Si se marca como activo, desactivar otros avatars del mismo usuario
        if is_active:
            self._deactivate_other_avatars(db, user_id=user_id, exclude_id=created_avatar.id)
        
        return created_avatar

    def set_active_avatar(
        self, 
        db: Session, 
        *, 
        user_id: UUID, 
        avatar_id: UUID
    ) -> Optional[UserAvatar]:
        """
        Establece un avatar como activo para el usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            avatar_id: ID del avatar a activar
            
        Returns:
            UserAvatar activado o None si no existe o no pertenece al usuario
        """
        # Verificar que el avatar pertenezca al usuario
        avatar = (
            db.query(UserAvatar)
            .filter(
                and_(
                    UserAvatar.id == avatar_id,
                    UserAvatar.user_id == user_id
                )
            )
            .first()
        )
        
        if not avatar:
            return None
        
        # Desactivar otros avatars del usuario
        self._deactivate_other_avatars(db, user_id=user_id, exclude_id=avatar_id)
        
        # Activar el avatar seleccionado
        return self.update(db, db_obj=avatar, obj_in={"is_active": True})

    def update_avatar_privacy(
        self, 
        db: Session, 
        *, 
        user_id: UUID, 
        avatar_id: UUID, 
        is_public: bool
    ) -> Optional[UserAvatar]:
        """
        Actualiza la privacidad de un avatar.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            avatar_id: ID del avatar
            is_public: True para público, False para privado
            
        Returns:
            UserAvatar actualizado o None si no existe o no pertenece al usuario
        """
        avatar = (
            db.query(UserAvatar)
            .filter(
                and_(
                    UserAvatar.id == avatar_id,
                    UserAvatar.user_id == user_id
                )
            )
            .first()
        )
        
        if avatar:
            return self.update(db, db_obj=avatar, obj_in={"is_public": is_public})
        return None

    def delete_user_avatar(
        self, 
        db: Session, 
        *, 
        user_id: UUID, 
        avatar_id: UUID
    ) -> Optional[UserAvatar]:
        """
        Elimina un avatar del usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            avatar_id: ID del avatar a eliminar
            
        Returns:
            UserAvatar eliminado o None si no existe o no pertenece al usuario
        """
        avatar = (
            db.query(UserAvatar)
            .filter(
                and_(
                    UserAvatar.id == avatar_id,
                    UserAvatar.user_id == user_id
                )
            )
            .first()
        )
        
        if avatar:
            db.delete(avatar)
            db.commit()
            return avatar
        return None

    def search_avatars(
        self, 
        db: Session, 
        *, 
        search_term: str,
        user_id: Optional[UUID] = None,
        public_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserAvatar]:
        """
        Busca avatars por nombre.
        
        Args:
            db: Sesión de base de datos
            search_term: Término para buscar en el nombre
            user_id: ID del usuario para filtrar (opcional)
            public_only: Si incluir solo avatars públicos
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de UserAvatar que coinciden
        """
        query = db.query(UserAvatar).filter(
            UserAvatar.name.ilike(f"%{search_term}%")
        )
        
        if user_id:
            query = query.filter(UserAvatar.user_id == user_id)
        
        if public_only:
            query = query.filter(UserAvatar.is_public == True)
        
        return (
            query
            .order_by(desc(UserAvatar.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_popular_avatars(
        self, 
        db: Session, 
        *, 
        skip: int = 0,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtiene avatars populares (más duplicados por hash).
        
        Args:
            db: Sesión de base de datos
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de dict con información de avatars populares
        """
        # Query para contar avatars por hash de capas
        from sqlalchemy import func
        
        popular_hashes = (
            db.query(
                UserAvatar.layers_hash,
                func.count(UserAvatar.id).label('count'),
                func.max(UserAvatar.created_at).label('latest_created')
            )
            .filter(UserAvatar.is_public == True)
            .group_by(UserAvatar.layers_hash)
            .having(func.count(UserAvatar.id) > 1)
            .order_by(desc('count'), desc('latest_created'))
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        result = []
        for hash_info in popular_hashes:
            # Obtener un avatar ejemplo de este hash
            example_avatar = (
                db.query(UserAvatar)
                .filter(
                    and_(
                        UserAvatar.layers_hash == hash_info.layers_hash,
                        UserAvatar.is_public == True
                    )
                )
                .first()
            )
            
            if example_avatar:
                result.append({
                    'avatar': example_avatar,
                    'usage_count': hash_info.count,
                    'layers_hash': hash_info.layers_hash
                })
        
        return result

    def get_user_stats(self, db: Session, *, user_id: UUID) -> Dict[str, Any]:
        """
        Obtiene estadísticas de avatars de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Dict con estadísticas del usuario
        """
        total_avatars = (
            db.query(UserAvatar)
            .filter(UserAvatar.user_id == user_id)
            .count()
        )
        
        public_avatars = (
            db.query(UserAvatar)
            .filter(
                and_(
                    UserAvatar.user_id == user_id,
                    UserAvatar.is_public == True
                )
            )
            .count()
        )
        
        active_avatar = self.get_active_avatar(db, user_id=user_id)
        
        return {
            'total_avatars': total_avatars,
            'public_avatars': public_avatars,
            'private_avatars': total_avatars - public_avatars,
            'has_active_avatar': active_avatar is not None,
            'active_avatar_id': active_avatar.id if active_avatar else None
        }

    def _deactivate_other_avatars(self, db: Session, *, user_id: UUID, exclude_id: UUID):
        """
        Desactiva todos los avatars de un usuario excepto el especificado.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            exclude_id: ID del avatar a excluir de la desactivación
        """
        db.query(UserAvatar).filter(
            and_(
                UserAvatar.user_id == user_id,
                UserAvatar.id != exclude_id,
                UserAvatar.is_active == True
            )
        ).update({"is_active": False})
        db.commit()


# Instancia del CRUD
crud_user_avatar = CRUDUserAvatar(UserAvatar)