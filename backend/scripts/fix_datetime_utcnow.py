#!/usr/bin/env python3
"""
Script para reemplazar datetime.utcnow() por datetime.now(timezone.utc)
en los archivos principales del servicio.
"""
import re
from pathlib import Path
from typing import List, Tuple

# Archivos a procesar
FILES_TO_FIX = [
    "src/services/academic/comentario_service.py",
    "src/services/academic/tarea_service.py",
    "src/services/academic/inscripcion_service.py",
    "src/services/academic/archivo_service.py",
    "src/services/academic/reaccion_service.py",
    "src/crud/academic/crud_clase.py",
]

def fix_file(filepath: Path) -> Tuple[bool, int]:
    """
    Reemplaza datetime.utcnow() por datetime.now(timezone.utc) en un archivo.
    
    Returns:
        (modified, count): Si se modificó y cuántos reemplazos
    """
    if not filepath.exists():
        print(f"⚠️  Archivo no encontrado: {filepath}")
        return False, 0
    
    content = filepath.read_text()
    original = content
    
    # Reemplazo directo
    content = content.replace("datetime.utcnow()", "datetime.now(timezone.utc)")
    
    count = original.count("datetime.utcnow()")
    modified = content != original
    
    if modified:
        # Verificar si ya tiene el import de timezone
        has_timezone_import = "from datetime import" in content and "timezone" in content
        
        if not has_timezone_import:
            # Buscar línea con import de datetime
            import_pattern = r"from datetime import ([^\n]+)"
            match = re.search(import_pattern, content)
            
            if match:
                imports = match.group(1)
                if "timezone" not in imports:
                    # Agregar timezone al import existente
                    new_imports = imports.rstrip() + ", timezone"
                    content = content.replace(
                        f"from datetime import {imports}",
                        f"from datetime import {new_imports}"
                    )
            else:
                # Agregar import completo al inicio
                content = "from datetime import timezone\n" + content
        
        filepath.write_text(content)
        print(f"✅ {filepath.name}: {count} reemplazos")
    else:
        print(f"⏭️  {filepath.name}: Sin cambios")
    
    return modified, count

def main():
    """Procesa todos los archivos."""
    base_path = Path(__file__).parent.parent
    
    total_files = 0
    total_replacements = 0
    
    print("🔧 Corrigiendo datetime.utcnow() deprecated...\n")
    
    for relative_path in FILES_TO_FIX:
        filepath = base_path / relative_path
        modified, count = fix_file(filepath)
        
        if modified:
            total_files += 1
            total_replacements += count
    
    print(f"\n✨ Completado:")
    print(f"   - {total_files} archivos modificados")
    print(f"   - {total_replacements} reemplazos realizados")
    print(f"\n📝 Ahora usa: datetime.now(timezone.utc)")

if __name__ == "__main__":
    main()
