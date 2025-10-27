#!/usr/bin/env python3
"""
Script para cargar assets iniciales de avatars.
Crea la estructura básica de assets para que el sistema funcione.
"""

import os
import sys
import asyncio
from pathlib import Path
from PIL import Image, ImageDraw
from typing import Dict, List, Tuple

# Añadir el directorio src al path para importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import settings
from src.utils.image_utils import STANDARD_RESOLUTION, save_normalized_image


def create_base_assets() -> List[Tuple[str, str, Image.Image]]:
    """
    Crea assets base básicos programáticamente.
    
    Returns:
        Lista de tuplas (category, filename, image)
    """
    assets = []
    
    # Colors for different asset types
    base_colors = [
        (255, 220, 177),  # Light skin
        (241, 194, 125),  # Medium skin
        (198, 134, 66),   # Dark skin
    ]
    
    hair_colors = [
        (139, 69, 19),    # Brown
        (0, 0, 0),        # Black
        (255, 255, 0),    # Blonde
        (255, 69, 0),     # Red
    ]
    
    eye_colors = [
        (139, 69, 19),    # Brown
        (0, 0, 255),      # Blue
        (0, 128, 0),      # Green
        (128, 128, 128),  # Gray
    ]
    
    clothing_colors = [
        (255, 0, 0),      # Red
        (0, 0, 255),      # Blue
        (0, 128, 0),      # Green
        (128, 0, 128),    # Purple
    ]
    
    # Create base assets (body shapes)
    for i, color in enumerate(base_colors, 1):
        img = Image.new('RGBA', STANDARD_RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw simple body shape
        # Head (circle)
        head_center = (256, 150)
        head_radius = 80
        draw.ellipse([
            head_center[0] - head_radius, head_center[1] - head_radius,
            head_center[0] + head_radius, head_center[1] + head_radius
        ], fill=color + (255,))
        
        # Neck
        neck_width = 30
        neck_height = 40
        draw.rectangle([
            head_center[0] - neck_width//2, head_center[1] + head_radius,
            head_center[0] + neck_width//2, head_center[1] + head_radius + neck_height
        ], fill=color + (255,))
        
        # Body (rectangle with rounded top)
        body_width = 120
        body_height = 200
        body_top = head_center[1] + head_radius + neck_height
        draw.rectangle([
            head_center[0] - body_width//2, body_top,
            head_center[0] + body_width//2, body_top + body_height
        ], fill=color + (255,))
        
        assets.append(('base', f'base_{i:03d}.png', img))
    
    # Create hair assets
    for i, color in enumerate(hair_colors, 1):
        img = Image.new('RGBA', STANDARD_RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple hair shape
        head_center = (256, 150)
        hair_radius = 90
        
        # Hair as larger circle covering head
        draw.ellipse([
            head_center[0] - hair_radius, head_center[1] - hair_radius,
            head_center[0] + hair_radius, head_center[1] + hair_radius//2
        ], fill=color + (255,))
        
        assets.append(('hair', f'hair_{i:03d}.png', img))
    
    # Create eye assets
    for i, color in enumerate(eye_colors, 1):
        img = Image.new('RGBA', STANDARD_RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw eyes
        head_center = (256, 150)
        eye_radius = 8
        eye_offset = 25
        
        # Left eye
        left_eye = (head_center[0] - eye_offset, head_center[1] - 10)
        draw.ellipse([
            left_eye[0] - eye_radius, left_eye[1] - eye_radius,
            left_eye[0] + eye_radius, left_eye[1] + eye_radius
        ], fill=(255, 255, 255, 255))
        
        # Left pupil
        draw.ellipse([
            left_eye[0] - eye_radius//2, left_eye[1] - eye_radius//2,
            left_eye[0] + eye_radius//2, left_eye[1] + eye_radius//2
        ], fill=color + (255,))
        
        # Right eye
        right_eye = (head_center[0] + eye_offset, head_center[1] - 10)
        draw.ellipse([
            right_eye[0] - eye_radius, right_eye[1] - eye_radius,
            right_eye[0] + eye_radius, right_eye[1] + eye_radius
        ], fill=(255, 255, 255, 255))
        
        # Right pupil
        draw.ellipse([
            right_eye[0] - eye_radius//2, right_eye[1] - eye_radius//2,
            right_eye[0] + eye_radius//2, right_eye[1] + eye_radius//2
        ], fill=color + (255,))
        
        assets.append(('eyes', f'eyes_{i:03d}.png', img))
    
    # Create clothing assets (simple shirts)
    for i, color in enumerate(clothing_colors, 1):
        img = Image.new('RGBA', STANDARD_RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Simple shirt shape
        head_center = (256, 150)
        shirt_width = 130
        shirt_height = 180
        shirt_top = head_center[1] + 90  # Below neck
        
        draw.rectangle([
            head_center[0] - shirt_width//2, shirt_top,
            head_center[0] + shirt_width//2, shirt_top + shirt_height
        ], fill=color + (255,))
        
        # Sleeves
        sleeve_width = 40
        sleeve_height = 80
        # Left sleeve
        draw.rectangle([
            head_center[0] - shirt_width//2 - sleeve_width, shirt_top,
            head_center[0] - shirt_width//2, shirt_top + sleeve_height
        ], fill=color + (255,))
        # Right sleeve
        draw.rectangle([
            head_center[0] + shirt_width//2, shirt_top,
            head_center[0] + shirt_width//2 + sleeve_width, shirt_top + sleeve_height
        ], fill=color + (255,))
        
        assets.append(('clothes', f'shirt_{i:03d}.png', img))
    
    # Create simple accessories (glasses)
    for i in range(1, 3):
        img = Image.new('RGBA', STANDARD_RESOLUTION, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        head_center = (256, 150)
        frame_color = (0, 0, 0, 255) if i == 1 else (139, 69, 19, 255)
        
        # Glasses frames
        glass_radius = 20
        glass_offset = 30
        frame_width = 3
        
        # Left lens frame
        left_center = (head_center[0] - glass_offset, head_center[1] - 15)
        draw.ellipse([
            left_center[0] - glass_radius, left_center[1] - glass_radius,
            left_center[0] + glass_radius, left_center[1] + glass_radius
        ], outline=frame_color, width=frame_width)
        
        # Right lens frame
        right_center = (head_center[0] + glass_offset, head_center[1] - 15)
        draw.ellipse([
            right_center[0] - glass_radius, right_center[1] - glass_radius,
            right_center[0] + glass_radius, right_center[1] + glass_radius
        ], outline=frame_color, width=frame_width)
        
        # Bridge
        draw.line([
            (left_center[0] + glass_radius, left_center[1]),
            (right_center[0] - glass_radius, right_center[1])
        ], fill=frame_color, width=frame_width)
        
        assets.append(('accessories', f'glasses_{i:03d}.png', img))
    
    # Create simple backgrounds
    background_colors = [
        (135, 206, 235),  # Sky blue
        (144, 238, 144),  # Light green
        (255, 182, 193),  # Light pink
        (221, 160, 221),  # Plum
    ]
    
    for i, color in enumerate(background_colors, 1):
        img = Image.new('RGBA', STANDARD_RESOLUTION, color + (255,))
        assets.append(('backgrounds', f'bg_{i:03d}.png', img))
    
    return assets


async def create_assets_directory_structure():
    """Crea la estructura de directorios para assets."""
    base_dir = Path(settings.AVATAR_ASSETS_PATH)
    
    categories = ['base', 'hair', 'eyes', 'clothes', 'accessories', 'backgrounds']
    
    print(f"Creating assets directory structure at: {base_dir}")
    
    for category in categories:
        category_dir = base_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        print(f"  Created: {category_dir}")
    
    return base_dir


async def save_initial_assets():
    """Guarda los assets iniciales en el directorio."""
    print("Generating initial assets...")
    
    # Crear estructura de directorios
    base_dir = await create_assets_directory_structure()
    
    # Generar assets
    assets = create_base_assets()
    
    print(f"Saving {len(assets)} initial assets...")
    
    for category, filename, image in assets:
        file_path = base_dir / category / filename
        
        # Solo crear si no existe
        if not file_path.exists():
            await save_normalized_image(image, str(file_path))
            print(f"  Created: {category}/{filename}")
        else:
            print(f"  Exists: {category}/{filename}")
    
    print("Initial assets creation completed!")


def create_sample_manifest():
    """Crea un manifest.json de ejemplo."""
    manifest = {
        "resolution": [512, 512],
        "categories": {
            "base": [
                {"filename": "base_001.png", "display_name": "Light Skin"},
                {"filename": "base_002.png", "display_name": "Medium Skin"},
                {"filename": "base_003.png", "display_name": "Dark Skin"}
            ],
            "hair": [
                {"filename": "hair_001.png", "display_name": "Brown Hair"},
                {"filename": "hair_002.png", "display_name": "Black Hair"},
                {"filename": "hair_003.png", "display_name": "Blonde Hair"},
                {"filename": "hair_004.png", "display_name": "Red Hair"}
            ],
            "eyes": [
                {"filename": "eyes_001.png", "display_name": "Brown Eyes"},
                {"filename": "eyes_002.png", "display_name": "Blue Eyes"},
                {"filename": "eyes_003.png", "display_name": "Green Eyes"},
                {"filename": "eyes_004.png", "display_name": "Gray Eyes"}
            ],
            "clothes": [
                {"filename": "shirt_001.png", "display_name": "Red Shirt"},
                {"filename": "shirt_002.png", "display_name": "Blue Shirt"},
                {"filename": "shirt_003.png", "display_name": "Green Shirt"},
                {"filename": "shirt_004.png", "display_name": "Purple Shirt"}
            ],
            "accessories": [
                {"filename": "glasses_001.png", "display_name": "Black Glasses"},
                {"filename": "glasses_002.png", "display_name": "Brown Glasses"}
            ],
            "backgrounds": [
                {"filename": "bg_001.png", "display_name": "Sky Blue"},
                {"filename": "bg_002.png", "display_name": "Light Green"},
                {"filename": "bg_003.png", "display_name": "Light Pink"},
                {"filename": "bg_004.png", "display_name": "Plum"}
            ]
        },
        "total_assets": 21,
        "generated_at": None
    }
    
    return manifest


async def main():
    """Función principal del script."""
    print("=== Avatar Assets Initial Load ===")
    print(f"Target directory: {settings.AVATAR_ASSETS_PATH}")
    print()
    
    try:
        # Crear assets iniciales
        await save_initial_assets()
        
        print("\n" + "="*50)
        print("INITIAL LOAD COMPLETED")
        print("You can now run sync_assets.py to import these into the database.")
        print("="*50)
        
    except Exception as e:
        print(f"Error during initial load: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())