"""
Utilidades para procesamiento de imágenes de avatars.
Maneja validación, normalización, composición y hash de capas.
"""

import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from PIL import Image, ImageDraw
import json
import asyncio
import aiofiles

# Configuración estándar
STANDARD_RESOLUTION = (512, 512)
MAX_FILE_SIZE = 1024 * 1024 * 1.5  # 1.5MB
SUPPORTED_FORMATS = {'PNG', 'JPEG'}


def validate_asset_file(file_path: str) -> Dict[str, Any]:
    """
    Valida un archivo de asset PNG.
    
    Args:
        file_path: Ruta al archivo a validar
        
    Returns:
        Dict con información de validación: valid, size, format, dimensions, has_transparency
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        ValueError: Si el archivo no es válido
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Asset file not found: {file_path}")
    
    # Validar tamaño del archivo
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
    
    try:
        with Image.open(file_path) as img:
            # Validar formato
            if img.format not in SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {img.format}. Expected: {SUPPORTED_FORMATS}")
            
            # Validar que sea RGBA o RGB (con transparencia)
            has_transparency = 'transparency' in img.info or img.mode in ('RGBA', 'LA')
            
            validation_info = {
                'valid': True,
                'size': file_size,
                'format': img.format,
                'dimensions': img.size,
                'has_transparency': has_transparency,
                'mode': img.mode,
                'matches_standard': img.size == STANDARD_RESOLUTION
            }
            
            return validation_info
            
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")


def normalize_image(image_path: str, target_size: Tuple[int, int] = STANDARD_RESOLUTION) -> Image.Image:
    """
    Normaliza una imagen a la resolución estándar manteniendo la transparencia.
    
    Args:
        image_path: Ruta a la imagen original
        target_size: Tamaño objetivo (width, height)
        
    Returns:
        PIL.Image normalizada
    """
    with Image.open(image_path) as img:
        # Convertir a RGBA si no lo es (para mantener transparencia)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Si ya tiene el tamaño correcto, devolver copia
        if img.size == target_size:
            return img.copy()
        
        # Crear canvas transparente del tamaño objetivo
        normalized = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Redimensionar la imagen manteniendo aspect ratio
        img_resized = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # Centrar en el canvas
        paste_x = (target_size[0] - img_resized.width) // 2
        paste_y = (target_size[1] - img_resized.height) // 2
        
        normalized.paste(img_resized, (paste_x, paste_y), img_resized)
        
        return normalized


async def save_normalized_image(image: Image.Image, output_path: str) -> None:
    """
    Guarda una imagen normalizada de forma asíncrona.
    
    Args:
        image: Imagen PIL a guardar
        output_path: Ruta donde guardar
    """
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar imagen (sync) - PIL no soporta async nativo
    image.save(output_path, 'PNG', optimize=True)


def layers_hash(layers: List[Dict[str, str]]) -> str:
    """
    Genera un hash SHA256 de las capas para caching.
    
    Args:
        layers: Lista de diccionarios con category y file
        
    Returns:
        Hash SHA256 hexadecimal
    """
    # Crear string ordenado determinístico
    layer_strings = []
    for layer in sorted(layers, key=lambda x: (x.get('category', ''), x.get('file', ''))):
        layer_str = f"{layer.get('category', '')}:{layer.get('file', '')}"
        layer_strings.append(layer_str)
    
    content = "|".join(layer_strings)
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def compose_images(layer_files: List[str], output_size: Tuple[int, int] = STANDARD_RESOLUTION) -> Image.Image:
    """
    Compone múltiples imágenes PNG en capas.
    
    Args:
        layer_files: Lista de rutas a archivos PNG en orden de composición
        output_size: Tamaño de la imagen final
        
    Returns:
        PIL.Image compuesta
        
    Raises:
        ValueError: Si algún archivo no es válido
    """
    # Crear canvas base transparente
    composed = Image.new('RGBA', output_size, (0, 0, 0, 0))
    
    for layer_file in layer_files:
        if not os.path.exists(layer_file):
            raise ValueError(f"Layer file not found: {layer_file}")
        
        try:
            with Image.open(layer_file) as layer_img:
                # Convertir a RGBA si es necesario
                if layer_img.mode != 'RGBA':
                    layer_img = layer_img.convert('RGBA')
                
                # Normalizar tamaño si es necesario
                if layer_img.size != output_size:
                    layer_img = normalize_image(layer_file, output_size)
                
                # Componer usando alpha blending
                composed = Image.alpha_composite(composed, layer_img)
                
        except Exception as e:
            raise ValueError(f"Error composing layer {layer_file}: {str(e)}")
    
    return composed


def generate_manifest(assets_dir: str) -> Dict[str, Any]:
    """
    Genera un manifest.json automáticamente escaneando la carpeta de assets.
    
    Args:
        assets_dir: Ruta a la carpeta de assets
        
    Returns:
        Diccionario con el manifest
    """
    manifest = {
        "resolution": STANDARD_RESOLUTION,
        "categories": {},
        "total_assets": 0,
        "generated_at": None
    }
    
    if not os.path.exists(assets_dir):
        return manifest
    
    # Escanear cada subcarpeta como categoría
    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and category_path.name != 'normalized':
            category = category_path.name
            files = []
            
            # Buscar archivos PNG en la categoría
            for file_path in category_path.glob('*.png'):
                try:
                    # Validar archivo
                    validation = validate_asset_file(str(file_path))
                    if validation['valid']:
                        relative_path = f"{category}/{file_path.name}"
                        files.append({
                            "filename": file_path.name,
                            "path": relative_path,
                            "size": validation['size'],
                            "dimensions": validation['dimensions'],
                            "normalized": validation['matches_standard']
                        })
                except Exception as e:
                    print(f"Warning: Skipping invalid file {file_path}: {e}")
                    continue
            
            if files:
                manifest["categories"][category] = files
                manifest["total_assets"] += len(files)
    
    return manifest


async def save_manifest(manifest: Dict[str, Any], output_path: str) -> None:
    """
    Guarda el manifest.json de forma asíncrona.
    
    Args:
        manifest: Diccionario del manifest
        output_path: Ruta donde guardar
    """
    import datetime
    manifest["generated_at"] = datetime.datetime.utcnow().isoformat()
    
    async with aiofiles.open(output_path, 'w') as f:
        await f.write(json.dumps(manifest, indent=2, ensure_ascii=False))


def get_layer_order() -> List[str]:
    """
    Retorna el orden de composición de capas (de fondo a frente).
    
    Returns:
        Lista ordenada de categorías
    """
    return [
        'backgrounds',  # Fondo
        'base',         # Cuerpo base
        'makeup',       # Maquillaje base (foundation, base makeup)
        'shirt',        # Camisas/blusas (debajo de chaquetas)
        'pants',        # Pantalones/faldas  
        'shoes',        # Zapatos
        'hair',         # Cabello
        'eyes',         # Ojos
        'mouth',        # Bocas/labios
        'jacket',       # Chaquetas/abrigos (encima de camisas)
        'accessories'   # Accesorios al frente
    ]


def validate_layers(layers: List[Dict[str, str]], assets_dir: str) -> List[str]:
    """
    Valida que todas las capas existan y sean válidas.
    
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
    layers_by_category = {layer['category']: layer for layer in layers}
    
    for category in layer_order:
        if category in layers_by_category:
            layer = layers_by_category[category]
            file_path = os.path.join(assets_dir, layer['file'])
            
            # Validar que el archivo existe
            if not os.path.exists(file_path):
                raise ValueError(f"Layer file not found: {file_path}")
            
            # Validar que es un PNG válido
            try:
                validate_asset_file(file_path)
                ordered_files.append(file_path)
            except Exception as e:
                raise ValueError(f"Invalid layer file {file_path}: {str(e)}")
    
    return ordered_files


