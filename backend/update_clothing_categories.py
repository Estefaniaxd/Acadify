#!/usr/bin/env python3
"""
Script para actualizar las categorías de ropa existentes a las nuevas categorías específicas.
"""

from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.avatar.avatar_asset import AvatarAsset

def update_clothing_categories():
    """
    Actualiza las categorías de 'clothes' a categorías específicas.
    """
    db = SessionLocal()
    
    try:
        # Obtener todos los assets de clothes
        clothes_assets = db.query(AvatarAsset).filter(AvatarAsset.category == 'clothes').all()
        
        print(f"📊 Encontrados {len(clothes_assets)} assets de ropa para categorizar...")
        
        # Mapeo de nombres de archivo a categorías
        # Puedes ajustar esto según tus archivos específicos
        category_mappings = {
            # Palabras clave para camisas/blusas
            'shirt': ['shirt', 'blouse', 'blusa', 'camisa', 'top'],
            # Palabras clave para pantalones/faldas  
            'pants': ['pants', 'pantalon', 'falda', 'skirt', 'jeans'],
            # Palabras clave para zapatos
            'shoes': ['shoes', 'zapatos', 'boots', 'botas', 'sneakers'],
            # Palabras clave para chaquetas/abrigos
            'jacket': ['jacket', 'chaqueta', 'coat', 'abrigo', 'blazer', 'hoodie']
        }
        
        updated_count = 0
        
        for asset in clothes_assets:
            filename_lower = asset.filename.lower()
            new_category = None
            
            # Buscar coincidencias en el nombre del archivo
            for category, keywords in category_mappings.items():
                if any(keyword in filename_lower for keyword in keywords):
                    new_category = category
                    break
            
            # Si no se encuentra coincidencia, categorizar como 'shirt' por defecto
            if new_category is None:
                new_category = 'shirt'
                print(f"⚠️  Sin coincidencia para {asset.filename}, categorizando como 'shirt'")
            
            # Actualizar categoría
            asset.category = new_category
            print(f"✅ {asset.filename} -> {new_category}")
            updated_count += 1
        
        # Guardar cambios
        db.commit()
        print(f"\n🎉 Actualización completada: {updated_count} assets categorizados")
        
        # Mostrar resumen por categoría
        print("\n📊 Resumen por categoría:")
        for category in ['shirt', 'pants', 'shoes', 'jacket']:
            count = db.query(AvatarAsset).filter(AvatarAsset.category == category).count()
            print(f"   {category}: {count} assets")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_clothing_categories()