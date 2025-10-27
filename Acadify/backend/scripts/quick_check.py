#!/usr/bin/env python3
"""
Script de verificación básica del sistema de avatares.
No requiere dependencias instaladas.
"""

import os
import json
from pathlib import Path


def check_file_structure():
    """Verifica la estructura de archivos del proyecto."""
    print("=== Verificando estructura de archivos ===")
    
    backend_files = [
        "src/models/avatar/avatar_asset.py",
        "src/models/avatar/user_avatar.py", 
        "src/services/avatar_service.py",
        "src/services/storage.py",
        "src/utils/image_utils.py",
        "src/api/routes/avatar.py",
        "src/crud/avatar/avatar_asset_crud.py",
        "src/crud/avatar/user_avatar_crud.py",
        "src/schemas/avatar/avatar_schemas.py",
        "scripts/sync_assets.py",
        "scripts/load_initial_assets.py",
        "scripts/validate_assets.py",
        "alembic/versions/a1b2c3d4e5f6_add_avatar_tables.py"
    ]
    
    frontend_files = [
        "../frontend/src/components/avatar/AvatarEditor.tsx",
        "../frontend/src/components/avatar/PreviewCanvas.tsx", 
        "../frontend/src/components/avatar/LayerPicker.tsx",
        "../frontend/src/components/avatar/SaveAvatarDialog.tsx",
        "../frontend/src/components/avatar/AvatarGallery.tsx",
        "../frontend/src/components/avatar/avatarAPI.ts",
        "../frontend/src/components/avatar/useAvatar.ts",
        "../frontend/src/components/avatar/index.ts"
    ]
    
    all_files = backend_files + frontend_files
    missing_files = []
    existing_files = []
    
    for file_path in all_files:
        full_path = Path(file_path)
        if full_path.exists():
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path}")
    
    print(f"\nResumen:")
    print(f"  Archivos existentes: {len(existing_files)}")
    print(f"  Archivos faltantes: {len(missing_files)}")
    
    return len(missing_files) == 0


def check_configuration():
    """Verifica archivos de configuración."""
    print("\n=== Verificando configuración ===")
    
    config_file = Path("src/core/config.py")
    if not config_file.exists():
        print("❌ config.py no encontrado")
        return False
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Verificar configuraciones de avatar
        avatar_configs = [
            "AVATAR_STORAGE_TYPE",
            "AVATAR_ASSETS_PATH", 
            "AVATAR_ASSETS_BASE_URL",
            "AVATAR_PREVIEW_CACHE_TTL",
            "AVATAR_COMPOSITION_CACHE_TTL"
        ]
        
        missing_configs = []
        for config in avatar_configs:
            if config not in content:
                missing_configs.append(config)
            else:
                print(f"✅ {config}")
        
        if missing_configs:
            print(f"❌ Configuraciones faltantes: {missing_configs}")
            return False
        else:
            print("✅ Todas las configuraciones de avatar presentes")
            return True
            
    except Exception as e:
        print(f"❌ Error leyendo config.py: {e}")
        return False


def check_migrations():
    """Verifica migración de base de datos."""
    print("\n=== Verificando migraciones ===")
    
    migration_file = Path("alembic/versions/a1b2c3d4e5f6_add_avatar_tables.py")
    if not migration_file.exists():
        print("❌ Migración de avatar no encontrada")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            content = f.read()
        
        # Verificar que contiene las tablas esperadas
        required_tables = ["avatar_asset", "user_avatar"]
        tables_found = []
        
        for table in required_tables:
            if f"create_table('{table}'" in content:
                tables_found.append(table)
                print(f"✅ Tabla {table}")
            else:
                print(f"❌ Tabla {table}")
        
        if len(tables_found) == len(required_tables):
            print("✅ Migración completa")
            return True
        else:
            print(f"❌ Faltan tablas: {set(required_tables) - set(tables_found)}")
            return False
            
    except Exception as e:
        print(f"❌ Error leyendo migración: {e}")
        return False


