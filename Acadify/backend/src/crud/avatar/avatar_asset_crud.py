"""
CRUD para avatar assets.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.crud.base import CRUDBase
from src.models.avatar.avatar_asset import AvatarAsset


class CRUDAvatarAsset(CRUDBase[AvatarAsset, Dict[str, Any], Dict[str, Any]]):
    """CRUD operations para AvatarAsset."""

    def get_by_filename(self, db: Session, *, filename: str) -> Optional[AvatarAsset]:
        """
        Obtiene un asset por su filename.
        
        Args:
            db: Sesión de base de datos
            filename: Nombre del archivo (ej: hair/short_black.png)
            
        Returns:
            AvatarAsset o None si no existe
        """
        return db.query(AvatarAsset).filter(AvatarAsset.filename == filename).first()

    def get_by_category(
        self, 
        db: Session, 
        *, 
        category: str,
        gender: Optional[str] = None,
        active_only: bool = True,
        skip: int = 0, 
        limit: int = 100
    ) -> List[AvatarAsset]:
        """
        Obtiene assets por categoría.
        
        Args:
            db: Sesión de base de datos
            category: Categoría de assets (hair, eyes, etc.)
            gender: Filtrar por género (male, female, unisex o None para todos)
            active_only: Si incluir solo assets activos
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de AvatarAsset
        """
        query = db.query(AvatarAsset).filter(AvatarAsset.category == category)
        
        if active_only:
            query = query.filter(AvatarAsset.is_active == 'Y')
            
        if gender:
            # Incluir assets específicos del género Y unisex
            query = query.filter(
                or_(
                    AvatarAsset.target_gender == gender,
                    AvatarAsset.target_gender == 'unisex'
                )
            )
        
        return query.offset(skip).limit(limit).all()

    def get_all_categories(self, db: Session, *, active_only: bool = True) -> List[str]:
        """
        Obtiene todas las categorías disponibles.
        
        Args:
            db: Sesión de base de datos
            active_only: Si incluir solo assets activos
            
        Returns:
            Lista de nombres de categorías únicas
        """
        query = db.query(AvatarAsset.category).distinct()
        
        if active_only:
            query = query.filter(AvatarAsset.is_active == 'Y')
        
        return [row[0] for row in query.all()]

    def get_assets_by_categories(
        self, 
        db: Session, 
        *, 
        categories: List[str],
        active_only: bool = True
    ) -> Dict[str, List[AvatarAsset]]:
        """
        Obtiene assets agrupados por categorías.
        
        Args:
            db: Sesión de base de datos
            categories: Lista de categorías a buscar
            active_only: Si incluir solo assets activos
            
        Returns:
            Dict con categoría como key y lista de assets como value
        """
        query = db.query(AvatarAsset).filter(AvatarAsset.category.in_(categories))
        
        if active_only:
            query = query.filter(AvatarAsset.is_active == 'Y')
        
        assets = query.all()
        
        # Agrupar por categoría
        result = {category: [] for category in categories}
        for asset in assets:
            if asset.category in result:
                result[asset.category].append(asset)
        
        return result

    def create_asset(
        self, 
        db: Session, 
        *, 
        category: str,
        filename: str,
        display_name: Optional[str] = None,
        file_size: int,
        width: int,
        height: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AvatarAsset:
        """
        Crea un nuevo asset.
        
        Args:
            db: Sesión de base de datos
            category: Categoría del asset
            filename: Nombre del archivo
            display_name: Nombre para mostrar (opcional)
            file_size: Tamaño en bytes
            width: Ancho en píxeles
            height: Alto en píxeles
            metadata: Metadatos adicionales
            
        Returns:
            AvatarAsset creado
        """
        asset_data = {
            "category": category,
            "filename": filename,
            "display_name": display_name,
            "file_size": file_size,
            "width": width,
            "height": height,
            "metadata": metadata or {}
        }
        
        return self.create(db, obj_in=asset_data)

    def update_asset_status(
        self, 
        db: Session, 
        *, 
        asset_id: str, 
        is_active: bool
    ) -> Optional[AvatarAsset]:
        """
        Actualiza el estado activo de un asset.
        
        Args:
            db: Sesión de base de datos
            asset_id: ID del asset
            is_active: True para activar, False para desactivar
            
        Returns:
            AvatarAsset actualizado o None si no existe
        """
        asset = self.get(db, id=asset_id)
        if asset:
            status = 'Y' if is_active else 'N'
            return self.update(db, db_obj=asset, obj_in={"is_active": status})
        return None

    def search_assets(
        self, 
        db: Session, 
        *, 
        search_term: str,
        categories: Optional[List[str]] = None,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[AvatarAsset]:
        """
        Busca assets por término de búsqueda.
        
        Args:
            db: Sesión de base de datos
            search_term: Término para buscar en filename y display_name
            categories: Lista de categorías para filtrar (opcional)
            active_only: Si incluir solo assets activos
            skip: Offset para paginación
            limit: Límite de resultados
            
        Returns:
            Lista de AvatarAsset que coinciden
        """
        query = db.query(AvatarAsset)
        
        # Filtro de búsqueda
        search_filter = or_(
            AvatarAsset.filename.ilike(f"%{search_term}%"),
            AvatarAsset.display_name.ilike(f"%{search_term}%")
        )
        query = query.filter(search_filter)
        
        # Filtro de categorías
        if categories:
            query = query.filter(AvatarAsset.category.in_(categories))
        
        # Filtro de activos
        if active_only:
            query = query.filter(AvatarAsset.is_active == 'Y')
        
        return query.offset(skip).limit(limit).all()

    def validate_assets_exist(
        self, 
        db: Session, 
        *, 
        asset_files: List[str]
    ) -> Dict[str, bool]:
        """
        Valida que una lista de archivos de assets existan.
        
        Args:
            db: Sesión de base de datos
            asset_files: Lista de filenames a validar
            
        Returns:
            Dict con filename como key y bool indicando si existe
        """
        existing_assets = db.query(AvatarAsset.filename).filter(
            and_(
                AvatarAsset.filename.in_(asset_files),
                AvatarAsset.is_active == 'Y'
            )
        ).all()
        
        existing_filenames = {asset[0] for asset in existing_assets}
        
        return {
            filename: filename in existing_filenames 
            for filename in asset_files
        }

    def get_stats(self, db: Session) -> Dict[str, Any]:
        """
        Obtiene estadísticas de assets.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Dict con estadísticas: total, por categoría, activos, etc.
        """
        total_assets = db.query(AvatarAsset).count()
        active_assets = db.query(AvatarAsset).filter(AvatarAsset.is_active == 'Y').count()
        
        # Assets por categoría
        category_stats = {}
        categories = self.get_all_categories(db, active_only=False)
        for category in categories:
            total_cat = db.query(AvatarAsset).filter(AvatarAsset.category == category).count()
            active_cat = db.query(AvatarAsset).filter(
                and_(
                    AvatarAsset.category == category,
                    AvatarAsset.is_active == 'Y'
                )
            ).count()
            category_stats[category] = {
                "total": total_cat,
                "active": active_cat
            }
        
        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "inactive_assets": total_assets - active_assets,
            "total_categories": len(categories),
            "category_stats": category_stats
        }

    def get_base_assets(self, db: Session) -> Dict[str, AvatarAsset]:
        """
        Obtiene los assets base (male_base.png y female_base.png).
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Dict con keys 'male' y 'female' apuntando a sus assets base
        """
        base_assets = db.query(AvatarAsset).filter(
            and_(
                AvatarAsset.category == 'base',
                AvatarAsset.is_active == 'Y'
            )
        ).all()
        
        result = {}
        for asset in base_assets:
            if 'male' in asset.filename.lower() and 'female' not in asset.filename.lower():
                result['male'] = asset
            elif 'female' in asset.filename.lower():
                result['female'] = asset
                
        return result


# Instancia del CRUD
crud_avatar_asset = CRUDAvatarAsset(AvatarAsset)