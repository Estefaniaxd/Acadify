# backend/app/services/file_service.py
"""
Servicio de archivos asíncrono y escalable para producción

Características:
- Subida de archivos de manera segura y asíncrona
- Validación de tamaño, tipo y extensiones peligrosas
- Nombres de archivo seguros y únicos
- Soporte para múltiples categorías y subcarpetas
- Estadísticas de almacenamiento
- Limpieza de archivos antiguos
- Validación de acceso por rol
"""

import uuid
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from uuid import UUID
import asyncio

import aiofiles
from fastapi import UploadFile, HTTPException

from ..core.config import settings
from ..core.logging import app_logger


class FileService:
    """Servicio de manejo de archivos asíncrono y seguro"""

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {
        'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'},
        'audio': {'.mp3', '.wav', '.m4a', '.ogg'},
        'video': {'.mp4', '.avi', '.mov', '.wmv', '.flv'},
        'spreadsheets': {'.xls', '.xlsx', '.csv'},
        'presentations': {'.ppt', '.pptx'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'}
    }
    DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.js'}

    # --------------------------
    # MÉTODOS INTERNOS
    # --------------------------
    @staticmethod
    def _get_file_category(filename: str) -> str:
        ext = Path(filename).suffix.lower()
        for category, extensions in FileService.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return category
        return 'other'

    @staticmethod
    def _validate_file(file: UploadFile, only_images=False) -> None:
        ext = Path(file.filename).suffix.lower()
        all_allowed = {e for exts in FileService.ALLOWED_EXTENSIONS.values() for e in exts}

        if ext not in all_allowed or (only_images and not file.content_type.startswith('image/')):
            raise HTTPException(status_code=400, detail=f"File type {ext} not allowed")

        if hasattr(file, 'spool_max_size') and file.spool_max_size > FileService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {FileService.MAX_FILE_SIZE // (1024*1024)}MB"
            )

        if ext in FileService.DANGEROUS_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Executable files are not allowed")

    @staticmethod
    def _generate_safe_filename(original_filename: str, user_id: UUID) -> str:
        ext = Path(original_filename).suffix.lower()
        safe_name = ''.join(
            c if c.isalnum() or c in '-_' else '_' for c in Path(original_filename).stem[:50]
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{user_id}_{timestamp}_{unique_id}_{safe_name}{ext}"

    @staticmethod
    async def _save_file(file: UploadFile, upload_dir: Path, filename: str) -> Path:
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        try:
            async with aiofiles.open(file_path, "wb") as out_file:
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)
            await file.close()
            return file_path
        except Exception as e:
            app_logger.error(f"Error saving file {filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # --------------------------
    # MÉTODOS PÚBLICOS
    # --------------------------
    async def upload_file(
        self,
        file: UploadFile,
        user_id: UUID,
        category: str,
        subfolder: Optional[str] = None
    ) -> str:
        """Subida genérica de archivo de manera segura y asíncrona"""
        self._validate_file(file, only_images=(category == 'images'))
        upload_dir = Path(settings.UPLOAD_DIR) / category
        if subfolder:
            upload_dir = upload_dir / subfolder

        safe_filename = self._generate_safe_filename(file.filename, user_id)
        await self._save_file(file, upload_dir, safe_filename)
        return f"/uploads/{category}/{subfolder + '/' if subfolder else ''}{safe_filename}"

    # Subidas específicas para cada tipo
    async def upload_assignment_file(self, file: UploadFile, student_id: UUID, assignment_id: UUID) -> str:
        return await self.upload_file(file, student_id, "assignments", str(assignment_id))

    async def upload_chat_file(self, file: UploadFile, user_id: UUID, group_chat_id: UUID) -> str:
        return await self.upload_file(file, user_id, "chat", str(group_chat_id))

    async def upload_profile_image(self, file: UploadFile, user_id: UUID) -> str:
        return await self.upload_file(file, user_id, "profiles")

    async def upload_material_file(self, file: UploadFile, uploader_id: UUID, course_id: Optional[UUID] = None) -> str:
        subfolder = str(course_id) if course_id else "general"
        return await self.upload_file(file, uploader_id, "materials", subfolder)

    async def upload_multiple_files(
        self, files: List[UploadFile], user_id: UUID, category: str, subfolder: Optional[str] = None
    ) -> List[str]:
        """Subida masiva de archivos en paralelo"""
        tasks = [self.upload_file(f, user_id, category, subfolder) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=False)

    def delete_file(self, file_url: str) -> bool:
        try:
            file_path = Path(settings.UPLOAD_DIR) / file_url.lstrip('/uploads/')
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            app_logger.error(f"Error deleting file {file_url}: {e}")
            return False

    def get_file_info(self, file_url: str) -> Optional[Dict]:
        try:
            file_path = Path(settings.UPLOAD_DIR) / file_url.lstrip('/uploads/')
            if not file_path.exists() or not file_path.is_file():
                return None
            stat = file_path.stat()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return {
                "filename": file_path.name,
                "size": stat.st_size,
                "mime_type": mime_type,
                "category": self._get_file_category(file_path.name),
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime)
            }
        except Exception as e:
            app_logger.error(f"Error getting file info for {file_url}: {e}")
            return None

    def cleanup_old_files(self, days_old: int = 30, temp_dirs=None) -> int:
        """Eliminar archivos antiguos de carpetas temporales"""
        temp_dirs = temp_dirs or ['temp', 'cache', 'tmp']
        cutoff = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        try:
            for file_path in Path(settings.UPLOAD_DIR).rglob('*'):
                if file_path.is_file() and any(d in str(file_path) for d in temp_dirs):
                    if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff:
                        file_path.unlink()
                        deleted_count += 1
        except Exception as e:
            app_logger.error(f"Error cleaning old files: {e}")
        return deleted_count

    def get_storage_stats(self) -> Dict:
        """Estadísticas de almacenamiento"""
        stats = {"total_size": 0, "total_files": 0, "categories": {}}
        try:
            for file_path in Path(settings.UPLOAD_DIR).rglob('*'):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    stats["total_size"] += size
                    stats["total_files"] += 1
                    category = self._get_file_category(file_path.name)
                    stats["categories"].setdefault(category, {"count": 0, "size": 0})
                    stats["categories"][category]["count"] += 1
                    stats["categories"][category]["size"] += size
        except Exception as e:
            app_logger.error(f"Error calculating storage stats: {e}")
        return stats

    def validate_file_access(self, file_url: str, user_id: UUID, user_role: str) -> bool:
        """Validar acceso a archivo según reglas de negocio"""
        try:
            parts = file_url.strip('/').split('/')
            if len(parts) < 3:
                return False
            file_type, filename = parts[1], parts[-1]

            if file_type == "profiles":
                return True
            if file_type == "assignments" and (user_role in ["administrator", "coordinator"] or filename.startswith(str(user_id))):
                return True
            if file_type == "chat" and (user_role in ["administrator", "coordinator"] or filename.startswith(str(user_id))):
                return True
            if file_type == "materials":
                return True
            return False
        except Exception as e:
            app_logger.error(f"Error validating file access {file_url}: {e}")
            return False