def check_assets_structure():
    """Verifica estructura de assets."""
    print("\n=== Verificando estructura de assets ===")
    
    # Buscar directorio de assets
    possible_assets_dirs = [
        "static/assets",
        "../static/assets", 
        "assets"
    ]
    
    assets_dir = None
    for dir_path in possible_assets_dirs:
        if Path(dir_path).exists():
            assets_dir = Path(dir_path)
            break
    
    if not assets_dir:
        print("⚠️  Directorio de assets no encontrado")
        print("   Se puede crear con: python3 scripts/load_initial_assets.py")
        return False
    
    print(f"✅ Directorio de assets: {assets_dir}")
    
    # Verificar categorías esperadas
    expected_categories = ['base', 'hair', 'eyes', 'clothes', 'accessories', 'backgrounds']
    found_categories = []
    
    for category in expected_categories:
        category_path = assets_dir / category
        if category_path.exists() and category_path.is_dir():
            png_files = list(category_path.glob('*.png'))
            found_categories.append(category)
            print(f"✅ {category}: {len(png_files)} archivos")
        else:
            print(f"❌ {category}: no encontrado")
    
    if len(found_categories) >= 3:  # Al menos 3 categorías
        print("✅ Estructura de assets básica")
        return True
    else:
        print("❌ Estructura de assets incompleta")
        return False


def check_frontend_integration():
    """Verifica integración del frontend."""
    print("\n=== Verificando integración frontend ===")
    
    # Verificar archivo principal de API
    api_file = Path("../frontend/src/components/avatar/avatarAPI.ts")
    if not api_file.exists():
        print("❌ avatarAPI.ts no encontrado")
        return False
    
    try:
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Verificar endpoints principales
        endpoints = [
            "/assets",
            "/preview", 
            "/save",
            "/me"
        ]
        
        endpoints_found = []
        for endpoint in endpoints:
            if f"'{endpoint}'" in content or f'"{endpoint}"' in content:
                endpoints_found.append(endpoint)
                print(f"✅ Endpoint {endpoint}")
            else:
                print(f"❌ Endpoint {endpoint}")
        
        if len(endpoints_found) >= 3:
            print("✅ Integración API básica")
            return True
        else:
            print("❌ Integración API incompleta")
            return False
            
    except Exception as e:
        print(f"❌ Error leyendo avatarAPI.ts: {e}")
        return False


def generate_summary_report(results):
    """Genera reporte resumen."""
    print("\n" + "="*60)
    print("REPORTE DE VERIFICACIÓN DEL SISTEMA DE AVATARES")
    print("="*60)
    
    total_checks = len(results)
    passed_checks = sum(1 for r in results.values() if r)
    
    print(f"Total verificaciones: {total_checks}")
    print(f"Exitosas: {passed_checks}")
    print(f"Fallidas: {total_checks - passed_checks}")
    print(f"Porcentaje de éxito: {(passed_checks/total_checks)*100:.1f}%")
    
    print("\nResultados detallados:")
    for check_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {check_name}")
    
    if passed_checks == total_checks:
        print("\n🎉 ¡Sistema completo y listo para usar!")
        return True
    else:
        print(f"\n⚠️  Sistema incompleto. Revisar elementos fallidos.")
        return False


def main():
    """Función principal."""
    print("VERIFICACIÓN RÁPIDA DEL SISTEMA DE AVATARES")
    print("="*50)
    
    # Ejecutar verificaciones
    results = {
        "Estructura de archivos": check_file_structure(),
        "Configuración": check_configuration(),
        "Migraciones": check_migrations(),
        "Assets": check_assets_structure(),
        "Integración Frontend": check_frontend_integration()
    }
    
    # Generar reporte
    success = generate_summary_report(results)
    
    if not success:
        print("\n📋 ACCIONES RECOMENDADAS:")
        print("1. Ejecutar: python3 scripts/load_initial_assets.py")
        print("2. Ejecutar: python3 scripts/sync_assets.py") 
        print("3. Verificar configuración en .env")
        print("4. Ejecutar migración: alembic upgrade head")
    
    return success


if __name__ == "__main__":
    os.chdir("/home/esteban/Acadify/backend")
    success = main()
    exit(0 if success else 1)