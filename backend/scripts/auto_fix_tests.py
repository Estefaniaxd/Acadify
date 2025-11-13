#!/usr/bin/env python3
"""
Script automático para corregir errores comunes en tests
Aplica Clean Code y principios SOLID
"""
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Fix:
    """Representa una corrección a aplicar (Data Class para claridad)"""
    pattern: str
    replacement: str
    description: str
    file_pattern: str = "**/*.py"


class ModelFieldCorrector:
    """Corrige campos de modelo incorrectos (Single Responsibility)"""
    
    FIELD_MAPPINGS = {
        # Primary Keys
        r'\bEvaluacion\.id\b': 'Evaluacion.evaluacion_id',
        r'\bPreguntaEvaluacion\.id\b': 'PreguntaEvaluacion.pregunta_id',
        r'\bRespuestaEstudiante\.id\b': 'RespuestaEstudiante.respuesta_id',
        r'\bIntentoEvaluacion\.id\b': 'IntentoEvaluacion.intento_id',
        
        # Instance attributes
        r'\.id\s*==\s*respuesta_id': '.respuesta_id == respuesta_id',
        r'\.id\s*==\s*intento_id': '.intento_id == intento_id',
        r'\.id\s*==\s*pregunta_id': '.pregunta_id == pregunta_id',
        r'\.id\s*==\s*evaluacion_id': '.evaluacion_id == evaluacion_id',
        
        # Field names in constructors
        r'respuesta_estudiante=': 'respuesta_texto=',
        r'revisado_por_id=': 'calificador_id=',
        
        # Common mistakes
        r'\btitulo=(?=.*PreguntaEvaluacion)': 'enunciado=',
    }
    
    @staticmethod
    def apply_corrections(file_path: Path) -> int:
        """Aplica todas las correcciones a un archivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        corrections = 0
        
        for pattern, replacement in ModelFieldCorrector.FIELD_MAPPINGS.items():
            new_content, count = re.subn(pattern, replacement, content)
            corrections += count
            content = new_content
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return corrections


class FixtureValidator:
    """Valida que los fixtures tengan todos los campos requeridos"""
    
    REQUIRED_FIELDS = {
        'Evaluacion': ['evaluacion_id', 'titulo'],
        'PreguntaEvaluacion': ['pregunta_id', 'evaluacion_id', 'enunciado', 'tipo_pregunta', 'orden', 'puntuacion'],
        'RespuestaEstudiante': ['respuesta_id', 'intento_id', 'pregunta_id', 'puntuacion_maxima'],
        'IntentoEvaluacion': ['intento_id', 'evaluacion_id', 'estudiante_id'],
    }
    
    @staticmethod
    def find_incomplete_fixtures(file_path: Path) -> List[Dict]:
        """Encuentra fixtures que no tienen campos requeridos"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        for model, required in FixtureValidator.REQUIRED_FIELDS.items():
            # Buscar constructores del modelo
            pattern = rf'{model}\([^)]+\)'
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                constructor = match.group(0)
                missing = [field for field in required if field not in constructor]
                
                if missing:
                    issues.append({
                        'model': model,
                        'position': match.start(),
                        'missing_fields': missing,
                        'constructor': constructor[:100]
                    })
        
        return issues


