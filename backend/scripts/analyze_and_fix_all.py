#!/usr/bin/env python3
"""
Script Exhaustivo: Análisis y Corrección Automática de TODOS los Tests
Aplicando Clean Code, DRY, y SOLID
"""
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class TestAnalyzer:
    """Analiza y corrige tests automáticamente"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.models_cache = {}
        self.errors = defaultdict(list)
        self.fixes_applied = 0
        
    def analyze_model_structure(self, model_name: str) -> Dict[str, str]:
        """Extrae la estructura real de un modelo"""
        if model_name in self.models_cache:
            return self.models_cache[model_name]
        
        # Mapeo de modelos a archivos
        model_files = {
            'Evaluacion': 'src/models/evaluaciones/evaluacion_expandida.py',
            'PreguntaEvaluacion': 'src/models/evaluaciones/evaluacion_expandida.py',
            'IntentoEvaluacion': 'src/models/evaluaciones/intento_respuesta_gamificacion.py',
            'RespuestaEstudiante': 'src/models/evaluaciones/intento_respuesta_gamificacion.py',
            'Curso': 'src/models/academic/curso.py',
            'ConfiguracionAntiTrampa': 'src/models/evaluaciones/configuracion_antitrampa.py',
        }
        
        if model_name not in model_files:
            return {}
        
        file_path = self.base_path / model_files[model_name]
        if not file_path.exists():
            return {}
        
        structure = {}
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Buscar la clase
        class_match = re.search(rf'class {model_name}\([^)]+\):', content)
        if not class_match:
            return {}
        
        # Extraer campos
        in_class = False
        for line in content[class_match.start():].split('\n'):
            if f'class {model_name}' in line:
                in_class = True
                continue
            if in_class:
                if line.strip().startswith('class ') and model_name not in line:
                    break
                    
                # Buscar Column definitions
                col_match = re.match(r'\s+(\w+)\s*=\s*Column\(', line)
                if col_match:
                    field_name = col_match.group(1)
                    # Detectar si es PK
                    if 'primary_key=True' in line:
                        structure['__pk__'] = field_name
                    structure[field_name] = 'field'
        
        self.models_cache[model_name] = structure
        return structure
    
    def analyze_test_file(self, file_path: Path) -> Dict:
        """Analiza un archivo de test y encuentra errores"""
        print(f"\n🔍 Analizando {file_path.name}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        issues = {
            'wrong_pk': [],
            'wrong_field': [],
            'duplicate_args': [],
            'wrong_enum': [],
            'wrong_import': [],
        }
        
        # Analizar cada fixture/llamada de modelo
        for model in ['Evaluacion', 'PreguntaEvaluacion', 'IntentoEvaluacion', 
                      'RespuestaEstudiante', 'Curso']:
            structure = self.analyze_model_structure(model)
            if not structure:
                continue
            
            pk_field = structure.get('__pk__', 'id')
            
            # Buscar usos incorrectos de id=
            pattern = rf'{model}\([^)]*\bid\s*='
            for match in re.finditer(pattern, content):
                if pk_field != 'id':
                    issues['wrong_pk'].append({
                        'model': model,
                        'should_be': pk_field,
                        'position': match.start()
                    })
        
        # Detectar campos que no existen
        known_issues = {
            'estado_intento': 'estado',
            'revisado_por_id': 'calificador_id',
            'administrador_id': 'coordinador_id',
        }
        
        for wrong, correct in known_issues.items():
            if wrong in content:
                issues['wrong_field'].append({
                    'wrong': wrong,
                    'correct': correct,
                    'count': content.count(wrong)
                })
        
        # Detectar enums incorrectos
        wrong_enums = {
            'TipoEvaluacion.EXAMEN': 'TipoEvaluacion.EXAMEN_FINAL',
            'EstadoEvaluacion.PUBLICADO': 'EstadoEvaluacion.ACTIVA',
            'EstadoEvaluacion.PUBLICADA': 'EstadoEvaluacion.ACTIVA',
        }
        
        for wrong, correct in wrong_enums.items():
            if wrong in content:
                issues['wrong_enum'].append({
                    'wrong': wrong,
                    'correct': correct,
                    'count': content.count(wrong)
                })
        
        return issues
    
    def fix_test_file(self, file_path: Path) -> int:
        """Aplica todas las correcciones a un archivo"""
        print(f"\n🔧 Corrigiendo {file_path.name}...")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        fixes = 0
        
        # 1. Corregir PKs
        pk_fixes = {
            'Evaluacion': 'evaluacion_id',
            'PreguntaEvaluacion': 'pregunta_id',
            'IntentoEvaluacion': 'intento_id',
            'RespuestaEstudiante': 'respuesta_id',
            'Curso': 'curso_id',
        }
        
        for model, pk in pk_fixes.items():
            # Reemplazar id= por pk correcto en constructores
            pattern = rf'({model}\([^)]*)\bid\s*='
            def replacer(m):
                return m.group(1) + f'{pk}='
            new_content = re.sub(pattern, replacer, content)
            if new_content != content:
                fixes += content.count(f'{model}(') - new_content.count(f'{model}(')
                content = new_content
        
        # 2. Corregir accesos a .id
        id_fixes = {
            r'\.curso_id\.id\b': '.curso_id.curso_id',
            r'\.evaluacion\.id\b': '.evaluacion.evaluacion_id',
            r'\.pregunta\.id\b': '.pregunta.pregunta_id',
            r'\.intento\.id\b': '.intento.intento_id',
        }
        
        for wrong, correct in id_fixes.items():
            new_content = re.sub(wrong, correct, content)
            if new_content != content:
                fixes += 1
                content = new_content
        
        # 3. Corregir campos incorrectos
        field_fixes = {
            r'\bestado_intento\b': 'estado',
            r'\brevisado_por_id\b': 'calificador_id',
            r'\badministrador_id\b(?=.*Curso)': 'coordinador_id',
        }
        
        for wrong, correct in field_fixes.items():
            new_content = re.sub(wrong, correct, content)
            if new_content != content:
                fixes += 1
                content = new_content
        
        # 4. Corregir enums
        enum_fixes = {
            'TipoEvaluacion.EXAMEN': 'TipoEvaluacion.EXAMEN_FINAL',
            'EstadoEvaluacion.PUBLICADO': 'EstadoEvaluacion.ACTIVA',
            'EstadoEvaluacion.PUBLICADA': 'EstadoEvaluacion.ACTIVA',
        }
        
        for wrong, correct in enum_fixes.items():
            if wrong in content:
                content = content.replace(wrong, correct)
                fixes += 1
        
        # 5. Eliminar argumentos duplicados
        # Buscar patrones como evaluacion_id=uuid4(), seguido de evaluacion_id=...
        pattern = r'(\w+)\(([^)]*evaluacion_id\s*=\s*uuid4\(\)\s*,\s*evaluacion_id\s*=[^,)]+)'
        matches = list(re.finditer(pattern, content))
        for match in reversed(matches):  # Reverse para no afectar posiciones
            # Eliminar la primera evaluacion_id=uuid4(),
            fixed = re.sub(r'evaluacion_id\s*=\s*uuid4\(\)\s*,\s*', '', match.group(2))
            content = content[:match.start(2)] + fixed + content[match.end(2):]
            fixes += 1
        
        # 6. Corregir métodos que no existen
        method_fixes = {
            '.buscar_evaluaciones(': '.listar_evaluaciones(',
        }
        
        for wrong, correct in method_fixes.items():
            if wrong in content:
                content = content.replace(wrong, correct)
                fixes += 1
        
        # Guardar si hubo cambios
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  ✅ {fixes} correcciones aplicadas")
            return fixes
        else:
            print(f"  ℹ️  Sin cambios necesarios")
            return 0
    
    def verify_syntax(self, file_path: Path) -> List[str]:
        """Verifica sintaxis de Python"""
        try:
            with open(file_path, 'r') as f:
                ast.parse(f.read())
            return []
        except SyntaxError as e:
            return [f"Línea {e.lineno}: {e.msg}"]
    
    def run_analysis(self):
        """Ejecuta análisis completo"""
        print("="*70)
        print("🚀 ANÁLISIS Y CORRECCIÓN EXHAUSTIVA DE TESTS")
        print("="*70)
        
        test_files = [
            'TEST/test_calificacion_service.py',
            'TEST/test_evaluacion_service.py',
            'TEST/test_intento_service.py',
            'TEST/test_puntos_integration.py',
        ]
        
        total_fixes = 0
        
        # Fase 1: Análisis
        print("\n📊 FASE 1: ANÁLISIS")
        print("-"*70)
        
        all_issues = {}
        for test_file in test_files:
            file_path = self.base_path / test_file
            if file_path.exists():
                issues = self.analyze_test_file(file_path)
                all_issues[test_file] = issues
                
                # Mostrar resumen
                total_issues = sum(len(v) for v in issues.values())
                if total_issues > 0:
                    print(f"  ⚠️  {total_issues} problemas detectados")
        
        # Fase 2: Corrección
        print("\n🔧 FASE 2: CORRECCIÓN AUTOMÁTICA")
        print("-"*70)
        
        for test_file in test_files:
            file_path = self.base_path / test_file
            if file_path.exists():
                fixes = self.fix_test_file(file_path)
                total_fixes += fixes
        
        # Fase 3: Verificación
        print("\n✅ FASE 3: VERIFICACIÓN DE SINTAXIS")
        print("-"*70)
        
        errors_found = False
        for test_file in test_files:
            file_path = self.base_path / test_file
            if file_path.exists():
                errors = self.verify_syntax(file_path)
                if errors:
                    print(f"\n❌ {test_file}:")
                    for error in errors:
                        print(f"  {error}")
                    errors_found = True
                else:
                    print(f"  ✅ {file_path.name}: Sintaxis correcta")
        
        # Resumen final
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        print(f"  Total de correcciones aplicadas: {total_fixes}")
        print(f"  Estado de sintaxis: {'❌ ERRORES' if errors_found else '✅ TODO OK'}")
        print("="*70)
        
        return total_fixes


def main():
    analyzer = TestAnalyzer()
    analyzer.run_analysis()
    
    print("\n💡 Siguiente paso: Ejecutar pytest para ver resultados")
    print("   venv/bin/python -m pytest TEST/ -v --tb=no -q")


if __name__ == "__main__":
    main()
