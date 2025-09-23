#!/usr/bin/env python3
"""
Script para normalizar imágenes de avatar al formato correcto:
- Convertir JPEG a PNG
- Redimensionar a 512x512
- Eliminar fondo negro y hacer transparente
- Mantener proporción de aspecto
"""

import os
import sys
from PIL import Image, ImageChops, ImageOps
import numpy as np

def remove_black_background(image):
    """
    Remueve el fondo negro y lo hace transparente.
    """
    # Convertir a RGBA si no lo está
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Obtener datos de píxeles
    data = np.array(image)
    
    # Crear máscara para píxeles negros o muy oscuros
    # Consideramos negro cualquier píxel con valores RGB < 30
    black_mask = (data[:,:,0] < 30) & (data[:,:,1] < 30) & (data[:,:,2] < 30)
    
    # Hacer transparentes los píxeles negros
    data[black_mask] = [0, 0, 0, 0]
    
    return Image.fromarray(data, 'RGBA')

def normalize_image(input_path, output_path):
    """
    Normaliza una imagen al formato correcto para avatars.
    """
    try:
        print(f"Procesando: {input_path}")
        
        # Abrir imagen
        with Image.open(input_path) as img:
            print(f"  - Formato original: {img.format}, Tamaño: {img.size}, Modo: {img.mode}")
            
            # Remover fondo negro si es necesario
            if img.mode in ['RGB', 'RGBA']:
                img_no_bg = remove_black_background(img)
            else:
                img_no_bg = img.convert('RGBA')
            
            # Redimensionar manteniendo proporción
            # Para imágenes 576x1280, queremos mantener la proporción pero ajustar a 512x512
            target_size = (512, 512)
            
            # Calcular nuevo tamaño manteniendo proporción
            original_ratio = img.width / img.height
            target_ratio = 1.0  # 512x512 es cuadrado
            
            if original_ratio > target_ratio:
                # Imagen más ancha, ajustar por ancho
                new_width = 512
                new_height = int(512 / original_ratio)
            else:
                # Imagen más alta, ajustar por alto
                new_height = 512
                new_width = int(512 * original_ratio)
            
            # Redimensionar
            img_resized = img_no_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crear imagen final 512x512 con fondo transparente
            final_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            
            # Centrar la imagen redimensionada
            x_offset = (512 - new_width) // 2
            y_offset = (512 - new_height) // 2
            final_img.paste(img_resized, (x_offset, y_offset), img_resized)
            
            # Crear directorio de salida si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Guardar como PNG
            final_img.save(output_path, 'PNG', optimize=True)
            print(f"  ✅ Guardado: {output_path}")
            
            return True
            
    except Exception as e:
        print(f"  ❌ Error procesando {input_path}: {e}")
        return False

def normalize_assets_directory(assets_dir):
    """
    Normaliza todas las imágenes en el directorio de assets.
    """
    assets_path = os.path.abspath(assets_dir)
    normalized_path = os.path.join(os.path.dirname(assets_path), "assets_normalized")
    
    print(f"🔄 Normalizando imágenes desde: {assets_path}")
    print(f"📁 Guardando en: {normalized_path}")
    
    total_processed = 0
    total_success = 0
    
    # Recorrer todas las imágenes
    for root, dirs, files in os.walk(assets_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                input_path = os.path.join(root, file)
                
                # Calcular ruta de salida
                rel_path = os.path.relpath(input_path, assets_path)
                output_file = os.path.splitext(rel_path)[0] + '.png'  # Cambiar extensión a PNG
                output_path = os.path.join(normalized_path, output_file)
                
                total_processed += 1
                if normalize_image(input_path, output_path):
                    total_success += 1
    
    print(f"\n📊 Procesamiento completado:")
    print(f"   Total procesadas: {total_processed}")
    print(f"   Exitosas: {total_success}")
    print(f"   Errores: {total_processed - total_success}")
    print(f"   Imágenes normalizadas en: {normalized_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        assets_dir = sys.argv[1]
    else:
        assets_dir = "/home/esteban/Acadify/backend/static/assets"
    
    if not os.path.exists(assets_dir):
        print(f"❌ Directorio no encontrado: {assets_dir}")
        sys.exit(1)
    
    normalize_assets_directory(assets_dir)