# Utilidades para normalización masiva
async def normalize_all_assets(assets_dir: str, normalized_dir: str) -> Dict[str, Any]:
    """
    Normaliza todos los assets a la resolución estándar.
    
    Args:
        assets_dir: Directorio de assets originales
        normalized_dir: Directorio donde guardar normalizados
        
    Returns:
        Reporte de normalización
    """
    report = {
        'processed': 0,
        'normalized': 0,
        'errors': [],
        'skipped': 0
    }
    
    for category_path in Path(assets_dir).iterdir():
        if category_path.is_dir() and category_path.name != 'normalized':
            category = category_path.name
            normalized_category_dir = os.path.join(normalized_dir, category)
            os.makedirs(normalized_category_dir, exist_ok=True)
            
            for file_path in category_path.glob('*.png'):
                try:
                    report['processed'] += 1
                    
                    # Validar archivo original
                    validation = validate_asset_file(str(file_path))
                    
                    if validation['matches_standard']:
                        report['skipped'] += 1
                        continue
                    
                    # Normalizar
                    normalized_img = normalize_image(str(file_path))
                    output_path = os.path.join(normalized_category_dir, file_path.name)
                    
                    await save_normalized_image(normalized_img, output_path)
                    report['normalized'] += 1
                    
                except Exception as e:
                    error_msg = f"Error normalizing {file_path}: {str(e)}"
                    report['errors'].append(error_msg)
                    print(f"Warning: {error_msg}")
    
    return report