"""
Módulo de almacenamiento abstracto para avatars.
Soporta almacenamiento local y S3 (configuración futura).
"""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path
from PIL import Image

from src.core.config import settings


class StorageBackend(ABC):
    """Interfaz abstracta para backends de almacenamiento."""
    
    @abstractmethod
    async def save_image(self, image: Image.Image, path: str) -> str:
        """
        Guarda una imagen y retorna la URL pública.
        
        Args:
            image: Imagen PIL a guardar
            path: Ruta relativa donde guardar
            
        Returns:
            URL pública de la imagen guardada
        """
        pass
    
    @abstractmethod
    async def delete_image(self, path: str) -> bool:
        """
        Elimina una imagen.
        
        Args:
            path: Ruta de la imagen a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            path: Ruta del archivo
            
        Returns:
            True si existe
        """
        pass
    
    @abstractmethod
    def get_public_url(self, path: str) -> str:
        """
        Obtiene la URL pública de un archivo.
        
        Args:
            path: Ruta del archivo
            
        Returns:
            URL pública
        """
        pass


class LocalStorageBackend(StorageBackend):
    """Backend de almacenamiento local."""
    
    def __init__(self, base_path: str = "static"):
        self.base_path = os.path.abspath(base_path)
        
    def _get_full_path(self, path: str) -> str:
        """Convierte ruta relativa a absoluta."""
        # Remover / inicial si existe
        if path.startswith('/'):
            path = path[1:]
        # Remover 'static/' del inicio si existe
        if path.startswith('static/'):
            path = path[7:]
        
        return os.path.join(self.base_path, path)
    
    async def save_image(self, image: Image.Image, path: str) -> str:
        """Guarda imagen localmente."""
        full_path = self._get_full_path(path)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Guardar imagen (operación sync en thread pool)
        await asyncio.get_event_loop().run_in_executor(
            None, 
            lambda: image.save(full_path, 'PNG', optimize=True)
        )
        
        return self.get_public_url(path)
    
    async def delete_image(self, path: str) -> bool:
        """Elimina imagen local."""
        full_path = self._get_full_path(path)
        
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except Exception as e:
            print(f"Error deleting local file {full_path}: {e}")
        
        return False
    
    def exists(self, path: str) -> bool:
        """Verifica si archivo existe localmente."""
        full_path = self._get_full_path(path)
        return os.path.exists(full_path)
    
    def get_public_url(self, path: str) -> str:
        """Obtiene URL pública local."""
        # Asegurar que empiece con /static/
        if not path.startswith('/static/'):
            if path.startswith('static/'):
                path = '/' + path
            else:
                path = '/static/' + path
        
        return path


class S3StorageBackend(StorageBackend):
    """
    Backend de almacenamiento S3.
    TODO: Implementar cuando se necesite deployment en producción.
    """
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.region = region
        # TODO: Configurar boto3 client
        raise NotImplementedError("S3 backend not implemented yet")
    
    async def save_image(self, image: Image.Image, path: str) -> str:
        # TODO: Implementar upload a S3
        raise NotImplementedError("S3 backend not implemented yet")
    
    async def delete_image(self, path: str) -> bool:
        # TODO: Implementar delete de S3
        raise NotImplementedError("S3 backend not implemented yet")
    
    def exists(self, path: str) -> bool:
        # TODO: Implementar check de existencia en S3
        raise NotImplementedError("S3 backend not implemented yet")
    
    def get_public_url(self, path: str) -> str:
        # TODO: Implementar URL pública de S3
        raise NotImplementedError("S3 backend not implemented yet")


