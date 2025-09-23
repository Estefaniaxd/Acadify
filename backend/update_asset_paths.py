#!/usr/bin/env python3
"""
Script para actualizar la base de datos con las rutas de las imágenes normalizadas.
"""

import os
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.models.avatar.avatar_asset import AvatarAsset

def update_asset_paths():
    """
    Actualiza las rutas de los assets para usar las imágenes normalizadas.
    """
    db = SessionLocal()
    
    try:
        # Obtener todos los assets
        assets = db.query(AvatarAsset).all()
        
        print(f"📊 Actualizando {len(assets)} assets...")
        
        updated_count = 0
        for asset in assets:
            # Construir nueva ruta normalizada
            old_filename = asset.filename
            
            # Cambiar extensión a PNG y ajustar ruta
            if old_filename.endswith('.jpeg') or old_filename.endswith('.jpg'):
                new_filename = old_filename.rsplit('.', 1)[0] + '.png'
            else:
                new_filename = old_filename
            
            # Verificar que el archivo normalizado existe
            normalized_path = f"/home/esteban/Acadify/backend/static/assets_normalized/{new_filename}"
            
            if os.path.exists(normalized_path):
                # Actualizar registro
                asset.filename = new_filename
                asset.width = 512
                asset.height = 512
                # is_normalized es una propiedad calculada, no se asigna directamente
                
                # Calcular nuevo file_size
                try:
                    asset.file_size = os.path.getsize(normalized_path)
                except:
                    asset.file_size = None
                
                print(f"✅ Actualizado: {old_filename} -> {new_filename}")
                updated_count += 1
            else:
                print(f"⚠️  No encontrado: {normalized_path}")
        
        # Guardar cambios
        db.commit()
        print(f"\n🎉 Actualización completada: {updated_count} assets actualizados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_asset_paths()