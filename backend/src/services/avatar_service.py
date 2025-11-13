"""Servicio para manejo de avatars: composición, cache y almacenamiento."""

import contextlib
import os
from typing import Any
from uuid import UUID

import redis
from sqlalchemy.orm import Session

from src.core.config import settings
from src.crud.avatar import crud_avatar_asset, crud_user_avatar
from src.models.avatar.user_avatar import UserAvatar
from src.utils.image_utils import (
    STANDARD_RESOLUTION,
    compose_images,
    layers_hash,
    save_normalized_image,
    validate_layers,
)


# Orden de composición de capas del avatar
# PIL compone de primera a última capa: primera capa = FONDO (atrás), última capa = FRENTE (adelante)
# Valores menores = se pintan primero (quedan ATRÁS/ABAJO)
# Valores mayores = se pintan después (quedan ADELANTE/ENCIMA)
LAYER_ORDER = {
    "backgrounds": 0,  # Fondo (primera capa, muy atrás)
    "base": 1,  # Base del cuerpo (sobre fondo)
    "shoes": 2,  # Zapatos (PRIMERO, quedan DEBAJO de todo)
    "socks": 3,  # Medias (sobre zapatos)
    "pants": 4,  # Pantalones (sobre zapatos/medias, DEBAJO de camisa)
    "skirt": 5,  # Faldas (sobre zapatos/medias, DEBAJO de camisa)
    "shirt": 6,  # Camisas (ENCIMA de pantalones/faldas)
    # Chaquetas: queremos que se pinten POR ENCIMA del cabello en este proyecto
    # (por ejemplo, para chaquetas con capucha que cubren parte del pelo).
    # Asignamos prioridad mayor que 'hair' para que queden por delante.
    "jacket": 13,  # Chaquetas (ENCIMA de camisa y hair)
    "mouth": 8,  # Boca (rasgos faciales)
    "eyes": 9,  # Ojos (rasgos faciales)
    "makeup": 10,  # Maquillaje (sobre rasgos)
    "hair": 11,  # Cabello (cubre parte de la cara)
    "accessories": 14,  # Accesorios (última capa, MUY ADELANTE)
}


def sort_layers_by_priority(layers: list[dict[str, str]]) -> list[dict[str, str]]:
    """Ordena las capas según su prioridad visual correcta.

    Args:
        layers: Lista de capas con category y file

    Returns:
        Lista ordenada de capas (atrás → adelante)
    """

    def get_order(layer: dict[str, str]) -> int:
        category = layer.get("category", "")
        return LAYER_ORDER.get(category, 50)  # 50 para categorías desconocidas

    return sorted(layers, key=get_order)


