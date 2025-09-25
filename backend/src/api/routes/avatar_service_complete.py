#!/usr/bin/env python3
"""
Servicio completo de avatars con composición de imágenes.
"""

import os
import io
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from PIL import Image
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Imports for database and auth
from src.api.deps import get_db
from src.api.dependencies import get_current_user

router = APIRouter()

class LayerRequest(BaseModel):
    category: str
    file: str

class GenerateRequest(BaseModel):
    base_gender: str
    layers: List[LayerRequest]

def load_manifest(gender: Optional[str] = None) -> Dict[str, Any]:
    """Cargar manifest desde archivo JSON."""
    try:
        if gender and gender in ["male", "female"]:
            manifest_file = f"static/assets/manifest_{gender}.json"
        else:
            manifest_file = "static/assets/manifest.json"
        
        if not os.path.exists(manifest_file):
            return {"categories": {}, "total_assets": 0, "resolution": [512, 512]}
        
        with open(manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading manifest: {e}")
        return {"categories": {}, "total_assets": 0, "resolution": [512, 512]}

def get_layer_order() -> List[str]:
    """Orden de composición de capas."""
    return [
        'backgrounds',  # Fondo
        'base',         # Cuerpo base
        'makeup',       # Maquillaje base
        'shoes',        # Zapatos (ANTES que pantalones)
        'shirt',        # Camisas/blusas
        'pants',        # Pantalones/faldas (DESPUÉS de zapatos)
        'hair',         # Cabello
        'eyes',         # Ojos
        'mouth',        # Bocas/labios
        'jacket',       # Chaquetas/abrigos
        'accessories'   # Accesorios al frente
    ]

def compose_avatar(base_gender: str, layers: List[LayerRequest]) -> bytes:
    """
    Compone un avatar superponiendo las capas en orden correcto.
    Automáticamente selecciona la base correcta (con o sin ojos).
    """
    # Crear imagen base transparente
    final_image = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    
    # Ordenar capas según el orden correcto
    layer_order = get_layer_order()
    layers_dict = {layer.category: layer.file for layer in layers}
    
    # Verificar si se seleccionaron ojos personalizados
    has_custom_eyes = 'eyes' in layers_dict and layers_dict['eyes']
    
    # Seleccionar la base correcta automáticamente
    if 'base' not in layers_dict:
        if has_custom_eyes:
            # Usar base SIN ojos cuando SÍ se seleccionan ojos personalizados
            layers_dict['base'] = f"base/{base_gender}/{base_gender}_base_ayes.png"
            print(f"🎨 Using base WITHOUT eyes: {layers_dict['base']}")
        else:
            # Usar base sin ojos como predeterminada (cuando NO hay ojos)
            layers_dict['base'] = f"base/{base_gender}/{base_gender}_base_ayes.png"
            print(f"🎨 Using base WITHOUT eyes (default): {layers_dict['base']}")
    
    print(f"🎨 Composing avatar with layers: {layers_dict}")
    print(f"👁️ Has custom eyes: {has_custom_eyes}")
    
    # Aplicar capas en orden
    for category in layer_order:
        if category in layers_dict:
            layer_file = layers_dict[category]
            layer_path = Path("static/assets") / layer_file
            
            print(f"  🖼️ Loading layer: {category} -> {layer_path}")
            
            if layer_path.exists():
                try:
                    with Image.open(layer_path) as layer_img:
                        # Convertir a RGBA si no lo está
                        if layer_img.mode != 'RGBA':
                            layer_img = layer_img.convert('RGBA')
                        
                        # Redimensionar si es necesario
                        if layer_img.size != (512, 512):
                            layer_img = layer_img.resize((512, 512), Image.Resampling.LANCZOS)
                        
                        # Superponer la capa
                        final_image = Image.alpha_composite(final_image, layer_img)
                        print(f"    ✅ Layer {category} applied successfully")
                        
                except Exception as e:
                    print(f"    ❌ Error loading layer {category}: {e}")
            else:
                print(f"    ⚠️ Layer file not found: {layer_path}")
    
    # Convertir a bytes
    img_buffer = io.BytesIO()
    final_image.save(img_buffer, format='PNG', optimize=True)
    img_buffer.seek(0)
    
    print(f"✅ Avatar composed successfully, size: {len(img_buffer.getvalue())} bytes")
    
    return img_buffer.getvalue()

@router.get("/assets")
async def get_assets_manifest_simple(gender: Optional[str] = Query(None)):
    """Obtiene el manifest de assets."""
    try:
        manifest = load_manifest(gender)
        return manifest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading manifest: {str(e)}")

@router.post("/save")
async def save_avatar_endpoint(
    name: str,
    base_gender: str,
    layers: str,  # JSON string of layers
    is_active: bool = True,
    is_public: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Guarda un avatar permanentemente para el usuario."""
    try:
        import hashlib
        import json
        from uuid import uuid4
        from src.crud.avatar.user_avatar_crud import crud_user_avatar
        
        print(f"💾 Saving avatar: {name} for user: {current_user.usuario_id}")
        
        # Validar datos
        if not name.strip():
            raise HTTPException(status_code=400, detail="Avatar name cannot be empty")
        
        # Parse layers JSON
        try:
            layers_data = json.loads(layers)
            print(f"🔍 Parsed layers_data: {layers_data}")
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid layers JSON format")
        
        if not layers_data:
            raise HTTPException(status_code=400, detail="Avatar must have at least one layer")
        
        # Verificar que cada capa tenga las propiedades necesarias
        for i, layer in enumerate(layers_data):
            print(f"🔍 Layer {i}: {layer}")
            if "category" not in layer:
                raise HTTPException(status_code=400, detail=f"Layer {i} missing 'category'")
            if "file" not in layer:
                raise HTTPException(status_code=400, detail=f"Layer {i} missing 'file'")
        
        # Convertir a formato LayerRequest
        layer_requests = [LayerRequest(category=l["category"], file=l["file"]) for l in layers_data]
        
        # Generar avatar
        avatar_bytes = compose_avatar(base_gender, layer_requests)
        
        # Crear hash de las capas para evitar duplicados
        layers_str = json.dumps(layers_data, sort_keys=True)
        layers_hash = hashlib.sha256(layers_str.encode()).hexdigest()
        
        # Crear directorio para avatares del usuario
        user_avatars_dir = f"static/avatars/{current_user.usuario_id}"
        os.makedirs(user_avatars_dir, exist_ok=True)
        
        # Guardar imagen
        avatar_filename = f"{uuid4()}.png"
        avatar_path = os.path.join(user_avatars_dir, avatar_filename)
        
        with open(avatar_path, 'wb') as f:
            f.write(avatar_bytes)
        
        # URL para acceder a la imagen (URL completa)
        image_url = f"http://localhost:8000/static/avatars/{current_user.usuario_id}/{avatar_filename}"
        
        # Guardar en base de datos
        avatar_record = crud_user_avatar.create_avatar(
            db=db,
            user_id=current_user.usuario_id,
            name=name,
            base_gender=base_gender,
            layers=layers_data,
            image_url=image_url,
            layers_hash=layers_hash,
            is_active=is_active,
            is_public=is_public
        )
        
        print(f"✅ Avatar saved successfully: {avatar_record.id}")
        
        return {
            "id": str(avatar_record.id),
            "user_id": str(avatar_record.user_id),
            "name": avatar_record.name,
            "base_gender": avatar_record.base_gender,
            "layers": avatar_record.layers,
            "image_url": avatar_record.image_url,
            "layers_hash": avatar_record.layers_hash,
            "is_active": avatar_record.is_active,
            "is_public": avatar_record.is_public,
            "created_at": avatar_record.created_at.isoformat(),
            "updated_at": avatar_record.updated_at.isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error saving avatar: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving avatar: {str(e)}")

@router.get("/me")
async def get_my_avatars(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Obtiene los avatares del usuario actual."""
    try:
        from src.crud.avatar.user_avatar_crud import crud_user_avatar
        
        avatars = crud_user_avatar.get_by_user(db=db, user_id=current_user.usuario_id)
        
        avatar_list = []
        for avatar in avatars:
            avatar_list.append({
                "id": str(avatar.id),
                "user_id": str(avatar.user_id),
                "name": avatar.name,
                "base_gender": avatar.base_gender,
                "layers": avatar.layers,
                "image_url": avatar.image_url,
                "layers_hash": avatar.layers_hash,
                "is_active": avatar.is_active,
                "is_public": avatar.is_public,
                "created_at": avatar.created_at.isoformat(),
                "updated_at": avatar.updated_at.isoformat()
            })
        
        return {
            "avatars": avatar_list,
            "total": len(avatar_list),
            "has_active": any(a["is_active"] for a in avatar_list),
            "active_avatar_id": next((a["id"] for a in avatar_list if a["is_active"]), None)
        }
        
    except Exception as e:
        print(f"❌ Error getting user avatars: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting avatars: {str(e)}")

@router.post("/generate")
async def generate_avatar_simple(request: GenerateRequest):
    """Genera un avatar compuesto."""
    try:
        print(f"🚀 Generating avatar for gender: {request.base_gender}")
        print(f"📋 Layers requested: {len(request.layers)}")
        
        # Componer avatar
        avatar_bytes = compose_avatar(request.base_gender, request.layers)
        
        # Retornar como imagen
        return StreamingResponse(
            io.BytesIO(avatar_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=avatar.png"}
        )
        
    except Exception as e:
        print(f"❌ Error generating avatar: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating avatar: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba."""
    return {
        "message": "Avatar service is working!",
        "assets_exist": os.path.exists("static/assets"),
        "manifest_exists": os.path.exists("static/assets/manifest.json"),
        "base_male_exists": os.path.exists("static/assets/base/male/male_base.png"),
        "base_female_exists": os.path.exists("static/assets/base/female/female_base.png")
    }