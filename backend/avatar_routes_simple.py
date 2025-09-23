#!/usr/bin/env python3
"""
Ruta temporal para servir manifests de assets sin base de datos.
"""

import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()

@router.get("/assets")
async def get_assets_manifest_simple(gender: Optional[str] = Query(None)):
    """
    Obtiene el manifest de assets directamente desde archivos JSON.
    """
    try:
        # Determinar qué manifest cargar
        if gender and gender in ["male", "female"]:
            manifest_file = f"static/assets/manifest_{gender}.json"
        else:
            manifest_file = "static/assets/manifest.json"
        
        # Verificar que el archivo existe
        if not os.path.exists(manifest_file):
            raise HTTPException(
                status_code=404, 
                detail=f"Manifest file not found: {manifest_file}"
            )
        
        # Cargar y retornar el manifest
        with open(manifest_file, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        return manifest
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail="Assets manifest not found"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500, 
            detail="Error parsing manifest file"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error loading assets manifest: {str(e)}"
        )

@router.post("/generate")
async def generate_avatar_simple():
    """
    Placeholder para generar avatars.
    """
    return {"message": "Avatar generation not implemented yet"}