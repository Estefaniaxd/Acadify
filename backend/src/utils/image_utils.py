"""Utilidades para procesamiento de imágenes de avatars.
Maneja validación, normalización, composición y hash de capas.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import aiofiles
from PIL import Image


# Configuración estándar
STANDARD_RESOLUTION = (512, 512)
MAX_FILE_SIZE = 1024 * 1024 * 1.5  # 1.5MB
SUPPORTED_FORMATS = {"PNG", "JPEG"}


def validate_asset_file(file_path: str) -> dict[str, Any]:
    """Valida un archivo de asset PNG.

    Args:
        file_path: Ruta al archivo a validar

    Returns:
        Dict con información de validación: valid, size, format, dimensions, has_transparency

    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no es válido
    """
    if not os.path.exists(file_path):
        msg = f"Asset file not found: {file_path}"
        raise FileNotFoundError(msg)

    # Validar tamaño del archivo
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        msg = f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})"
        raise ValueError(msg)

    try:
        with Image.open(file_path) as img:
            # Validar formato
            if img.format not in SUPPORTED_FORMATS:
                msg = f"Unsupported format: {img.format}. Expected: {SUPPORTED_FORMATS}"
                raise ValueError(msg)

            # Validar que sea RGBA o RGB (con transparencia)
            has_transparency = "transparency" in img.info or img.mode in ("RGBA", "LA")

            return {
                "valid": True,
                "size": file_size,
                "format": img.format,
                "dimensions": img.size,
                "has_transparency": has_transparency,
                "mode": img.mode,
                "matches_standard": img.size == STANDARD_RESOLUTION,
            }

    except Exception as e:
        msg = f"Invalid image file: {e!s}"
        raise ValueError(msg) from e


def normalize_image(
    image_path: str, target_size: tuple[int, int] = STANDARD_RESOLUTION
) -> Image.Image:
    """Normaliza una imagen a la resolución estándar manteniendo la transparencia.

    Args:
        image_path: Ruta a la imagen original
        target_size: Tamaño objetivo (width, height)

    Returns:
        PIL.Image normalizada
    """
    with Image.open(image_path) as img:
        # Convertir a RGBA si no lo es (para mantener transparencia)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        # Si ya tiene el tamaño correcto, devolver copia
        if img.size == target_size:
            return img.copy()

        # Crear canvas transparente del tamaño objetivo
        normalized = Image.new("RGBA", target_size, (0, 0, 0, 0))

        # Redimensionar la imagen manteniendo aspect ratio
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

        # Centrar en el canvas
        paste_x = (target_size[0] - img_resized.width) // 2
        paste_y = (target_size[1] - img_resized.height) // 2

        normalized.paste(img_resized, (paste_x, paste_y), img_resized)

        return normalized


async def save_normalized_image(image: Image.Image, output_path: str) -> None:
    """Guarda una imagen normalizada de forma asíncrona.

    Args:
        image: Imagen PIL a guardar
        output_path: Ruta donde guardar
    """
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Guardar imagen (sync) - PIL no soporta async nativo
    image.save(output_path, "PNG", optimize=True)


def layers_hash(layers: list[dict[str, str]]) -> str:
    """Genera un hash SHA256 de las capas para caching.

    Args:
        layers: Lista de diccionarios con category y file

    Returns:
        Hash SHA256 hexadecimal
    """
    # Crear string ordenado determinístico
    layer_strings = []
    for layer in sorted(
        layers, key=lambda x: (x.get("category", ""), x.get("file", ""))
    ):
        layer_str = f"{layer.get('category', '')}:{layer.get('file', '')}"
        layer_strings.append(layer_str)

    content = "|".join(layer_strings)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compose_images(
    layer_files: list[str], output_size: tuple[int, int] = STANDARD_RESOLUTION
) -> Image.Image:
    """Compone múltiples imágenes PNG en capas.

    Args:
        layer_files: Lista de rutas a archivos PNG en orden de composición
        output_size: Tamaño de la imagen final

    Returns:
        PIL.Image compuesta

    Raises:
        ValueError: Si algún archivo no es válido
    """
    # Crear canvas base transparente
    composed = Image.new("RGBA", output_size, (0, 0, 0, 0))

    for layer_file in layer_files:
        if not os.path.exists(layer_file):
            msg = f"Layer file not found: {layer_file}"
            raise ValueError(msg)

        try:
            with Image.open(layer_file) as layer_img:
                # Convertir a RGBA si es necesario
                if layer_img.mode != "RGBA":
                    layer_img = layer_img.convert("RGBA")

                # Normalizar tamaño si es necesario
                if layer_img.size != output_size:
                    layer_img = normalize_image(layer_file, output_size)

                # Componer usando alpha blending
                composed = Image.alpha_composite(composed, layer_img)

        except Exception as e:
            msg = f"Error composing layer {layer_file}: {e!s}"
            raise ValueError(msg) from e

    return composed


def generate_manifest(assets_dir: str) -> dict[str, Any]:
    """Genera un manifest.json automáticamente escaneando la carpeta de assets.

    Args:
        assets_dir: Ruta a la carpeta de assets

    Returns:
        Diccionario con el manifest
    """
    manifest = {
        "resolution": STANDARD_RESOLUTION,
        "categories": {},
        "total_assets": 0,
        "generated_at": None,
    }

    if not os.path.exists(assets_dir):
        return manifest

    # Escanear cada subcarpeta como categoría
    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and category_path.name != "normalized":
            category = category_path.name
            files = []

            # Buscar archivos PNG en la categoría
            for file_path in category_path.glob("*.png"):
                try:
                    # Validar archivo
                    validation = validate_asset_file(str(file_path))
                    if validation["valid"]:
                        relative_path = f"{category}/{file_path.name}"
                        files.append(
                            {
                                "filename": file_path.name,
                                "path": relative_path,
                                "size": validation["size"],
                                "dimensions": validation["dimensions"],
                                "normalized": validation["matches_standard"],
                            }
                        )
                except Exception:
                    continue

            if files:
                manifest["categories"][category] = files
                manifest["total_assets"] += len(files)

    return manifest


async def save_manifest(manifest: dict[str, Any], output_path: str) -> None:
    """Guarda el manifest.json de forma asíncrona.

    Args:
        manifest: Diccionario del manifest
        output_path: Ruta donde guardar
    """
    import datetime

    manifest["generated_at"] = datetime.datetime.utcnow().isoformat()

    async with aiofiles.open(output_path, "w") as f:
        await f.write(json.dumps(manifest, indent=2, ensure_ascii=False))


def get_layer_order() -> list[str]:
    """Retorna el orden de composición de capas (de fondo a frente).
    
    IMPORTANTE: En PIL, el orden de la lista determina el orden de composición:
    - Primera capa = se pinta PRIMERO = queda AL FONDO (tapado por otras)
    - Última capa = se pinta ÚLTIMA = queda AL FRENTE (tapa a otras)
    
    LÓGICA DE ROPA:
    - Zapatos se pintan PRIMERO (fondo) → quedan TAPADOS por pantalones
    - Pantalones se pintan DESPUÉS → TAPAN parte de los zapatos (correcto visualmente)
    - Camisa se pinta DESPUÉS → TAPA cintura del pantalón
    """
    return [
        "backgrounds",  # 0 - Fondo
        "base",  # 1 - Cuerpo base
        "shoes",  # 2 - Zapatos (PRIMERO = fondo, serán tapados)
        "socks",  # 3 - Medias
        "pants",  # 4 - Pantalones (TAPAN los zapatos)
        "skirt",  # 5 - Faldas
        "shirt",  # 6 - Camisas (TAPAN cintura)
        "jacket",  # 7 - Chaquetas
        "mouth",  # 8 - Boca
        "eyes",  # 9 - Ojos
        "makeup",  # 10 - Maquillaje
        "hair",  # 11 - Cabello
        "accessories",  # 12 - Accesorios (ÚLTIMO = frente)
    ]


def validate_layers(
    layers: list[dict[str, str]], assets_dir: str, base_gender: str | None = None
) -> list[str]:
    """Valida que todas las capas existan y sean válidas.

    Args:
        layers: Lista de capas con category y file
        assets_dir: Directorio base de assets

    Returns:
        Lista de rutas absolutas a los archivos de capas ordenadas

    Raises:
        ValueError: Si alguna capa no es válida
    """
    layer_order = get_layer_order()
    ordered_files = []

    # Organizar capas por orden de composición
    layers_by_category = {layer["category"]: layer for layer in layers}

    for category in layer_order:
        if category in layers_by_category:
            layer = layers_by_category[category]
            file_path = os.path.join(assets_dir, layer["file"])

            # If file doesn't exist, attempt to resolve basename within the category
            if not os.path.exists(file_path):
                # Try to resolve candidates
                basename = os.path.basename(layer.get("file", ""))
                candidates: list[Path] = []

                # First, search inside the specific category folder (including subdirs)
                category_dir = os.path.join(assets_dir, category)
                if os.path.exists(category_dir):
                    for p in Path(category_dir).rglob(basename):
                        if p.is_file():
                            candidates.append(p)

                # If none found, search entire assets tree as fallback
                if not candidates:
                    for p in Path(assets_dir).rglob(basename):
                        if p.is_file():
                            candidates.append(p)

                if len(candidates) == 1:
                    # Resolve to unique candidate and update layer['file'] to relative path
                    chosen = candidates[0]
                    file_path = str(chosen)
                    # update the layer entry to canonical relative path (category/...)
                    rel = os.path.relpath(file_path, assets_dir).replace(os.path.sep, "/")
                    layer["file"] = rel
                elif len(candidates) > 1:
                    # Ambiguous candidates - attempt to resolve using base_gender preference
                    rels = [str(p.relative_to(assets_dir)).replace(os.path.sep, "/") for p in candidates]

                    # If caller provided a base_gender, prefer that gender folder first,
                    # then prefer 'unisex', then fall back to ambiguous error.
                    if base_gender in ("male", "female"):
                        # Prefer candidates inside the category/<gender>/ path
                        preferred = [
                            p
                            for p in candidates
                            if f"/{base_gender}/" in str(p.relative_to(assets_dir)).replace(os.path.sep, "/")
                            or str(p.relative_to(assets_dir)).replace(os.path.sep, "/").startswith(f"{category}/{base_gender}/")
                        ]

                        if len(preferred) == 1:
                            chosen = preferred[0]
                            file_path = str(chosen)
                            rel = os.path.relpath(file_path, assets_dir).replace(os.path.sep, "/")
                            layer["file"] = rel
                        elif len(preferred) > 1:
                            # Still ambiguous among same-gender candidates
                            pref_rels = [
                                str(p.relative_to(assets_dir)).replace(os.path.sep, "/") for p in preferred
                            ]
                            msg = (
                                f"Ambiguous layer file for category '{category}' basename '{basename}' among preferred gender candidates. "
                                f"Candidates: {pref_rels}. Provide full path (category/filename) to disambiguate."
                            )
                            raise ValueError(msg)
                        else:
                            # Try 'unisex' candidates next
                            unisex = [
                                p
                                for p in candidates
                                if "/unisex/" in str(p.relative_to(assets_dir)).replace(os.path.sep, "/")
                                or str(p.relative_to(assets_dir)).replace(os.path.sep, "/").startswith(f"{category}/unisex/")
                            ]

                            if len(unisex) == 1:
                                chosen = unisex[0]
                                file_path = str(chosen)
                                rel = os.path.relpath(file_path, assets_dir).replace(os.path.sep, "/")
                                layer["file"] = rel
                            elif len(unisex) > 1:
                                uni_rels = [
                                    str(p.relative_to(assets_dir)).replace(os.path.sep, "/") for p in unisex
                                ]
                                msg = (
                                    f"Ambiguous layer file for category '{category}' basename '{basename}' among unisex candidates. "
                                    f"Candidates: {uni_rels}. Provide full path (category/filename) to disambiguate."
                                )
                                raise ValueError(msg)
                            else:
                                msg = (
                                    f"Ambiguous layer file for category '{category}' basename '{basename}'. "
                                    f"Candidates: {rels}. Provide full path (category/filename) to disambiguate."
                                )
                                raise ValueError(msg)
                    else:
                        msg = (
                            f"Ambiguous layer file for category '{category}' basename '{basename}'. "
                            f"Candidates: {rels}. Provide full path (category/filename) to disambiguate."
                        )
                        raise ValueError(msg)
                else:
                    msg = f"Layer file not found: {file_path} (and no candidates found for basename '{basename}')"
                    raise ValueError(msg)

            # Validar que es un PNG válido
            try:
                validate_asset_file(file_path)
                ordered_files.append(file_path)
            except Exception as e:
                msg = f"Invalid layer file {file_path}: {e!s}"
                raise ValueError(msg) from e

    return ordered_files


# Utilidades para normalización masiva
async def normalize_all_assets(assets_dir: str, normalized_dir: str) -> dict[str, Any]:
    """Normaliza todos los assets a la resolución estándar.

    Args:
        assets_dir: Directorio de assets originales
        normalized_dir: Directorio donde guardar normalizados

    Returns:
        Reporte de normalización
    """
    report = {"processed": 0, "normalized": 0, "errors": [], "skipped": 0}

    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and category_path.name != "normalized":
            category = category_path.name
            normalized_category_dir = os.path.join(normalized_dir, category)
            os.makedirs(normalized_category_dir, exist_ok=True)

            for file_path in category_path.glob("*.png"):
                try:
                    report["processed"] += 1

                    # Validar archivo original
                    validation = validate_asset_file(str(file_path))

                    if validation["matches_standard"]:
                        report["skipped"] += 1
                        continue

                    # Normalizar
                    normalized_img = normalize_image(str(file_path))
                    output_path = os.path.join(normalized_category_dir, file_path.name)

                    await save_normalized_image(normalized_img, output_path)
                    report["normalized"] += 1

                except Exception as e:
                    error_msg = f"Error normalizing {file_path}: {e!s}"
                    report["errors"].append(error_msg)

    return report
