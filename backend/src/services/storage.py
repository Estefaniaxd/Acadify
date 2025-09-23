"""
Servicio de almacenamiento para avatares.
Abstrae el almacenamiento local vs S3/cloud.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple, Union
from abc import ABC, abstractmethod
from uuid import UUID

from src.core.config import settings


class StorageBackend(ABC):
    """Interfaz abstracta para backends de almacenamiento."""
    
    @abstractmethod
    async def save_file(
        self, 
        file_content: bytes, 
        destination_path: str
    ) -> str:
        """
        Guarda un archivo y retorna la URL pública.
        
        Args:
            file_content: Contenido del archivo en bytes
            destination_path: Ruta relativa donde guardar
            
        Returns:
            URL pública del archivo guardado
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """
        Elimina un archivo.
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    def get_public_url(self, file_path: str) -> str:
        """
        Obtiene la URL pública de un archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            URL pública
        """
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            True si existe
        """
        pass


class LocalStorageBackend(StorageBackend):
    """Backend de almacenamiento local."""
    
    def __init__(self, base_path: str = "static", base_url: str = "/static"):
        """
        Inicializa el backend local.
        
        Args:
            base_path: Directorio base para almacenamiento
            base_url: URL base para acceso público
        """
        self.base_path = Path(base_path).resolve()
        self.base_url = base_url.rstrip('/')
        
        # Crear directorio base si no existe
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(
        self, 
        file_content: bytes, 
        destination_path: str
    ) -> str:
        """Guarda archivo en sistema de archivos local."""
        full_path = self.base_path / destination_path
        
        # Crear directorios padre si no existen
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Escribir archivo
        with open(full_path, 'wb') as f:
            f.write(file_content)
        
        return self.get_public_url(destination_path)
    
    async def delete_file(self, file_path: str) -> bool:
        """Elimina archivo del sistema de archivos local."""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_public_url(self, file_path: str) -> str:
        """Genera URL pública para archivo local."""
        return f"{self.base_url}/{file_path.lstrip('/')}"
    
    def file_exists(self, file_path: str) -> bool:
        """Verifica si archivo existe localmente."""
        full_path = self.base_path / file_path
        return full_path.exists()
    
    def get_full_path(self, file_path: str) -> Path:
        """Obtiene la ruta completa de un archivo."""
        return self.base_path / file_path


class S3StorageBackend(StorageBackend):
    """Backend de almacenamiento S3 (para futuro uso)."""
    
    def __init__(
        self, 
        bucket_name: str,
        aws_region: str = "us-east-1",
        base_url: Optional[str] = None
    ):
        """
        Inicializa el backend S3.
        
        Args:
            bucket_name: Nombre del bucket S3
            aws_region: Región AWS
            base_url: URL base personalizada (opcional)
        """
        self.bucket_name = bucket_name
        self.aws_region = aws_region
        self.base_url = base_url or f"https://{bucket_name}.s3.{aws_region}.amazonaws.com"
        
        # TODO: Inicializar cliente boto3 cuando se implemente
        raise NotImplementedError("S3 backend not implemented yet")
    
    async def save_file(self, file_content: bytes, destination_path: str) -> str:
        # TODO: Implementar subida a S3
        raise NotImplementedError("S3 upload not implemented yet")
    
    async def delete_file(self, file_path: str) -> bool:
        # TODO: Implementar eliminación de S3
        raise NotImplementedError("S3 delete not implemented yet")
    
    def get_public_url(self, file_path: str) -> str:
        return f"{self.base_url}/{file_path.lstrip('/')}"
    
    def file_exists(self, file_path: str) -> bool:
        # TODO: Implementar verificación en S3
        raise NotImplementedError("S3 exists check not implemented yet")


