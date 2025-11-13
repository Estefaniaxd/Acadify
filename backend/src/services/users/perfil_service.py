"""Servicio para gestión de personalización de perfil (foto, banner, marco)."""

from datetime import UTC, datetime
import hashlib
import io
from typing import Any
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.storage import storage_manager
from src.models.gamification.inventario_usuario import InventarioUsuario
from src.models.gamification.tienda_item import TiendaItem
from src.models.users.usuario import Usuario
from src.schemas.users.perfil_schemas import PerfilPersonalizacionResponse


class PerfilService:
    """Servicio para gestionar personalización de perfil."""

    # Configuración de imágenes
    MAX_PHOTO_SIZE_MB = 5
    MAX_BANNER_SIZE_MB = 10
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
    PHOTO_MAX_WIDTH = 800
    PHOTO_MAX_HEIGHT = 800
    BANNER_MAX_WIDTH = 1920
    BANNER_MAX_HEIGHT = 400

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_usuario(self, usuario_id: UUID) -> Usuario:
        """Obtiene usuario o lanza excepción."""
        result = await self.db.execute(
            select(Usuario).where(Usuario.usuario_id == usuario_id)
        )
        usuario = result.scalar_one_or_none()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        return usuario

    def _validate_image(self, file: UploadFile, max_size_mb: int) -> None:
        """Valida imagen subida."""
        # Validar extensión
        filename = file.filename or ""
        ext = filename[filename.rfind(".") :].lower() if "." in filename else ""

        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato no permitido. Use: {', '.join(self.ALLOWED_EXTENSIONS)}",
            )

        # Validar tamaño
        if file.size and file.size > max_size_mb * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Imagen muy grande. Máximo {max_size_mb}MB",
            )

    async def _process_image(
        self, file: UploadFile, max_width: int, max_height: int
    ) -> Image.Image:
        """Procesa y optimiza imagen."""
        try:
            # Leer contenido
            contents = await file.read()
            image = Image.open(io.BytesIO(contents))

            # Convertir a RGB si es necesario
            if image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                if image.mode == "P":
                    image = image.convert("RGBA")
                background.paste(
                    image, mask=image.split()[-1] if "A" in image.mode else None
                )
                image = background
            elif image.mode != "RGB":
                image = image.convert("RGB")

            # Redimensionar si es necesario
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            return image

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error procesando imagen: {e!s}",
            ) from e

    def _generate_filename(self, usuario_id: UUID, prefix: str) -> str:
        """Genera nombre único para archivo."""
        timestamp = datetime.now(UTC).isoformat()
        hash_str = hashlib.md5(f"{usuario_id}{timestamp}".encode()).hexdigest()[:10]
        return f"{prefix}_{hash_str}.jpg"

    async def upload_foto_perfil(self, usuario_id: UUID, file: UploadFile) -> str:
        """Sube una foto de perfil custom.

        Args:
            usuario_id: ID del usuario
            file: Archivo de imagen

        Returns:
            URL de la foto subida
        """
        # Validar
        self._validate_image(file, self.MAX_PHOTO_SIZE_MB)

        # Obtener usuario
        usuario = await self._get_usuario(usuario_id)

        # Procesar imagen
        image = await self._process_image(
            file, self.PHOTO_MAX_WIDTH, self.PHOTO_MAX_HEIGHT
        )

        # Generar nombre
        filename = self._generate_filename(usuario_id, "profile")

        # Guardar
        url = await storage_manager.save_profile_photo(image, str(usuario_id), filename)

        # Actualizar usuario
        usuario.foto_perfil_custom_url = url
        usuario.usa_foto_custom = True

        await self.db.commit()

        return url

    async def upload_banner(self, usuario_id: UUID, file: UploadFile) -> str:
        """Sube un banner/portada custom.

        Args:
            usuario_id: ID del usuario
            file: Archivo de imagen

        Returns:
            URL del banner subido
        """
        # Validar
        self._validate_image(file, self.MAX_BANNER_SIZE_MB)

        # Obtener usuario
        usuario = await self._get_usuario(usuario_id)

        # Procesar imagen
        image = await self._process_image(
            file, self.BANNER_MAX_WIDTH, self.BANNER_MAX_HEIGHT
        )

        # Generar nombre
        filename = self._generate_filename(usuario_id, "banner")

        # Guardar
        url = await storage_manager.save_banner(image, str(usuario_id), filename)

        # Actualizar usuario
        usuario.banner_url = url

        await self.db.commit()

        return url

    async def cambiar_a_avatar(self, usuario_id: UUID) -> dict[str, Any]:
        """Cambia de foto custom a avatar.

        Args:
            usuario_id: ID del usuario

        Returns:
            Confirmación del cambio
        """
        usuario = await self._get_usuario(usuario_id)

        usuario.usa_foto_custom = False
        await self.db.commit()

        return {
            "success": True,
            "message": "Cambiado a avatar",
            "usa_foto_custom": False,
        }

    async def cambiar_a_foto_custom(self, usuario_id: UUID) -> dict[str, Any]:
        """Cambia de avatar a foto custom.

        Args:
            usuario_id: ID del usuario

        Returns:
            Confirmación del cambio
        """
        usuario = await self._get_usuario(usuario_id)

        if not usuario.foto_perfil_custom_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No has subido una foto de perfil aún",
            )

        usuario.usa_foto_custom = True
        await self.db.commit()

        return {
            "success": True,
            "message": "Cambiado a foto custom",
            "usa_foto_custom": True,
        }

    async def equipar_banner_tienda(
        self, usuario_id: UUID, banner_id: UUID | None
    ) -> dict[str, Any]:
        """Equipa un banner comprado en la tienda.

        Args:
            usuario_id: ID del usuario
            banner_id: ID del item de banner (None para quitar)

        Returns:
            Confirmación
        """
        usuario = await self._get_usuario(usuario_id)

        if banner_id is None:
            # Quitar banner
            usuario.banner_activo_id = None
            await self.db.commit()
            return {
                "success": True,
                "message": "Banner removido",
                "banner_activo_id": None,
            }

        # Verificar que el item existe y es un banner
        result = await self.db.execute(
            select(TiendaItem).where(TiendaItem.id == banner_id)
        )
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado"
            )

        from src.enums.gamification.tienda_enums import CategoriaItem

        if item.categoria != CategoriaItem.fondo_perfil:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El item no es un banner",
            )

        # Verificar que el usuario lo tiene en inventario
        result = await self.db.execute(
            select(InventarioUsuario).where(
                InventarioUsuario.usuario_id == usuario_id,
                InventarioUsuario.item_id == banner_id,
            )
        )
        inventario = result.scalar_one_or_none()

        if not inventario or inventario.cantidad < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes este item en tu inventario",
            )

        # Equipar
        usuario.banner_activo_id = banner_id
        await self.db.commit()

        return {
            "success": True,
            "message": f"Banner '{item.nombre}' equipado",
            "banner_activo_id": banner_id,
        }

    async def equipar_marco_perfil(
        self, usuario_id: UUID, marco_id: UUID | None
    ) -> dict[str, Any]:
        """Equipa un marco de perfil comprado en la tienda.

        Args:
            usuario_id: ID del usuario
            marco_id: ID del item de marco (None para quitar)

        Returns:
            Confirmación
        """
        usuario = await self._get_usuario(usuario_id)

        if marco_id is None:
            # Quitar marco
            usuario.marco_perfil_id = None
            await self.db.commit()
            return {
                "success": True,
                "message": "Marco removido",
                "marco_perfil_id": None,
            }

        # Verificar que el item existe y es un marco
        result = await self.db.execute(
            select(TiendaItem).where(TiendaItem.id == marco_id)
        )
        item = result.scalar_one_or_none()

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item no encontrado"
            )

        from src.enums.gamification.tienda_enums import CategoriaItem

        if item.categoria != CategoriaItem.marco_avatar:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="El item no es un marco"
            )

        # Verificar que el usuario lo tiene en inventario
        result = await self.db.execute(
            select(InventarioUsuario).where(
                InventarioUsuario.usuario_id == usuario_id,
                InventarioUsuario.item_id == marco_id,
            )
        )
        inventario = result.scalar_one_or_none()

        if not inventario or inventario.cantidad < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No tienes este item en tu inventario",
            )

        # Equipar
        usuario.marco_perfil_id = marco_id
        await self.db.commit()

        return {
            "success": True,
            "message": f"Marco '{item.nombre}' equipado",
            "marco_perfil_id": marco_id,
        }

    async def obtener_personalizacion(
        self, usuario_id: UUID
    ) -> PerfilPersonalizacionResponse:
        """Obtiene toda la personalización del perfil del usuario.

        Args:
            usuario_id: ID del usuario

        Returns:
            Datos de personalización completos
        """
        # Obtener usuario con relaciones
        result = await self.db.execute(
            select(Usuario).where(Usuario.usuario_id == usuario_id)
        )
        usuario = result.scalar_one_or_none()

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        # Construir respuesta
        response_data = {
            "usuario_id": usuario.usuario_id,
            "usa_foto_custom": usuario.usa_foto_custom,
            "foto_perfil_custom_url": usuario.foto_perfil_custom_url,
            "avatar_url": None,  # TODO: Generar desde avatar system
            "banner_url": usuario.banner_url,
            "banner_activo_id": usuario.banner_activo_id,
            "banner_activo_nombre": None,
            "banner_activo_preview": None,
            "marco_perfil_id": usuario.marco_perfil_id,
            "marco_perfil_nombre": None,
            "marco_perfil_preview": None,
        }

        # Cargar info del banner si existe
        if usuario.banner_activo_id:
            result = await self.db.execute(
                select(TiendaItem).where(TiendaItem.id == usuario.banner_activo_id)
            )
            banner_item = result.scalar_one_or_none()
            if banner_item:
                response_data["banner_activo_nombre"] = banner_item.nombre
                response_data["banner_activo_preview"] = banner_item.imagen_preview

        # Cargar info del marco si existe
        if usuario.marco_perfil_id:
            result = await self.db.execute(
                select(TiendaItem).where(TiendaItem.id == usuario.marco_perfil_id)
            )
            marco_item = result.scalar_one_or_none()
            if marco_item:
                response_data["marco_perfil_nombre"] = marco_item.nombre
                response_data["marco_perfil_preview"] = marco_item.imagen_preview

        return PerfilPersonalizacionResponse(**response_data)
