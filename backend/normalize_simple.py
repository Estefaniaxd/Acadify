#!/usr/bin/env python3
"""
Script simple para normalizar imágenes de avatars a 512x512 usando solo PIL.
"""
import os
from pathlib import Path

def normalize_images():
    """
    Normaliza todas las imágenes PNG a 512x512 con fondo transparente.
    """
    print("🔧 Normalizando imágenes de avatars...")
    
    try:
        from PIL import Image
    except ImportError:
        print("❌ PIL no está instalado. Instala con: pip install Pillow")
        return False
    
    assets_path = Path(__file__).parent / "static" / "assets"
    
    if not assets_path.exists():
        print(f"❌ Directorio de assets no encontrado: {assets_path}")
        return False
    
    # Buscar todos los archivos PNG
    png_files = list(assets_path.rglob("*.png"))
    
    if not png_files:
        print("❌ No se encontraron archivos PNG")
        return False
    
    print(f"🔍 Encontrados {len(png_files)} archivos PNG")
    
    processed = 0
    errors = 0
    
    for png_file in png_files:
        try:
            print(f"📄 Procesando: {png_file.relative_to(assets_path)}")
            
            # Abrir imagen
            with Image.open(png_file) as img:
                # Verificar si ya tiene el tamaño correcto
                if img.size == (512, 512):
                    print(f"   ✅ Ya tiene el tamaño correcto: 512x512")
                    processed += 1
                    continue
                
                print(f"   📏 Tamaño actual: {img.width}x{img.height}")
                
                # Convertir a RGBA si no lo está
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Crear nueva imagen de 512x512 con fondo transparente
                new_img = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
                
                # Calcular el mejor ajuste manteniendo proporción
                img_ratio = img.width / img.height
                target_ratio = 1.0  # 512/512
                
                if img_ratio > target_ratio:
                    # Imagen más ancha, ajustar por ancho
                    new_width = 512
                    new_height = int(512 / img_ratio)
                else:
                    # Imagen más alta, ajustar por alto
                    new_height = 512
                    new_width = int(512 * img_ratio)
                
                # Redimensionar manteniendo calidad
                resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Centrar en la nueva imagen
                x_offset = (512 - new_width) // 2
                y_offset = (512 - new_height) // 2
                
                new_img.paste(resized, (x_offset, y_offset), resized)
                
                # Guardar imagen normalizada
                new_img.save(png_file, 'PNG', optimize=True)
                
                print(f"   ✅ Normalizada a 512x512 (centrada)")
                processed += 1
                
        except Exception as e:
            print(f"   ❌ Error procesando {png_file.name}: {e}")
            errors += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Procesadas exitosamente: {processed}")
    print(f"   ❌ Errores: {errors}")
    print(f"   📄 Total: {len(png_files)}")
    
    if errors == 0:
        print("\n🎉 ¡Todas las imágenes normalizadas exitosamente!")
        return True
    else:
        print(f"\n⚠️  {errors} imágenes tuvieron problemas")
        return False

if __name__ == "__main__":
    normalize_images()