class StorageManager:
    """
    Manager principal para operaciones de almacenamiento.
    Permite cambiar entre backends según configuración.
    """
    
    def __init__(self):
        self._backend: Optional[StorageBackend] = None
        self._setup_backend()
    
    def _setup_backend(self):
        """Configura el backend según la configuración."""
        # Por ahora solo local, en el futuro leer de settings
        storage_type = getattr(settings, 'AVATAR_STORAGE_TYPE', 'local')
        
        if storage_type == 'local':
            base_path = getattr(settings, 'AVATAR_STORAGE_PATH', 'static')
            self._backend = LocalStorageBackend(base_path)
        elif storage_type == 's3':
            # TODO: Configurar S3 cuando se implemente
            bucket = getattr(settings, 'AVATAR_S3_BUCKET', None)
            region = getattr(settings, 'AVATAR_S3_REGION', 'us-east-1')
            if bucket:
                self._backend = S3StorageBackend(bucket, region)
            else:
                # Fallback a local
                print("Warning: S3 bucket not configured, using local storage")
                self._backend = LocalStorageBackend()
        else:
            # Fallback a local
            print(f"Warning: Unknown storage type '{storage_type}', using local storage")
            self._backend = LocalStorageBackend()
    
    @property
    def backend(self) -> StorageBackend:
        """Obtiene el backend actual."""
        if not self._backend:
            self._setup_backend()
        return self._backend
    
    async def save_avatar_image(
        self, 
        image: Image.Image, 
        user_id: str, 
        filename: str
    ) -> str:
        """
        Guarda imagen de avatar en el almacenamiento.
        
        Args:
            image: Imagen PIL a guardar
            user_id: ID del usuario
            filename: Nombre del archivo (ej: "hash123.png")
            
        Returns:
            URL pública de la imagen
        """
        path = f"avatars/{user_id}/{filename}"
        return await self.backend.save_image(image, path)
    
    async def save_preview_image(
        self, 
        image: Image.Image, 
        filename: str
    ) -> str:
        """
        Guarda imagen de preview temporal.
        
        Args:
            image: Imagen PIL a guardar
            filename: Nombre del archivo (ej: "preview_hash123.png")
            
        Returns:
            URL pública de la imagen
        """
        path = f"avatars/temp/{filename}"
        return await self.backend.save_image(image, path)
    
    async def delete_avatar_image(self, user_id: str, filename: str) -> bool:
        """
        Elimina imagen de avatar.
        
        Args:
            user_id: ID del usuario
            filename: Nombre del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        path = f"avatars/{user_id}/{filename}"
        return await self.backend.delete_image(path)
    
    async def delete_preview_image(self, filename: str) -> bool:
        """
        Elimina imagen de preview.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si se eliminó correctamente
        """
        path = f"avatars/temp/{filename}"
        return await self.backend.delete_image(path)
    
    def avatar_exists(self, user_id: str, filename: str) -> bool:
        """
        Verifica si imagen de avatar existe.
        
        Args:
            user_id: ID del usuario
            filename: Nombre del archivo
            
        Returns:
            True si existe
        """
        path = f"avatars/{user_id}/{filename}"
        return self.backend.exists(path)
    
    def get_avatar_url(self, user_id: str, filename: str) -> str:
        """
        Obtiene URL pública de avatar.
        
        Args:
            user_id: ID del usuario
            filename: Nombre del archivo
            
        Returns:
            URL pública
        """
        path = f"avatars/{user_id}/{filename}"
        return self.backend.get_public_url(path)
    
    def get_backend_type(self) -> str:
        """Obtiene el tipo de backend actual."""
        if isinstance(self._backend, LocalStorageBackend):
            return "local"
        elif isinstance(self._backend, S3StorageBackend):
            return "s3"
        else:
            return "unknown"
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Obtiene información del almacenamiento actual.
        
        Returns:
            Dict con información del backend
        """
        backend_type = self.get_backend_type()
        
        info = {
            "type": backend_type,
            "backend_class": self._backend.__class__.__name__
        }
        
        if backend_type == "local":
            info["base_path"] = self._backend.base_path
        elif backend_type == "s3":
            info["bucket"] = self._backend.bucket_name
            info["region"] = self._backend.region
        
        return info


# Instancia global del manager
storage_manager = StorageManager()