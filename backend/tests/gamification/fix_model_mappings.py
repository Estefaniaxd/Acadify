#!/usr/bin/env python3
"""
Script para corregir mapeos de campos entre tests y modelos reales.
Analiza los modelos y actualiza los fixtures automáticamente.
"""

import re
from pathlib import Path

# Mapeo de correcciones a aplicar
FIELD_MAPPINGS = {
    # Usuario
    'Usuario': {
        'id': 'usuario_id',
        'email': 'correo_institucional',
        'nombre': 'nombres',
        'apellido': 'apellidos',
        'hashed_password': 'password_hash',
        'email_verified': 'email_verified',  # Ya está correcto
    },
    
    # UsuarioPuntos - Este modelo NO tiene nivel ni puntos_nivel_actual
    'UsuarioPuntos': {
        'nivel': None,  # REMOVER - no existe en modelo
        'puntos_nivel_actual': None,  # REMOVER - no existe
        'puntos_siguiente_nivel': None,  # REMOVER - no existe
        # Campos válidos: usuario_id, puntos_acumulados, cambio, motivo, fecha
    },
    
    # HistorialPuntos
    'HistorialPuntos': {
        'puntos': 'cambio',  # El campo se llama 'cambio' no 'puntos'
        'descripcion': 'motivo',  # El campo se llama 'motivo' no 'descripcion'
        # Campos válidos: historial_id, usuario_id, cambio, motivo, fecha
    },
}

def fix_conftest():
    """Corrige el archivo conftest.py"""
    conftest_path = Path(__file__).parent / "conftest.py"
    
    with open(conftest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix 1: UsuarioPuntos - Remover campos que no existen
    print("🔧 Fixing UsuarioPuntos fixture...")
    
    # Buscar y reemplazar fixture usuario_puntos
    pattern = r'(UsuarioPuntos\(\s*usuario_id=estudiante_user\.usuario_id,\s*puntos_acumulados=\d+,)\s*nivel="[^"]*",\s*puntos_nivel_actual=\d+,\s*puntos_siguiente_nivel=\d+\s*\)'
    replacement = r'\1\n        cambio=1000,\n        motivo="Puntos iniciales de prueba"\n    )'
    content = re.sub(pattern, replacement, content)
    
    # Fix 2: HistorialPuntos - Cambiar 'puntos' a 'cambio'
    print("🔧 Fixing HistorialPuntos fixture...")
    content = re.sub(r'\bpuntos=(\d+)', r'cambio=\1', content)
    content = re.sub(r'\bdescripcion=', r'motivo=', content)
    
    # Fix 3: Más referencias a .id que quedaron
    print("🔧 Fixing remaining .id references...")
    content = re.sub(r'(\w+_user)\.id\b', r'\1.usuario_id', content)
    
    # Fix 4: Usuario constructor - id=uuid4() en otros fixtures
    print("🔧 Fixing Usuario(id=...) in test file...")
    content = re.sub(r'Usuario\(\s*id=uuid4\(\),', 'Usuario(', content)
    
    if content != original_content:
        with open(conftest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ conftest.py updated successfully!")
        return True
    else:
        print("ℹ️  No changes needed in conftest.py")
        return False

def fix_test_files():
    """Corrige los archivos de test"""
    test_files = [
        'test_puntos_api.py',
        'test_etiquetas_api.py',
        'test_tienda_api.py',
        'test_rachas_api.py'
    ]
    
    changes_made = False
    
    for filename in test_files:
        filepath = Path(__file__).parent / filename
        if not filepath.exists():
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        print(f"\n🔧 Fixing {filename}...")
        
        # Fix: Usuario(id=uuid4()) en tests
        content = re.sub(r'Usuario\(\s*id=uuid4\(\),', 'Usuario(', content)
        
        # Fix: Accesos a .id
        content = re.sub(r'(\w+)\.id\b', r'\1.usuario_id', content)
        
        # Fix: Assertions con 'nivel' en UsuarioPuntos
        # Los tests esperan nivel pero el modelo no lo tiene - necesitan ajustarse
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ {filename} updated")
            changes_made = True
        else:
            print(f"  ℹ️  No changes needed in {filename}")
    
    return changes_made

def show_model_info():
    """Muestra información sobre los modelos para referencia"""
    print("\n" + "="*70)
    print("📚 REFERENCIA DE MODELOS")
    print("="*70)
    
    print("\n🔹 Usuario:")
    print("  - usuario_id (UUID, PK)")
    print("  - correo_institucional, username")
    print("  - nombres, apellidos")
    print("  - password_hash")
    print("  - rol, estado_cuenta")
    print("  - email_verified, failed_login_attempts")
    
    print("\n🔹 UsuarioPuntos:")
    print("  - usuario_id (UUID, PK, FK)")
    print("  - puntos_acumulados (INTEGER)")
    print("  - cambio (INTEGER) - último cambio de puntos")
    print("  - motivo (TEXT)")
    print("  - fecha (TIMESTAMP)")
    print("  ⚠️  NO TIENE: nivel, puntos_nivel_actual, puntos_siguiente_nivel")
    
    print("\n🔹 HistorialPuntos:")
    print("  - historial_id (UUID, PK)")
    print("  - usuario_id (UUID, FK)")
    print("  - cambio (INTEGER) - cantidad de puntos")
    print("  - motivo (TEXT)")
    print("  - fecha (TIMESTAMP)")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    print("🚀 Starting model mapping fixes...\n")
    
    show_model_info()
    
    conftest_changed = fix_conftest()
    tests_changed = fix_test_files()
    
    if conftest_changed or tests_changed:
        print("\n" + "="*70)
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 Next steps:")
        print("  1. Review the changes in conftest.py")
        print("  2. Run: pytest tests/gamification/test_puntos_api.py -v")
        print("  3. Check if UsuarioPuntos needs nivel field added to model")
        print("     OR update test expectations to not expect nivel")
    else:
        print("\n✨ All files are already up to date!")
