#!/usr/bin/env python3
"""
Script para corregir imports de enums según el modelo correcto
Clean Code: mapeo explícito y claro
"""
from pathlib import Path
import re


def fix_enum_imports():
    """Corrige los imports de enums a sus ubicaciones reales"""
    
    # Mapeo de enums a sus módulos reales
    enum_mappings = {
        # Enums en evaluacion_expandida
        'TipoEvaluacion': 'from src.models.evaluaciones.evaluacion_expandida import TipoEvaluacion',
        'VisibilidadEvaluacion': 'from src.models.evaluaciones.evaluacion_expandida import VisibilidadEvaluacion',
        'ModoEvaluacion': 'from src.models.evaluaciones.evaluacion_expandida import ModoEvaluacion',
        'TipoPreguntaExpandido': 'from src.models.evaluaciones.evaluacion_expandida import TipoPreguntaExpandido',
        'EstadoEvaluacion': 'from src.models.evaluaciones.evaluacion_expandida import EstadoEvaluacion',
        'TipoCalificacion': 'from src.models.evaluaciones.evaluacion_expandida import TipoCalificacion',
        
        # Enums en intento_respuesta_gamificacion
        'EstadoIntento': 'from src.models.evaluaciones.intento_respuesta_gamificacion import EstadoIntento',
        'NivelRiesgoIntento': 'from src.models.evaluaciones.intento_respuesta_gamificacion import NivelRiesgoIntento',
        
        # Alias: TipoPregunta es realmente TipoPreguntaExpandido
        'TipoPregunta': 'TipoPreguntaExpandido',
    }
    
    base_path = Path(__file__).parent.parent
    
    # Archivos a corregir
    test_files = list(base_path.glob("TEST/test_*.py"))
    service_files = list(base_path.glob("src/services/evaluaciones/*.py"))
    
    all_files = test_files + service_files
    
    print(f"🔍 Procesando {len(all_files)} archivos...")
    
    fixes_applied = 0
    
    for file_path in all_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Buscar líneas de import que usan TipoPregunta
        if 'TipoPregunta' in content and 'TipoPreguntaExpandido' not in content:
            # Reemplazar TipoPregunta por TipoPreguntaExpandido en el código
            content = re.sub(r'\bTipoPregunta\.', 'TipoPreguntaExpandido.', content)
            content = re.sub(r'=\s*TipoPregunta\b', '= TipoPreguntaExpandido', content)
            content = re.sub(r'TipoPregunta,', 'TipoPreguntaExpandido,', content)
            
            # También actualizar el import si está presente
            if 'from src.models.evaluaciones.evaluacion_expandida import' in content:
                # Agregar TipoPreguntaExpandido si no está
                import_line_pattern = r'(from src\.models\.evaluaciones\.evaluacion_expandida import [^)]+)'
                matches = re.findall(import_line_pattern, content)
                for match in matches:
                    if 'TipoPregunta' in match and 'TipoPreguntaExpandido' not in match:
                        new_import = match.replace('TipoPregunta', 'TipoPreguntaExpandido')
                        content = content.replace(match, new_import)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            fixes_applied += 1
            print(f"  ✅ {file_path.name}")
    
    print(f"\n📊 Total de archivos corregidos: {fixes_applied}")


def main():
    print("="*80)
    print("🔧 CORRECCIÓN DE IMPORTS DE ENUMS")
    print("="*80 + "\n")
    
    fix_enum_imports()
    
    print("\n" + "="*80)
    print("✨ Correcciones completadas")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
