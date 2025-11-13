#!/usr/bin/env python3
"""
MEGA FIXER - Corrector Automático Universal de Tests
=====================================================

Corrige automáticamente TODOS los problemas detectados:
1. ✅ TipoConfiguracion.PREDEFINIDA → TipoConfiguracion.GLOBAL
2. ✅ fecha_inicio → fecha_apertura (Evaluacion)
3. ✅ fecha_fin → fecha_cierre (Evaluacion)
4. ✅ Mocks incorrectos (Mock() → return_value correcto)
5. ✅ Campos inexistentes (feedback, etc.)
6. ✅ Métodos incorrectos (buscar_evaluaciones → listar_evaluaciones)

Author: GitHub Copilot
Date: 1 nov 2025
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess


class MegaFixer:
    """Corrector automático inteligente de tests"""
    
    def __init__(self, backend_dir: str):
        self.backend_dir = Path(backend_dir)
        self.test_dir = self.backend_dir / "TEST"
        self.corrections_applied = 0
        
    def fix_all(self):
        """Aplica TODAS las correcciones necesarias"""
        print("🚀 MEGA FIXER - Iniciando correcciones automáticas\n")
        print("=" * 70)
        
        # 1. TipoConfiguracion.PREDEFINIDA → GLOBAL
        self.fix_tipo_configuracion()
        
        # 2. Campos de Evaluacion (fecha_inicio, fecha_fin)
        self.fix_evaluacion_fields()
        
        # 3. Mocks incorrectos
        self.fix_mocks()
        
        # 4. Campo feedback inexistente
        self.fix_feedback_field()
        
        # 5. Métodos renombrados
        self.fix_method_names()
        
        # 6. Fixtures con problemas
        self.fix_fixtures()
        
        print(f"\n{'=' * 70}")
        print(f"✅ COMPLETADO: {self.corrections_applied} correcciones aplicadas")
        print(f"{'=' * 70}\n")
        
    def fix_tipo_configuracion(self):
        """Corrige TipoConfiguracion.PREDEFINIDA → TipoConfiguracion.GLOBAL"""
        print("\n📝 Corrigiendo TipoConfiguracion...")
        
        pattern = r'TipoConfiguracion\.PREDEFINIDA'
        replacement = 'TipoConfiguracion.GLOBAL'
        
        count = self._sed_replace_all_tests(pattern, replacement)
        self.corrections_applied += count
        print(f"   ✅ {count} correcciones de TipoConfiguracion")
        
    def fix_evaluacion_fields(self):
        """Corrige campos de Evaluacion"""
        print("\n📝 Corrigiendo campos de Evaluacion...")
        
        corrections = [
            (r'\bfecha_inicio\s*=', 'fecha_apertura='),
            (r'\bfecha_fin\s*=', 'fecha_cierre='),
        ]
        
        total = 0
        for pattern, replacement in corrections:
            count = self._sed_replace_all_tests(pattern, replacement)
            total += count
            
        self.corrections_applied += total
        print(f"   ✅ {total} correcciones de campos Evaluacion")
        
    def fix_mocks(self):
        """Corrige configuraciones de mocks"""
        print("\n📝 Corrigiendo mocks...")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        total = 0
        
        for test_file in test_files:
            content = test_file.read_text()
            original = content
            
            # Mock que devuelve Mock() en lugar de lista
            # Buscar: mock_ia_service.calificar_pregunta_con_ia.return_value = Mock(...)
            # Reemplazar con return_value adecuado
            
            # Patrón 1: Mock() sin return_value en IA service
            if 'mock_ia_service' in content:
                # Buscar líneas con mock_ia_service que no tienen return_value configurado
                content = re.sub(
                    r'(mock_ia_service\.calificar_pregunta_con_ia)\s*=\s*Mock\(\)',
                    r'\1 = Mock(return_value={"puntuacion": 18.0, "feedback": "Excelente respuesta", "es_correcto": True})',
                    content
                )
                
                # Asegurar que return_value retorna dict, no Mock
                content = re.sub(
                    r'(mock_ia_service\.calificar_pregunta_con_ia\.return_value)\s*=\s*Mock\(',
                    r'\1 = {',
                    content
                )
                content = re.sub(
                    r'Mock\(\s*puntuacion\s*=\s*(\d+\.?\d*),?\s*feedback\s*=\s*"([^"]*)"',
                    r'{"puntuacion": \1, "feedback": "\2", "es_correcto": True}',
                    content
                )
            
            # Patrón 2: puntuacion_maxima = Mock() en lugar de float
            content = re.sub(
                r'puntuacion_maxima\s*=\s*Mock\(\)',
                r'puntuacion_maxima = 20.0',
                content
            )
            
            # Patrón 3: Mock para respuestas que debe ser lista
            content = re.sub(
                r'mock_respuestas\s*=\s*Mock\(\)',
                r'mock_respuestas = []',
                content
            )
            
            if content != original:
                test_file.write_text(content)
                changes = content.count('\n') - original.count('\n') + 10  # Aproximado
                total += 1
                
        self.corrections_applied += total
        print(f"   ✅ {total} archivos con mocks corregidos")
        
    def fix_feedback_field(self):
        """Elimina campo 'feedback' que no existe en RespuestaEstudiante"""
        print("\n📝 Eliminando campo 'feedback' inexistente...")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        total = 0
        
        for test_file in test_files:
            content = test_file.read_text()
            original = content
            
            # Buscar RespuestaEstudiante(...feedback=..., ...)
            # y eliminar solo el parámetro feedback
            content = re.sub(
                r',\s*feedback\s*=\s*[^,\)]+',
                '',
                content
            )
            
            if content != original:
                test_file.write_text(content)
                total += 1
                
        self.corrections_applied += total
        print(f"   ✅ {total} archivos con 'feedback' eliminado")
        
    def fix_method_names(self):
        """Corrige nombres de métodos renombrados"""
        print("\n📝 Corrigiendo nombres de métodos...")
        
        corrections = [
            (r'\.buscar_evaluaciones\(', '.listar_evaluaciones('),
        ]
        
        total = 0
        for pattern, replacement in corrections:
            count = self._sed_replace_all_tests(pattern, replacement)
            total += count
            
        self.corrections_applied += total
        print(f"   ✅ {total} correcciones de nombres de métodos")
        
    def fix_fixtures(self):
        """Corrige fixtures con problemas complejos"""
        print("\n📝 Corrigiendo fixtures complejos...")
        
        # Corrección específica para test_evaluacion_service.py
        test_file = self.test_dir / "test_evaluacion_service.py"
        if test_file.exists():
            content = test_file.read_text()
            original = content
            
            # Corregir argumentos en listar_evaluaciones
            # Eliminar argumentos 'tipo' y 'estado' que no existen
            content = re.sub(
                r'service\.listar_evaluaciones\([^)]*tipo\s*=[^,)]+[,\s]*([^)]*)\)',
                r'service.listar_evaluaciones(\1)',
                content
            )
            content = re.sub(
                r'service\.listar_evaluaciones\([^)]*estado\s*=[^,)]+[,\s]*([^)]*)\)',
                r'service.listar_evaluaciones(\1)',
                content
            )
            
            if content != original:
                test_file.write_text(content)
                self.corrections_applied += 1
                print(f"   ✅ Fixtures de test_evaluacion_service.py corregidos")
        
    def _sed_replace_all_tests(self, pattern: str, replacement: str) -> int:
        """Ejecuta sed en todos los archivos de test"""
        test_files = list(self.test_dir.glob("test_*.py"))
        count = 0
        
        for test_file in test_files:
            try:
                # Verificar si el patrón existe
                content = test_file.read_text()
                if re.search(pattern, content):
                    # Aplicar reemplazo
                    new_content = re.sub(pattern, replacement, content)
                    test_file.write_text(new_content)
                    
                    # Contar cambios
                    changes = len(re.findall(pattern, content))
                    count += changes
            except Exception as e:
                print(f"   ⚠️  Error en {test_file.name}: {e}")
                
        return count
    
    def verify_syntax(self) -> bool:
        """Verifica que todos los archivos tengan sintaxis válida"""
        print("\n🔍 Verificando sintaxis...")
        
        test_files = list(self.test_dir.glob("test_*.py"))
        all_valid = True
        
        for test_file in test_files:
            try:
                compile(test_file.read_text(), test_file.name, 'exec')
            except SyntaxError as e:
                print(f"   ❌ Error de sintaxis en {test_file.name}: {e}")
                all_valid = False
                
        if all_valid:
            print("   ✅ Todos los archivos tienen sintaxis válida")
            
        return all_valid


def main():
    """Función principal"""
    backend_dir = os.getcwd()
    
    fixer = MegaFixer(backend_dir)
    fixer.fix_all()
    
    # Verificar sintaxis
    if fixer.verify_syntax():
        print("\n🎯 Listo para ejecutar tests!")
        print("\nComando sugerido:")
        print("venv/bin/python -m pytest TEST/ -v --tb=short")
    else:
        print("\n⚠️  Hay errores de sintaxis. Revisa los archivos.")


if __name__ == "__main__":
    main()
