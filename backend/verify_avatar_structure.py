#!/usr/bin/env python3
"""
Script simple para verificar la estructura de archivos de avatars
sin dependencias del backend.
"""
import os
from pathlib import Path
import json

def check_avatar_structure():
    """
    Verifica que la estructura de archivos esté correcta.
    """
    print("🔍 Verificando estructura de assets de avatars...")
    print()
    
    # Ruta base de assets
    assets_path = Path(__file__).parent / "static" / "assets"
    
    if not assets_path.exists():
        print(f"❌ Directorio de assets no encontrado: {assets_path}")
        return False
    
    print(f"📁 Directorio base: {assets_path}")
    print()
    
    # Categorías esperadas
    expected_categories = [
        'base', 'hair', 'eyes', 'mouth', 'makeup', 
        'shirt', 'pants', 'shoes', 'jacket', 
        'accessories', 'backgrounds'
    ]
    
    # Géneros esperados
    expected_genders = ['male', 'female', 'unisex']
    
    total_files = 0
    structure = {}
    
    for category in expected_categories:
        category_path = assets_path / category
        
        if not category_path.exists():
            print(f"⚠️  Categoría {category} no encontrada")
            continue
            
        structure[category] = {}
        print(f"📂 {category.upper()}:")
        
        for gender in expected_genders:
            gender_path = category_path / gender
            
            if not gender_path.exists():
                print(f"   👤 {gender}: directorio no encontrado")
                continue
            
            # Buscar archivos PNG
            png_files = list(gender_path.glob("*.png"))
            structure[category][gender] = [f.name for f in png_files]
            total_files += len(png_files)
            
            print(f"   👤 {gender}: {len(png_files)} archivos PNG")
            
            # Mostrar primeros 3 archivos como ejemplo
            for i, file in enumerate(png_files[:3]):
                print(f"      - {file.name}")
            if len(png_files) > 3:
                print(f"      ... y {len(png_files) - 3} más")
        
        print()
    
    print(f"📊 RESUMEN:")
    print(f"   📂 Categorías encontradas: {len(structure)}")
    print(f"   📄 Total de archivos PNG: {total_files}")
    print()
    
    # Guardar estructura en JSON para referencia
    structure_file = assets_path / "structure.json"
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Estructura guardada en: {structure_file}")
    
    # Verificar que hay al menos assets básicos
    required_basics = ['base', 'hair']
    missing_basics = []
    
    for basic in required_basics:
        if basic not in structure:
            missing_basics.append(basic)
        elif not any(structure[basic].values()):
            missing_basics.append(f"{basic} (sin archivos)")
    
    if missing_basics:
        print(f"⚠️  Faltan assets básicos: {', '.join(missing_basics)}")
        return False
    
    print("✅ Estructura de assets verificada correctamente!")
    return True

def verify_image_properties():
    """
    Verifica algunas propiedades básicas de las imágenes.
    """
    print("\n🖼️  Verificando propiedades de imágenes...")
    
    try:
        from PIL import Image
        
        assets_path = Path(__file__).parent / "static" / "assets"
        png_files = list(assets_path.rglob("*.png"))
        
        if not png_files:
            print("❌ No se encontraron archivos PNG")
            return False
        
        print(f"🔍 Verificando {len(png_files)} archivos PNG...")
        
        sizes = {}
        issues = []
        
        for png_file in png_files[:10]:  # Solo verificar los primeros 10
            try:
                with Image.open(png_file) as img:
                    size = img.size
                    if size not in sizes:
                        sizes[size] = 0
                    sizes[size] += 1
                    
                    # Verificar que sea 512x512
                    if size != (512, 512):
                        issues.append(f"{png_file.name}: {size[0]}x{size[1]} (esperado 512x512)")
                        
            except Exception as e:
                issues.append(f"{png_file.name}: Error al abrir - {e}")
        
        print(f"📏 Tamaños encontrados:")
        for size, count in sizes.items():
            print(f"   {size[0]}x{size[1]}: {count} archivos")
        
        if issues:
            print(f"\n⚠️  Problemas encontrados:")
            for issue in issues[:5]:  # Solo mostrar primeros 5
                print(f"   - {issue}")
            if len(issues) > 5:
                print(f"   ... y {len(issues) - 5} más")
        else:
            print("✅ Todas las imágenes verificadas tienen el tamaño correcto!")
            
    except ImportError:
        print("⚠️  PIL no disponible, saltando verificación de imágenes")
    
    return True

if __name__ == "__main__":
    success = check_avatar_structure()
    
    if success:
        verify_image_properties()
        print("\n🎉 ¡Verificación completada exitosamente!")
    else:
        print("\n❌ Verificación falló. Revisa la estructura de carpetas.")