#!/usr/bin/env python3
"""
Script para diagnosticar errores en tests de forma automática
Aplica principios SOLID y Clean Code
"""
import subprocess
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class TestAnalyzer:
    """Analiza resultados de tests y agrupa errores (Single Responsibility)"""
    
    def __init__(self, test_file: str):
        self.test_file = test_file
        self.errors = defaultdict(list)
        self.passed = []
        self.failed = []
        
    def run_tests(self) -> Tuple[str, int]:
        """Ejecuta tests y retorna output"""
        cmd = f"venv/bin/python -m pytest {self.test_file} -v --tb=short"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout + result.stderr, result.returncode
    
    def parse_results(self, output: str) -> Dict:
        """Parsea output de pytest y extrae información estructurada"""
        results = {
            'passed': [],
            'failed': [],
            'errors': defaultdict(list),
            'summary': {}
        }
        
        # Extraer tests que pasaron
        passed_pattern = r'(test_\w+)\s+PASSED'
        results['passed'] = re.findall(passed_pattern, output)
        
        # Extraer tests que fallaron
        failed_pattern = r'(test_\w+)\s+FAILED'
        results['failed'] = re.findall(failed_pattern, output)
        
        # Agrupar errores por tipo
        error_patterns = {
            'AttributeError': r"AttributeError: (.+)",
            'TypeError': r"TypeError: (.+)",
            'AssertionError': r"AssertionError: (.+)",
            'KeyError': r"KeyError: (.+)",
            'ValueError': r"ValueError: (.+)",
        }
        
        for error_type, pattern in error_patterns.items():
            matches = re.findall(pattern, output)
            for match in matches:
                results['errors'][error_type].append(match)
        
        # Extraer resumen
        summary_pattern = r'(\d+) failed, (\d+) passed'
        summary_match = re.search(summary_pattern, output)
        if summary_match:
            results['summary'] = {
                'failed': int(summary_match.group(1)),
                'passed': int(summary_match.group(2)),
                'total': int(summary_match.group(1)) + int(summary_match.group(2))
            }
        
        return results
    
    def categorize_errors(self, results: Dict) -> Dict:
        """Categoriza errores por tipo de problema"""
        categories = {
            'model_fields': [],
            'primary_keys': [],
            'foreign_keys': [],
            'mock_issues': [],
            'logic_errors': [],
            'other': []
        }
        
        for error_type, messages in results['errors'].items():
            for msg in messages:
                if 'has no attribute' in msg and any(field in msg for field in ['id', '_id']):
                    categories['primary_keys'].append((error_type, msg))
                elif 'invalid keyword argument' in msg:
                    categories['model_fields'].append((error_type, msg))
                elif 'Mock' in msg or 'call' in msg:
                    categories['mock_issues'].append((error_type, msg))
                elif error_type == 'AssertionError':
                    categories['logic_errors'].append((error_type, msg))
                else:
                    categories['other'].append((error_type, msg))
        
        return categories


class ErrorReporter:
    """Genera reportes legibles de errores (Single Responsibility)"""
    
    @staticmethod
    def print_summary(results: Dict):
        """Imprime resumen de tests"""
        print("\n" + "="*80)
        print("📊 RESUMEN DE TESTS")
        print("="*80)
        
        summary = results.get('summary', {})
        if summary:
            total = summary['total']
            passed = summary['passed']
            failed = summary['failed']
            percentage = (passed / total * 100) if total > 0 else 0
            
            print(f"✅ PASSED: {passed}/{total} ({percentage:.1f}%)")
            print(f"❌ FAILED: {failed}/{total}")
            
            # Indicador visual de progreso
            bar_length = 50
            passed_bar = int(bar_length * passed / total) if total > 0 else 0
            failed_bar = bar_length - passed_bar
            print(f"\n[{'█' * passed_bar}{'░' * failed_bar}] {percentage:.1f}%")
    
    @staticmethod
    def print_error_categories(categories: Dict):
        """Imprime errores agrupados por categoría"""
        print("\n" + "="*80)
        print("🔍 ERRORES POR CATEGORÍA")
        print("="*80)
        
        category_names = {
            'model_fields': '📝 Campos de Modelo Inválidos',
            'primary_keys': '🔑 Problemas con Primary Keys',
            'foreign_keys': '🔗 Problemas con Foreign Keys',
            'mock_issues': '🎭 Problemas con Mocks',
            'logic_errors': '⚠️  Errores de Lógica/Aserciones',
            'other': '❓ Otros Errores'
        }
        
        for category, errors in categories.items():
            if errors:
                print(f"\n{category_names.get(category, category)}: {len(errors)} errores")
                for i, (error_type, msg) in enumerate(errors[:3], 1):  # Mostrar solo primeros 3
                    print(f"  {i}. {error_type}: {msg[:100]}...")
                if len(errors) > 3:
                    print(f"  ... y {len(errors) - 3} más")
    
    @staticmethod
    def print_failed_tests(failed_tests: List[str]):
        """Imprime lista de tests fallidos"""
        print("\n" + "="*80)
        print(f"❌ TESTS FALLIDOS ({len(failed_tests)})")
        print("="*80)
        
        for i, test in enumerate(failed_tests, 1):
            print(f"{i:2d}. {test}")


class AutoFixer:
    """Intenta corregir errores comunes automáticamente (Single Responsibility)"""
    
    @staticmethod
    def suggest_fixes(categories: Dict) -> List[str]:
        """Sugiere comandos para corregir errores"""
        suggestions = []
        
        if categories['primary_keys']:
            suggestions.append("# Corregir Primary Keys:")
            suggestions.append("sed -i 's/\\.id\\b/.{model}_id/g' TEST/*.py src/services/**/*.py")
        
        if categories['model_fields']:
            suggestions.append("\n# Verificar campos de modelo:")
            suggestions.append("grep -n 'invalid keyword argument' TEST/*.py")
        
        if categories['mock_issues']:
            suggestions.append("\n# Revisar configuración de mocks:")
            suggestions.append("grep -n 'Mock\\|return_value' TEST/*.py | head -20")
        
        return suggestions


def main():
    """Función principal - orquesta el análisis"""
    test_file = "TEST/test_calificacion_service.py"
    
    print("🚀 Iniciando análisis automático de tests...")
    print(f"📁 Archivo: {test_file}\n")
    
    # Ejecutar análisis
    analyzer = TestAnalyzer(test_file)
    output, exit_code = analyzer.run_tests()
    results = analyzer.parse_results(output)
    categories = analyzer.categorize_errors(results)
    
    # Generar reportes
    reporter = ErrorReporter()
    reporter.print_summary(results)
    reporter.print_error_categories(categories)
    reporter.print_failed_tests(results['failed'])
    
    # Sugerir soluciones
    print("\n" + "="*80)
    print("💡 SUGERENCIAS DE CORRECCIÓN")
    print("="*80)
    
    fixer = AutoFixer()
    suggestions = fixer.suggest_fixes(categories)
    for suggestion in suggestions:
        print(suggestion)
    
    print("\n" + "="*80)
    print(f"✨ Análisis completado. Exit code: {exit_code}")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
