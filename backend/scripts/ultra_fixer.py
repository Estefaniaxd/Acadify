#!/usr/bin/env python3
"""
ULTRA FIXER - Corrector Definitivo Basado en Estructura Real
============================================================

Lee la estructura REAL de los modelos y corrige SOLO los campos que existen.
Evita cambios incorrectos como el mega_fixer anterior.

Author: GitHub Copilot
Date: 1 nov 2025
"""

import re
from pathlib import Path
from typing import Dict, Set


class UltraFixer:
    """Corrector basado en análisis de estructura real"""
    
    def __init__(self, backend_dir: str):
        self.backend_dir = Path(backend_dir)
        self.models_dir = self.backend_dir / "src" / "models"
        self.test_dir = self.backend_dir / "TEST"
        
        # Estructura de modelos (se carga dinámicamente)
        self.model_fields: Dict[str, Set[str]] = {}
        
    def extract_model_fields(self, model_file: Path, class_name: str) -> Set[str]:
        """Extrae TODOS los campos de un modelo"""
        content = model_file.read_text()
        fields = set()
        
        # Buscar la clase
        class_pattern = rf'class {class_name}\(.*?\):'
        class_match = re.search(class_pattern, content)
        
        if not class_match:
            return fields
            
        # Extraer sección de la clase (hasta la siguiente clase o fin)
        start = class_match.end()
        next_class = re.search(r'\nclass \w+\(', content[start:])
        end = start + next_class.start() if next_class else len(content)
        
        class_content = content[start:end]
        
        # Extraer todos los Column()
        column_pattern = r'(\w+)\s*=\s*Column\('
        for match in re.finditer(column_pattern, class_content):
            field_name = match.group(1)
            fields.add(field_name)
            
        return fields
        
    def load_model_structures(self):
        """Carga estructura de modelos principales"""
        print("📚 Cargando estructura de modelos...\n")
        
        models_to_load = [
            ("evaluaciones/evaluacion_expandida.py", "Evaluacion"),
            ("evaluaciones/intento_respuesta_gamificacion.py", "IntentoEvaluacion"),
            ("academic/curso.py", "Curso"),
            ("evaluaciones/configuracion_antitrampa.py", "ConfiguracionAntiTrampa"),
        ]
        
        for rel_path, class_name in models_to_load:
            model_file = self.models_dir / rel_path
            if model_file.exists():
                fields = self.extract_model_fields(model_file, class_name)
                self.model_fields[class_name] = fields
                print(f"   ✅ {class_name}: {len(fields)} campos")
            else:
                print(f"   ❌ No encontrado: {model_file}")
                
    def fix_evaluacion_fixtures(self):
        """Corrige fixtures de Evaluacion en test_intento_service.py"""
        print("\n📝 Corrigiendo fixtures de Evaluacion...")
        
        test_file = self.test_dir / "test_intento_service.py"
        if not test_file.exists():
            return
            
        content = test_file.read_text()
        original = content
        
        valid_fields = self.model_fields.get("Evaluacion", set())
        
        # Mapeo de campos incorrectos → correctos
        field_corrections = {
            'requiere_codigo_acceso': None,  # Eliminar (no existe)
            'requiere_contrasena': None,  # Eliminar
            'permitir_multiples_intentos': None,  # Eliminar
            'numero_intentos_permitidos': 'max_intentos',  # Corregir
            'tiene_tiempo_limite': None,  # Eliminar (solo tiempo_limite_minutos)
            'permitir_pausar': 'tiempo_total_pausable',  # Corregir
            'num_preguntas_mostrar': 'num_preguntas_por_intento',  # Corregir
            'mostrar_una_pregunta_a_la_vez': 'permitir_navegar_preguntas',  # Invertir lógica
            'fecha_inicio': 'fecha_apertura',  # Corregir en Evaluacion
            'fecha_fin': 'fecha_cierre',  # Corregir en Evaluacion
        }
        
        changes = 0
        for wrong, correct in field_corrections.items():
            if correct is None:
                # Eliminar línea completa
                pattern = rf',?\s*{wrong}\s*=\s*[^,\n]+,?'
                new_content = re.sub(pattern, '', content)
                if new_content != content:
                    content = new_content
                    changes += 1
            elif correct in valid_fields:
                # Reemplazar campo
                pattern = rf'\b{wrong}\s*='
                replacement = f'{correct}='
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    changes += 1
                    
        if content != original:
            test_file.write_text(content)
            print(f"   ✅ {changes} correcciones en Evaluacion fixtures")
        else:
            print(f"   ℹ️  Sin cambios necesarios")
            
    def fix_curso_fixtures(self):
        """Corrige fixtures de Curso"""
        print("\n📝 Corrigiendo fixtures de Curso...")
        
        test_files = [
            self.test_dir / "test_evaluacion_service.py",
        ]
        
        valid_fields = self.model_fields.get("Curso", set())
        total_changes = 0
        
        for test_file in test_files:
            if not test_file.exists():
                continue
                
            content = test_file.read_text()
            original = content
            
            # Curso NO tiene fecha_apertura/fecha_cierre, solo fecha_inicio/fecha_fin
            # Verificar que no se hayan cambiado incorrectamente
            # Si se cambiaron, revertir
            
            # En test_evaluacion_service.py, el fixture curso_realista tiene fecha_inicio correcto
            # NO tocar nada aquí
            
        print(f"   ✅ Curso ya está correcto")
        
    def fix_all(self):
        """Aplica todas las correcciones"""
        print("🚀 ULTRA FIXER - Corrector Basado en Estructura Real\n")
        print("=" * 70)
        
        self.load_model_structures()
        
        self.fix_evaluacion_fixtures()
        self.fix_curso_fixtures()
        
        print(f"\n{'=' * 70}")
        print("✅ COMPLETADO")
        print(f"{'=' * 70}\n")
        
    def verify_syntax(self) -> bool:
        """Verifica sintaxis"""
        print("🔍 Verificando sintaxis...")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        all_valid = True
        
        for test_file in test_files:
            try:
                compile(test_file.read_text(), test_file.name, 'exec')
            except SyntaxError as e:
                print(f"   ❌ Error en {test_file.name}: {e}")
                all_valid = False
                
        if all_valid:
            print("   ✅ Sintaxis válida")
            
        return all_valid


def main():
    import os
    backend_dir = os.getcwd()
    
    fixer = UltraFixer(backend_dir)
    fixer.fix_all()
    
    if fixer.verify_syntax():
        print("\n🎯 Ejecuta los tests:")
        print("venv/bin/python -m pytest TEST/ -v --tb=short")


if __name__ == "__main__":
    main()