class MockFixer:
    """Corrige problemas comunes con mocks"""
    
    @staticmethod
    def fix_mock_returns(file_path: Path) -> int:
        """Corrige mock.return_value que no devuelven objetos correctos"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        corrections = 0
        new_lines = []
        
        for i, line in enumerate(lines):
            # Detectar mocks que devuelven None cuando deberían devolver lista
            if 'mock_db.query' in line and 'all.return_value' in line:
                if '= None' in line or '= []' not in line:
                    # Asegurar que devuelve lista
                    line = re.sub(r'= None', '= []', line)
                    corrections += 1
            
            new_lines.append(line)
        
        if corrections > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        return corrections


class BatchCorrector:
    """Aplica correcciones en batch a múltiples archivos"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.stats = {
            'files_processed': 0,
            'total_corrections': 0,
            'files_with_issues': []
        }
    
    def process_directory(self, pattern: str = "TEST/*.py"):
        """Procesa todos los archivos que coinciden con el patrón"""
        files = list(self.base_path.glob(pattern))
        
        print(f"📁 Procesando {len(files)} archivos...")
        
        for file_path in files:
            print(f"\n🔍 Analizando: {file_path.name}")
            
            # Aplicar correcciones de campos
            corrections = ModelFieldCorrector.apply_corrections(file_path)
            if corrections > 0:
                print(f"  ✅ {corrections} correcciones de campos aplicadas")
                self.stats['total_corrections'] += corrections
            
            # Validar fixtures
            issues = FixtureValidator.find_incomplete_fixtures(file_path)
            if issues:
                print(f"  ⚠️  {len(issues)} fixtures incompletos encontrados")
                self.stats['files_with_issues'].append((file_path.name, issues))
            
            # Corregir mocks
            mock_fixes = MockFixer.fix_mock_returns(file_path)
            if mock_fixes > 0:
                print(f"  ✅ {mock_fixes} correcciones de mocks aplicadas")
                self.stats['total_corrections'] += mock_fixes
            
            self.stats['files_processed'] += 1
    
    def print_report(self):
        """Imprime reporte de correcciones aplicadas"""
        print("\n" + "="*80)
        print("📊 REPORTE DE CORRECCIONES")
        print("="*80)
        print(f"Archivos procesados: {self.stats['files_processed']}")
        print(f"Correcciones aplicadas: {self.stats['total_corrections']}")
        
        if self.stats['files_with_issues']:
            print(f"\n⚠️  Archivos con fixtures incompletos: {len(self.stats['files_with_issues'])}")
            for filename, issues in self.stats['files_with_issues'][:5]:
                print(f"\n  📄 {filename}:")
                for issue in issues[:3]:
                    print(f"    - {issue['model']}: faltan {', '.join(issue['missing_fields'])}")


def run_sed_fixes():
    """Ejecuta correcciones rápidas con sed (para casos masivos)"""
    fixes = [
        # Corregir atributos .id en objetos
        "sed -i 's/\\bpregunta\\.id\\b/pregunta.pregunta_id/g' TEST/*.py",
        "sed -i 's/\\brespuesta\\.id\\b/respuesta.respuesta_id/g' TEST/*.py",
        "sed -i 's/\\bintento\\.id\\b/intento.intento_id/g' TEST/*.py",
        "sed -i 's/\\bevaluacion\\.id\\b/evaluacion.evaluacion_id/g' TEST/*.py",
        
        # Corregir en servicios
        "sed -i 's/\\bPreguntaEvaluacion\\.id\\b/PreguntaEvaluacion.pregunta_id/g' src/services/**/*.py",
        "sed -i 's/\\bRespuestaEstudiante\\.id\\b/RespuestaEstudiante.respuesta_id/g' src/services/**/*.py",
    ]
    
    print("\n🔧 Ejecutando correcciones rápidas con sed...")
    for cmd in fixes:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"  ✅ {cmd[:60]}...")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Error: {e}")


def main():
    """Función principal"""
    print("🚀 Iniciando correcciones automáticas...")
    print("Aplicando Clean Code y principios SOLID\n")
    
    base_path = Path(__file__).parent.parent
    
    # Ejecutar correcciones sed primero (rápido y masivo)
    run_sed_fixes()
    
    # Aplicar correcciones Python (más sofisticadas)
    corrector = BatchCorrector(base_path)
    corrector.process_directory("TEST/test_*.py")
    corrector.process_directory("src/services/evaluaciones/*.py")
    
    # Reporte final
    corrector.print_report()
    
    print("\n" + "="*80)
    print("✨ Correcciones completadas!")
    print("="*80)
    print("\n💡 Ejecuta: python scripts/debug_tests.py para ver el progreso\n")


if __name__ == "__main__":
    main()
