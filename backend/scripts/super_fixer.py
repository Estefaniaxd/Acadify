#!/usr/bin/env python3
"""
SUPER FIXER - Corrector Inteligente de Todos los Errores Restantes
Analiza los errores reales de pytest y los corrige automáticamente
"""
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple


class SuperFixer:
    """Corrector superinteligente que aprende de los errores"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.fixes_applied = 0
        self.model_fields = self._load_all_model_fields()
        
    def _load_all_model_fields(self) -> Dict[str, Dict[str, str]]:
        """Carga TODOS los campos de TODOS los modelos"""
        print("🔍 Analizando estructura de modelos...")
        
        models = {}
        
        # Curso
        models['Curso'] = {
            '__pk__': 'curso_id',
            'curso_id': 'UUID',
            'institucion_id': 'UUID',
            'coordinador_id': 'UUID',
            'programa_id': 'UUID',
            'nombre': 'String',
            'descripcion': 'TEXT',
            'codigo_curso': 'String',
            'codigo_acceso': 'String',
            'creditos': 'INTEGER',
            'modalidad': 'String',
            'nivel_dificultad': 'String',
            'tipo_curso': 'String',
            'categoria_curso': 'String',
            'estado': 'String',
            'fecha_inicio': 'DateTime',
            'fecha_fin': 'DateTime',
            'fecha_creacion': 'DateTime',
        }
        
        # Evaluacion
        models['Evaluacion'] = {
            '__pk__': 'evaluacion_id',
            'evaluacion_id': 'UUID',
            'curso_id': 'UUID',
            'administrador_id': 'UUID',
            'titulo': 'String',
            'descripcion': 'TEXT',
            'instrucciones': 'TEXT',
            'tipo_evaluacion': 'Enum',
            'estado': 'Enum',
            'visibilidad': 'Enum',
            'fecha_inicio': 'DateTime',
            'fecha_fin': 'DateTime',
            'fecha_creacion': 'DateTime',
            'fecha_apertura': 'DateTime',
            'fecha_cierre': 'DateTime',
            'requiere_codigo_acceso': 'Boolean',
            'codigo_acceso': 'String',
            'permitir_multiples_intentos': 'Boolean',
            'numero_intentos_permitidos': 'Integer',
            'tiene_tiempo_limite': 'Boolean',
            'tiempo_limite_minutos': 'Integer',
            'randomizar_preguntas': 'Boolean',
            'randomizar_opciones': 'Boolean',
            'mostrar_resultados_inmediatos': 'Boolean',
            'mostrar_respuestas_correctas': 'Boolean',
            'calificacion_automatica': 'Boolean',
            'puntuacion_total': 'Float',
            'puntuacion_minima_aprobacion': 'Float',
            'usar_ia_calificacion': 'Boolean',
            'generar_feedback_ia': 'Boolean',
            'detectar_plagio': 'Boolean',
            'requerir_camara': 'Boolean',
            'otorga_puntos': 'Boolean',
            'puntos_base': 'Integer',
        }
        
        # IntentoEvaluacion
        models['IntentoEvaluacion'] = {
            '__pk__': 'intento_id',
            'intento_id': 'UUID',
            'evaluacion_id': 'UUID',
            'estudiante_id': 'UUID',
            'numero_intento': 'Integer',
            'estado': 'Enum',  # NO estado_intento
            'fecha_inicio': 'DateTime',
            'fecha_fin': 'DateTime',
            'puntuacion_obtenida': 'Float',
            'puntuacion_maxima': 'Float',
            'porcentaje': 'Float',
            'aprobado': 'Boolean',
            'tiempo_total_segundos': 'Integer',
        }
        
        # PreguntaEvaluacion
        models['PreguntaEvaluacion'] = {
            '__pk__': 'pregunta_id',
            'pregunta_id': 'UUID',
            'evaluacion_id': 'UUID',
            'enunciado': 'TEXT',
            'tipo_pregunta': 'Enum',
            'opciones_respuesta': 'JSON',
            'respuesta_correcta': 'JSON',
            'puntuacion': 'Float',
            'orden': 'Integer',
            'es_obligatoria': 'Boolean',
        }
        
        # RespuestaEstudiante
        models['RespuestaEstudiante'] = {
            '__pk__': 'respuesta_id',
            'respuesta_id': 'UUID',
            'intento_id': 'UUID',
            'pregunta_id': 'UUID',
            'respuesta_estudiante': 'JSON',
            'es_correcta': 'Boolean',
            'puntuacion_obtenida': 'Float',
            'puntuacion_maxima': 'Float',
            'calificador_id': 'UUID',  # NO revisado_por_id
            'fecha_respuesta': 'DateTime',
            'tiempo_respuesta_segundos': 'Integer',
        }
        
        print(f"  ✅ {len(models)} modelos cargados")
        return models
    
    def run_tests_and_capture_errors(self) -> List[str]:
        """Ejecuta tests y captura errores reales"""
        print("\n🧪 Ejecutando tests para capturar errores...")
        
        cmd = [
            'venv/bin/python', '-m', 'pytest',
            'TEST/test_evaluacion_service.py',
            'TEST/test_intento_service.py',
            '-v', '--tb=short', '-x'  # Stop en primer error
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.base_path,
            capture_output=True,
            text=True
        )
        
        output = result.stdout + result.stderr
        
        # Extraer errores
        errors = []
        lines = output.split('\n')
        for i, line in enumerate(lines):
            if 'TypeError:' in line or 'AttributeError:' in line or 'KeyError:' in line:
                # Capturar contexto
                context = '\n'.join(lines[max(0, i-3):min(len(lines), i+3)])
                errors.append(context)
        
        print(f"  📝 {len(errors)} errores capturados")
        return errors
    
    def analyze_error(self, error_text: str) -> Dict:
        """Analiza un error y determina la solución"""
        solution = {
            'type': None,
            'file': None,
            'line': None,
            'wrong_field': None,
            'correct_field': None,
            'model': None,
        }
        
        # Extraer archivo y línea
        file_match = re.search(r'TEST/(\w+\.py):(\d+)', error_text)
        if file_match:
            solution['file'] = f"TEST/{file_match.group(1)}"
            solution['line'] = int(file_match.group(2))
        
        # Detectar tipo de error
        if "is an invalid keyword argument" in error_text:
            solution['type'] = 'invalid_keyword'
            # Extraer campo incorrecto
            match = re.search(r"'(\w+)' is an invalid keyword argument for (\w+)", error_text)
            if match:
                solution['wrong_field'] = match.group(1)
                solution['model'] = match.group(2)
                
                # Buscar campo correcto
                if solution['model'] in self.model_fields:
                    # Sugerencias comunes
                    suggestions = {
                        'codigo': 'codigo_curso',
                        'activo': 'estado',
                        'estado_intento': 'estado',
                        'revisado_por_id': 'calificador_id',
                        'id': self.model_fields[solution['model']].get('__pk__', 'id'),
                    }
                    solution['correct_field'] = suggestions.get(
                        solution['wrong_field'],
                        solution['wrong_field']
                    )
        
        elif "object has no attribute" in error_text:
            solution['type'] = 'missing_attribute'
            match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_text)
            if match:
                solution['model'] = match.group(1)
                solution['wrong_field'] = match.group(2)
        
        return solution
    
    def apply_fix(self, solution: Dict) -> bool:
        """Aplica una corrección específica"""
        if not solution['file'] or not solution['wrong_field']:
            return False
        
        file_path = self.base_path / solution['file']
        if not file_path.exists():
            return False
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        
        if solution['type'] == 'invalid_keyword':
            # Reemplazar campo incorrecto por correcto
            pattern = rf'\b{solution["wrong_field"]}\s*='
            replacement = f'{solution["correct_field"]}='
            content = re.sub(pattern, replacement, content)
        
        elif solution['type'] == 'missing_attribute':
            # Reemplazar accesos a atributos
            pattern = rf'\.{solution["wrong_field"]}\b'
            if solution['wrong_field'] == 'id' and solution['model'] in self.model_fields:
                pk = self.model_fields[solution['model']].get('__pk__', 'id')
                replacement = f'.{pk}'
                content = re.sub(pattern, replacement, content)
        
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"  ✅ Corregido: {solution['wrong_field']} → {solution['correct_field']}")
            self.fixes_applied += 1
            return True
        
        return False
    
    def fix_all_remaining_errors(self):
        """Ejecuta ciclo completo: test → analizar → corregir → repetir"""
        print("="*70)
        print("🚀 SUPER FIXER - Modo Automático Completo")
        print("="*70)
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n🔄 Iteración {iteration}/{max_iterations}")
            
            # Ejecutar tests
            errors = self.run_tests_and_capture_errors()
            
            if not errors:
                print("\n🎉 ¡No hay más errores!")
                break
            
            # Analizar primer error
            error = errors[0]
            solution = self.analyze_error(error)
            
            if solution['type']:
                print(f"\n🔍 Error detectado:")
                print(f"  Tipo: {solution['type']}")
                print(f"  Modelo: {solution['model']}")
                print(f"  Campo incorrecto: {solution['wrong_field']}")
                print(f"  Campo correcto: {solution['correct_field']}")
                
                # Aplicar corrección
                if self.apply_fix(solution):
                    print(f"  ✨ Corrección aplicada, reintentando...")
                    continue
            
            print("  ⚠️  No se pudo corregir automáticamente este error")
            print(f"\n📄 Error completo:\n{error}\n")
            break
        
        print("\n" + "="*70)
        print("📊 RESUMEN FINAL")
        print("="*70)
        print(f"  Correcciones aplicadas: {self.fixes_applied}")
        print(f"  Iteraciones: {iteration}")
        print("="*70)


def main():
    fixer = SuperFixer()
    fixer.fix_all_remaining_errors()
    
    # Ejecutar tests finales
    print("\n🧪 Ejecutando tests finales...")
    subprocess.run([
        'venv/bin/python', '-m', 'pytest',
        'TEST/test_calificacion_service.py',
        'TEST/test_evaluacion_service.py',
        'TEST/test_intento_service.py',
        '--tb=no', '-q'
    ], cwd=fixer.base_path)


if __name__ == "__main__":
    main()