class AvatarService:
    """Servicio principal para el sistema de avatars.
    Maneja composición, cache Redis y almacenamiento.
    """

    def __init__(self) -> None:
        """Inicializa el servicio con el backend configurado."""
        self.redis: redis.Redis | None = None
        # Usar las imágenes normalizadas que ahora están en assets/
        self.assets_dir = settings.AVATAR_ASSETS_PATH
        self.avatars_dir = os.path.join(settings.AVATAR_STORAGE_PATH, "avatars")
        self.cache_ttl = settings.AVATAR_COMPOSITION_CACHE_TTL
        self.preview_cache_ttl = settings.AVATAR_PREVIEW_CACHE_TTL

    def connect_redis(self) -> None:
        """Establece conexión con Redis."""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,  # Para manejar datos binarios
            )
            # Test connection
            self.redis.ping()
        except Exception:
            self.redis = None

    def disconnect_redis(self) -> None:
        """Cierra conexión con Redis."""
        if self.redis:
            self.redis.close()
            self.redis = None

    def _get_cache_key(self, layers_hash_str: str) -> str:
        """Genera clave de cache para composición de avatar."""
        return f"avatar_comp:{layers_hash_str}"

    def _get_preview_cache_key(self, layers_hash_str: str) -> str:
        """Genera clave de cache para preview de avatar."""
        return f"avatar_preview:{layers_hash_str}"

    async def get_manifest(self, db: Session) -> dict[str, Any]:
        """Obtiene el manifest de assets disponibles.

        Args:
            db: Sesión de base de datos

        Returns:
            Dict con categorías, archivos y metadatos
        """
        categories = crud_avatar_asset.get_all_categories(db, active_only=True)

        manifest = {
            "resolution": STANDARD_RESOLUTION,
            "categories": {},
            "total_assets": 0,
        }

        for category in categories:
            assets = crud_avatar_asset.get_by_category(
                db, category=category, active_only=True
            )
            asset_list = []

            for asset in assets:
                # Construir URL completa del asset con dominio
                asset_url = f"http://localhost:8000/static/assets/{asset.filename}"

                asset_info = {
                    "id": str(asset.id),
                    "filename": asset.filename,
                    "display_name": asset.display_name or asset.filename.split("/")[-1],
                    "width": asset.width,
                    "height": asset.height,
                    "file_size": asset.file_size,
                    "is_normalized": asset.is_normalized,
                    "meta_info": asset.meta_info or {},
                    "url": asset_url,  # URL completa con dominio
                }
                asset_list.append(asset_info)

            manifest["categories"][category] = asset_list
            manifest["total_assets"] += len(asset_list)

        return manifest

    async def get_manifest_for_gender(self, db: Session, gender: str) -> dict[str, Any]:
        """Obtiene el manifest de assets filtrado por género.

        Args:
            db: Sesión de base de datos
            gender: Género a filtrar (male o female)

        Returns:
            Dict con categorías, archivos y metadatos filtrados
        """
        categories = crud_avatar_asset.get_all_categories(db, active_only=True)

        manifest = {
            "resolution": STANDARD_RESOLUTION,
            "categories": {},
            "total_assets": 0,
            "gender": gender,
        }

        for category in categories:
            # Para la categoría base, filtrar específicamente por género
            if category == "base":
                assets = crud_avatar_asset.get_by_category(
                    db, category=category, gender=gender, active_only=True
                )
            else:
                # Para otras categorías, incluir específicos del género Y unisex
                assets = crud_avatar_asset.get_by_category(
                    db, category=category, gender=gender, active_only=True
                )

            asset_list = []

            for asset in assets:
                # Construir URL completa del asset con dominio para que funcione en frontend
                asset_url = f"http://localhost:8000/static/assets/{asset.filename}"

                asset_info = {
                    "id": str(asset.id),
                    "filename": asset.filename,
                    "display_name": asset.display_name or asset.filename.split("/")[-1],
                    "target_gender": asset.target_gender,
                    "width": asset.width,
                    "height": asset.height,
                    "file_size": asset.file_size,
                    "is_normalized": asset.is_normalized,
                    "meta_info": asset.meta_info or {},
                    "url": asset_url,  # URL absoluta con dominio del backend
                }
                asset_list.append(asset_info)

            manifest["categories"][category] = asset_list
            manifest["total_assets"] += len(asset_list)

        return manifest

    async def generate_preview(
        self, db: Session, base_gender: str, layers: list[dict[str, str]]
    ) -> dict[str, Any]:
        """Genera preview de un avatar sin guardarlo.

        Args:
            db: Sesión de base de datos
            base_gender: Género base (male o female)
            layers: Lista de capas [{category: str, file: str}, ...]

        Returns:
            Dict con preview_url o preview_base64, layers_hash

        Raises:
            ValueError: Si las capas no son válidas
        """
        if not layers:
            msg = "Layers list cannot be empty"
            raise ValueError(msg)

        # Agregar la capa base según el género si no está presente
        has_base = any(layer.get("category") == "base" for layer in layers)
        if not has_base:
            # Obtener asset base correspondiente al género
            base_assets = crud_avatar_asset.get_base_assets(db)
            if base_gender not in base_assets:
                msg = f"No base asset found for gender: {base_gender}"
                raise ValueError(msg)

            base_asset = base_assets[base_gender]
            layers = [{"category": "base", "file": base_asset.filename}, *layers]

        # Generar hash de las capas (incluyendo género para diferenciación)
        layers_with_gender = [{"gender": base_gender}, *layers]
        hash_str = layers_hash(layers_with_gender)

        # Verificar cache primero
        cached_result = self._get_cached_preview(hash_str)
        if cached_result:
            return {
                "preview_url": cached_result,
                "layers_hash": hash_str,
                "from_cache": True,
            }

        # Ordenar capas por prioridad visual (de atrás hacia adelante)
        # sorted_layers = sort_layers_by_priority(layers)  # DESACTIVADO: validate_layers ya ordena
        sorted_layers = layers  # validate_layers se encarga del ordenamiento

        # Validar que las capas existen (pasar base_gender para resolución preferente)
        assets_base_path = os.path.abspath(self.assets_dir)
        layer_files = validate_layers(sorted_layers, assets_base_path, base_gender)

        # Componer imagen
        import time

        try:
            start_time = time.time()
            composed_img = compose_images(layer_files, STANDARD_RESOLUTION)
            compose_time = time.time() - start_time
            print(f"⏱️  Composición de imagen: {compose_time:.3f}s")

            # Guardar preview temporal
            preview_filename = f"preview_{hash_str}.png"
            preview_path = os.path.join(self.avatars_dir, "temp", preview_filename)

            # Crear directorio temporal si no existe
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)

            # Guardar imagen
            save_start = time.time()
            await save_normalized_image(composed_img, preview_path)
            save_time = time.time() - save_start
            print(f"💾 Guardado de imagen: {save_time:.3f}s")

            # URL relativa para servir
            preview_url = f"/static/avatars/temp/{preview_filename}"

            # Guardar en cache con TTL corto (1 hora para previews)
            self._cache_preview(hash_str, preview_url, ttl=self.preview_cache_ttl)

            total_time = time.time() - start_time
            print(f"✅ Tiempo total de generación: {total_time:.3f}s")

            return {
                "preview_url": preview_url,
                "layers_hash": hash_str,
                "from_cache": False,
            }

        except Exception as e:
            msg = f"Error composing avatar: {e!s}"
            raise ValueError(msg) from e

    async def save_avatar(
        self,
        db: Session,
        user_id: UUID,
        name: str,
        base_gender: str,
        layers: list[dict[str, str]],
        is_active: bool = False,
        is_public: bool = True,
    ) -> UserAvatar:
        """Guarda un avatar permanentemente.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            name: Nombre del avatar
            base_gender: Género base (male o female)
            layers: Lista de capas
            is_active: Si será el avatar activo
            is_public: Si será público

        Returns:
            UserAvatar creado

        Raises:
            ValueError: Si las capas no son válidas
        """
        if not layers:
            msg = "Layers list cannot be empty"
            raise ValueError(msg)

        if not name.strip():
            msg = "Avatar name cannot be empty"
            raise ValueError(msg)

        # Generar hash de las capas
        hash_str = layers_hash(layers)

        # Verificar si ya existe un avatar con el mismo hash para este usuario
        existing_avatar = crud_user_avatar.get_by_hash(db, layers_hash=hash_str)
        if existing_avatar and existing_avatar.user_id == user_id:
            # Actualizar el existente en lugar de crear duplicado
            return crud_user_avatar.update(
                db,
                db_obj=existing_avatar,
                obj_in={"name": name, "is_active": is_active, "is_public": is_public},
            )

        # Verificar cache de composición
        cached_image_path = self._get_cached_composition(hash_str)
        if cached_image_path and os.path.exists(cached_image_path):
            # Usar imagen cacheada
            final_image_url = cached_image_path.replace("static/", "/static/")
        else:
            # Componer y guardar nueva imagen (pasar base_gender para resolución preferente)
            final_image_url = await self._compose_and_store(
                db, user_id, layers, hash_str, base_gender
            )

        # Crear registro en base de datos
        return crud_user_avatar.create_avatar(
            db,
            user_id=user_id,
            name=name,
            base_gender=base_gender,
            layers=layers,
            image_url=final_image_url,
            layers_hash=hash_str,
            is_active=is_active,
            is_public=is_public,
        )

    async def _compose_and_store(
        self,
        db: Session,
        user_id: UUID,
        layers: list[dict[str, str]],
        hash_str: str,
        base_gender: str | None = None,
    ) -> str:
        """Compone y almacena una imagen de avatar.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            layers: Capas del avatar
            hash_str: Hash de las capas

        Returns:
            URL de la imagen guardada
        """
        # Validar capas (pasando el género para resolución preferente)
        assets_base_path = os.path.abspath(self.assets_dir)
        layer_files = validate_layers(layers, assets_base_path, base_gender)

        # Componer imagen
        composed_img = compose_images(layer_files, STANDARD_RESOLUTION)

        # Generar path de almacenamiento
        user_avatar_dir = os.path.join(self.avatars_dir, str(user_id))
        avatar_filename = f"{hash_str}.png"
        avatar_path = os.path.join(user_avatar_dir, avatar_filename)

        print(f"📁 [_compose_and_store] Avatar dir: {user_avatar_dir}")
        print(f"📁 [_compose_and_store] Avatar path: {avatar_path}")

        # Crear directorio del usuario si no existe
        os.makedirs(user_avatar_dir, exist_ok=True)

        # Guardar imagen
        await save_normalized_image(composed_img, avatar_path)

        # Verificar que el archivo se guardó
        if os.path.exists(avatar_path):
            file_size = os.path.getsize(avatar_path)
            print(
                f"✅ [_compose_and_store] Avatar guardado: {avatar_path} ({file_size} bytes)"
            )
        else:
            print(
                f"❌ [_compose_and_store] ERROR: Avatar NO se guardó en {avatar_path}"
            )

        # URL para servir
        image_url = f"/static/avatars/{user_id}/{avatar_filename}"
        print(f"🔗 [_compose_and_store] Image URL: {image_url}")

        # Cachear la composición
        self._cache_composition(hash_str, avatar_path)

        return image_url

    def _get_cached_preview(self, hash_str: str) -> str | None:
        """Obtiene preview cacheado por hash."""
        if not self.redis:
            return None

        try:
            cache_key = self._get_preview_cache_key(hash_str)
            cached_url = self.redis.get(cache_key)
            if cached_url:
                return (
                    cached_url.decode("utf-8")
                    if isinstance(cached_url, bytes)
                    else cached_url
                )
        except Exception:
            pass

        return None

    def _cache_preview(
        self, hash_str: str, preview_url: str, ttl: int | None = None
    ) -> None:
        """Cachea preview con TTL."""
        if not self.redis:
            return

        if ttl is None:
            ttl = self.preview_cache_ttl

        try:
            cache_key = self._get_preview_cache_key(hash_str)
            self.redis.setex(cache_key, ttl, preview_url)
        except Exception:
            pass

    def _get_cached_composition(self, hash_str: str) -> str | None:
        """Obtiene composición cacheada por hash."""
        if not self.redis:
            return None

        try:
            cache_key = self._get_cache_key(hash_str)
            cached_path = self.redis.get(cache_key)
            if cached_path:
                path_str = (
                    cached_path.decode("utf-8")
                    if isinstance(cached_path, bytes)
                    else cached_path
                )
                # Verificar que el archivo existe
                if os.path.exists(path_str):
                    return path_str
                # Limpiar cache si el archivo no existe
                self.redis.delete(cache_key)
        except Exception:
            pass

        return None

    def _cache_composition(self, hash_str: str, image_path: str) -> None:
        """Cachea composición con TTL largo."""
        if not self.redis:
            return

        try:
            cache_key = self._get_cache_key(hash_str)
            self.redis.setex(cache_key, self.cache_ttl, image_path)
        except Exception:
            pass

    async def delete_avatar(self, db: Session, user_id: UUID, avatar_id: UUID) -> bool:
        """Elimina un avatar y su archivo asociado.

        Args:
            db: Sesión de base de datos
            user_id: ID del usuario propietario
            avatar_id: ID del avatar a eliminar

        Returns:
            True si se eliminó correctamente, False si no se encontró
        """
        # Obtener avatar
        avatar = crud_user_avatar.get(db, id=avatar_id)
        if not avatar or avatar.user_id != user_id:
            return False

        # Verificar si otros avatars usan la misma imagen (mismo hash)
        same_hash_avatars = (
            db.query(UserAvatar)
            .filter(
                UserAvatar.layers_hash == avatar.layers_hash, UserAvatar.id != avatar_id
            )
            .count()
        )

        # Solo eliminar archivo si no hay otros avatars usándolo
        if same_hash_avatars == 0:
            try:
                # Construir path del archivo
                if avatar.image_url.startswith("/static/"):
                    file_path = avatar.image_url[1:]  # Remover / inicial
                    if os.path.exists(file_path):
                        os.remove(file_path)

                # Limpiar cache
                if self.redis:
                    cache_key = self._get_cache_key(avatar.layers_hash)
                    self.redis.delete(cache_key)

            except Exception:
                pass

        # Eliminar registro de DB
        deleted_avatar = crud_user_avatar.delete_user_avatar(
            db, user_id=user_id, avatar_id=avatar_id
        )

        return deleted_avatar is not None

    async def cleanup_temp_previews(self, max_age_hours: int = 24) -> None:
        """Limpia previews temporales antiguos.

        Args:
            max_age_hours: Edad máxima en horas para mantener previews
        """
        temp_dir = os.path.join(self.avatars_dir, "temp")
        if not os.path.exists(temp_dir):
            return

        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for filename in os.listdir(temp_dir):
            if filename.startswith("preview_") and filename.endswith(".png"):
                file_path = os.path.join(temp_dir, filename)
                file_age = current_time - os.path.getmtime(file_path)

                if file_age > max_age_seconds:
                    with contextlib.suppress(Exception):
                        os.remove(file_path)

    def get_cache_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas del cache Redis.

        Returns:
            Dict con estadísticas del cache
        """
        if not self.redis:
            return {"error": "Redis not connected"}

        try:
            # Contar claves de composiciones y previews
            comp_keys = len(self.redis.keys("avatar_comp:*"))
            preview_keys = len(self.redis.keys("avatar_preview:*"))

            # Información de memoria (si está disponible)
            try:
                info = self.redis.info("memory")
                memory_used = info.get("used_memory_human", "N/A")
            except:
                memory_used = "N/A"

            return {
                "compositions_cached": comp_keys,
                "previews_cached": preview_keys,
                "total_keys": comp_keys + preview_keys,
                "memory_used": memory_used,
                "cache_ttl_hours": self.cache_ttl // 3600,
            }

        except Exception as e:
            return {"error": f"Error getting cache stats: {e}"}


# Instancia global del servicio
avatar_service = AvatarService()