class StorageService:
    """
    Servicio principal de almacenamiento.
    Delega al backend configurado (local o S3).
    """
    
    def __init__(self):
        """Inicializa el servicio con el backend configurado."""
        self.backend = self._create_backend()
    
    def _create_backend(self) -> StorageBackend:
        """Crea el backend según la configuración."""
        storage_type = getattr(settings, 'AVATAR_STORAGE_TYPE', 'local')
        
        if storage_type == 'local':
            base_path = getattr(settings, 'AVATAR_STORAGE_PATH', 'static')
            base_url = getattr(settings, 'AVATAR_ASSETS_BASE_URL', '/static').replace('/assets', '')
            return LocalStorageBackend(base_path, base_url)
        
        elif storage_type == 's3':
            bucket = getattr(settings, 'AWS_S3_BUCKET', None)
            region = getattr(settings, 'AWS_REGION', 'us-east-1')
            if not bucket:
                raise ValueError("AWS_S3_BUCKET must be set for S3 storage")
            return S3StorageBackend(bucket, region)
        
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    async def save_avatar_image(
        self, 
        image_bytes: bytes,
        user_id: UUID,
        filename: str
    ) -> str:
        """
        Guarda imagen de avatar.
        
        Args:
            image_bytes: Contenido de la imagen
            user_id: ID del usuario propietario
            filename: Nombre del archivo
            
        Returns:
            URL pública de la imagen
        """
        destination_path = f"avatars/{user_id}/{filename}"
        return await self.backend.save_file(image_bytes, destination_path)
    
    async def save_preview_image(
        self, 
        image_bytes: bytes,
        filename: str
    ) -> str:
        """
        Guarda imagen de preview temporal.
        
        Args:
            image_bytes: Contenido de la imagen
            filename: Nombre del archivo
            
        Returns:
            URL pública de la imagen
        """
        destination_path = f"avatars/temp/{filename}"
        return await self.backend.save_file(image_bytes, destination_path)
    
    async def delete_avatar_image(self, user_id: UUID, filename: str) -> bool:
        """
        Elimina imagen de avatar.
        
        Args:
            user_id: ID del usuario propietario
            filename: Nombre del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        file_path = f"avatars/{user_id}/{filename}"
        return await self.backend.delete_file(file_path)
    
    async def delete_preview_image(self, filename: str) -> bool:
        """
        Elimina imagen de preview.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        file_path = f"avatars/temp/{filename}"
        return await self.backend.delete_file(file_path)
    
    def get_avatar_url(self, user_id: UUID, filename: str) -> str:
        """
        Obtiene URL de imagen de avatar.
        
        Args:
            user_id: ID del usuario propietario
            filename: Nombre del archivo
            
        Returns:
            URL pública
        """
        file_path = f"avatars/{user_id}/{filename}"
        return self.backend.get_public_url(file_path)
    
    def get_preview_url(self, filename: str) -> str:
        """
        Obtiene URL de imagen de preview.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            URL pública
        """
        file_path = f"avatars/temp/{filename}"
        return self.backend.get_public_url(file_path)
    
    def get_asset_url(self, asset_filename: str) -> str:
        """
        Obtiene URL de asset.
        
        Args:
            asset_filename: Nombre del archivo de asset
            
        Returns:
            URL pública
        """
        file_path = f"assets/{asset_filename}"
        return self.backend.get_public_url(file_path)
    
    def avatar_exists(self, user_id: UUID, filename: str) -> bool:
        """
        Verifica si existe imagen de avatar.
        
        Args:
            user_id: ID del usuario propietario
            filename: Nombre del archivo
            
        Returns:
            True si existe
        """
        file_path = f"avatars/{user_id}/{filename}"
        return self.backend.file_exists(file_path)
    
    def asset_exists(self, asset_filename: str) -> bool:
        """
        Verifica si existe asset.
        
        Args:
            asset_filename: Nombre del archivo de asset
            
        Returns:
            True si existe
        """
        file_path = f"assets/{asset_filename}"
        return self.backend.file_exists(file_path)
    
    async def cleanup_orphaned_files(self, user_id: UUID, active_filenames: list) -> int:
        """
        Limpia archivos huérfanos de un usuario.
        
        Args:
            user_id: ID del usuario
            active_filenames: Lista de nombres de archivos que deben mantenerse
            
        Returns:
            Número de archivos eliminados
        """
        if not isinstance(self.backend, LocalStorageBackend):
            # Solo implementado para almacenamiento local
            return 0
        
        user_avatar_dir = self.backend.get_full_path(f"avatars/{user_id}")
        if not user_avatar_dir.exists():
            return 0
        
        deleted_count = 0
        for file_path in user_avatar_dir.glob("*.png"):
            if file_path.name not in active_filenames:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting orphaned file {file_path}: {e}")
        
        return deleted_count
    
    def get_storage_stats(self) -> dict:
        """
        Obtiene estadísticas de almacenamiento.
        
        Returns:
            Dict con estadísticas
        """
        if not isinstance(self.backend, LocalStorageBackend):
            return {"error": "Stats only available for local storage"}
        
        try:
            base_path = self.backend.base_path
            
            # Calcular tamaño total
            total_size = 0
            file_count = 0
            
            if base_path.exists():
                for file_path in base_path.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            # Calcular tamaños por categoría
            avatars_size = 0
            assets_size = 0
            temp_size = 0
            
            avatars_dir = base_path / "avatars"
            if avatars_dir.exists():
                for file_path in avatars_dir.rglob("*.png"):
                    size = file_path.stat().st_size
                    if "temp" in str(file_path):
                        temp_size += size
                    else:
                        avatars_size += size
            
            assets_dir = base_path / "assets"
            if assets_dir.exists():
                for file_path in assets_dir.rglob("*.png"):
                    assets_size += file_path.stat().st_size
            
            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_files": file_count,
                "avatars_size_mb": round(avatars_size / (1024 * 1024), 2),
                "assets_size_mb": round(assets_size / (1024 * 1024), 2),
                "temp_size_mb": round(temp_size / (1024 * 1024), 2),
                "backend_type": "local",
                "base_path": str(base_path)
            }
            
        except Exception as e:
            return {"error": f"Error getting storage stats: {e}"}


# Instancia global del servicio
storage_service = StorageService()