#!/usr/bin/env python3
"""
Script para extraer información detallada de errores específicos
Clean Code: funciones pequeñas, nombres descriptivos, principio DRY
"""
import subprocess
import re
from typing import List, Dict
from pathlib import Path


class ErrorExtractor:
    """Extrae información detallada de errores de pytest"""
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.base_path = Path(__file__).parent.parent
    
    def get_specific_error(self, test_name: str) -> Dict:
        """Obtiene el error específico de un test"""
        cmd = f"venv/bin/python -m pytest {self.test_file}::{test_name} -v --tb=long"
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=self.base_path
        )
        
        output = result.stdout + result.stderr
        
        return {
            'test_name': test_name,
            'output': output,
            'error_type': self._extract_error_type(output),
            'error_message': self._extract_error_message(output),
            'file_location': self._extract_file_location(output),
            'code_snippet': self._extract_code_snippet(output)
        }
    
    @staticmethod
    def _extract_error_type(output: str) -> str:
        """Extrae el tipo de error"""
        match = re.search(r'(AttributeError|TypeError|AssertionError|KeyError|ValueError):', output)
        return match.group(1) if match else "Unknown"
    
    @staticmethod
    def _extract_error_message(output: str) -> str:
        """Extrae el mensaje de error"""
        match = re.search(r'(AttributeError|TypeError|AssertionError|KeyError|ValueError): (.+)', output)
        return match.group(2) if match else "No message"
    
    @staticmethod
    def _extract_file_location(output: str) -> str:
        """Extrae la ubicación del archivo donde ocurrió el error"""
        match = re.search(r'(TEST/\S+\.py):(\d+)', output)
        return f"{match.group(1)}:{match.group(2)}" if match else "Unknown"
    
    @staticmethod
    def _extract_code_snippet(output: str) -> str:
        """Extrae el snippet de código que causó el error"""
        # Buscar líneas que empiezan con > (pytest las marca así)
        lines = output.split('\n')
        snippet_lines = []
        in_snippet = False
        
        for line in lines:
            if line.strip().startswith('>'):
                in_snippet = True
                snippet_lines.append(line)
            elif in_snippet and line.strip().startswith('E'):
                snippet_lines.append(line)
            elif in_snippet and not line.strip():
                break
        
        return '\n'.join(snippet_lines[:10])  # Máximo 10 líneas


class FailedTestsCollector:
    """Recolecta todos los tests fallidos"""
    
    @staticmethod
    def get_failed_tests(test_file: str) -> List[str]:
        """Obtiene lista de todos los tests fallidos"""
        cmd = f"venv/bin/python -m pytest {test_file} --collect-only -q"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Ejecutar tests y extraer fallidos
        cmd = f"venv/bin/python -m pytest {test_file} -v --tb=no"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        output = result.stdout + result.stderr
        
        # Extraer nombres de tests fallidos
        pattern = r'(test_\w+)\s+FAILED'
        failed = re.findall(pattern, output)
        
        return failed


def analyze_failed_test(test_name: str, test_file: str):
    """Analiza un test fallido específico y muestra información detallada"""
    extractor = ErrorExtractor(test_file)
    info = extractor.get_specific_error(test_name)
    
    print(f"\n{'='*80}")
    print(f"🔴 TEST: {test_name}")
    print(f"{'='*80}")
    print(f"📍 Ubicación: {info['file_location']}")
    print(f"⚠️  Tipo de Error: {info['error_type']}")
    print(f"💬 Mensaje: {info['error_message'][:200]}")
    
    if info['code_snippet']:
        print(f"\n📝 Código:")
        print(info['code_snippet'])


def main():
    """Función principal"""
    test_file = "TEST/test_calificacion_service.py"
    
    print("🔍 Recolectando tests fallidos...")
    collector = FailedTestsCollector()
    failed_tests = collector.get_failed_tests(test_file)
    
    print(f"\n📊 Total de tests fallidos: {len(failed_tests)}")
    
    if not failed_tests:
        print("✅ ¡Todos los tests pasaron!")
        return
    
    print("\n" + "="*80)
    print("ANÁLISIS DETALLADO DE ERRORES")
    print("="*80)
    
    # Analizar primeros 5 tests fallidos en detalle
    for i, test in enumerate(failed_tests[:5], 1):
        print(f"\n[{i}/{len(failed_tests)}]")
        analyze_failed_test(test, test_file)
    
    if len(failed_tests) > 5:
        print(f"\n\n... y {len(failed_tests) - 5} tests más fallidos")
        print("\nTests restantes:")
        for test in failed_tests[5:]:
            print(f"  - {test}")


if __name__ == "__main__":
    main()
