#!/usr/bin/env python3
"""
Script para corregir automáticamente datetime.now() sin timezone.
Reemplaza datetime.now() por datetime.now(UTC)
"""

import re
from pathlib import Path

# Archivos a corregir
files_to_fix = [
    "src/api/routes/academic/clase.py",
    "src/api/routes/auth/auth_account.py",
    "src/api/routes/classes/clase.py",
    "src/api/routes/communication/videollamadas_ws.py",
    "src/crud/academic/crud_inscripcion.py",
    "src/crud/academic/crud_institucion.py",
    "src/crud/classes/clase.py",
    "src/crud/communication/chat.py",
    "src/crud/communication/faq_bot.py",
    "src/crud/communication/mensaje_bot.py",
    "src/models/academic/inscripcion.py",
    "src/models/academic/tarea.py",
    "src/models/communication/chat.py",
    "src/models/evaluaciones/evaluacion_expandida.py",
    "src/models/evaluaciones/examen.py",
    # Segunda ronda
    "src/models/evaluaciones/intento_respuesta_gamificacion.py",
    "src/services/academic/inscripcion_service.py",
    "src/services/academic/tarea_enriched_service.py",
    "src/services/auth/auth_service.py",
    "src/services/notification_service.py",
    "src/services/users/perfil_service.py",
    "src/services/videollamada_websocket.py",
    "src/services/websocket_manager.py",
]

def fix_datetime_in_file(filepath: str) -> tuple[bool, int]:
    """Corrige datetime.now() sin timezone en un archivo."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ Archivo no encontrado: {filepath}")
        return False, 0
    
    content = path.read_text(encoding='utf-8')
    original_content = content
    
    # Contador de reemplazos
    count = 0
    
    # Asegurar que UTC está importado
    needs_utc_import = False
    has_datetime_import = "from datetime import datetime" in content
    has_utc_import = "UTC" in content or "timezone.utc" in content
    
    # Patrón 1: datetime.now() sin argumentos
    pattern1 = r'\bdatetime\.now\(\s*\)'
    if re.search(pattern1, content):
        content = re.sub(pattern1, 'datetime.now(UTC)', content)
        count += len(re.findall(pattern1, original_content))
        needs_utc_import = True
    
    # Agregar import de UTC si es necesario
    if needs_utc_import and has_datetime_import and not has_utc_import:
        # Buscar línea de import de datetime
        import_pattern = r'from datetime import datetime'
        if re.search(import_pattern, content):
            # Agregar UTC al import existente
            content = re.sub(
                r'from datetime import datetime\b',
                'from datetime import UTC, datetime',
                content
            )
        else:
            # Agregar import completo al inicio
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from datetime import'):
                    lines[i] = 'from datetime import UTC, datetime'
                    break
            content = '\n'.join(lines)
    
    if content != original_content:
        path.write_text(content, encoding='utf-8')
        return True, count
    
    return False, 0

def main():
    print("🔧 Corrigiendo datetime.now() sin timezone...\n")
    
    total_files = 0
    total_fixes = 0
    
    for filepath in files_to_fix:
        modified, count = fix_datetime_in_file(filepath)
        if modified:
            total_files += 1
            total_fixes += count
            print(f"✅ {filepath}: {count} correcciones")
        else:
            print(f"⏭️  {filepath}: Sin cambios")
    
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN:")
    print(f"   Archivos modificados: {total_files}")
    print(f"   Total de correcciones: {total_fixes}")
    print(f"{'='*60}")
    
    if total_fixes > 0:
        print("\n✨ Ejecuta 'black src/' y 'ruff check src/ --fix' para formatear")

if __name__ == "__main__":
    main()
