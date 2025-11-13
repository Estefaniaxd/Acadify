from sqlalchemy import create_engine, inspect
from src.core.config import settings
import os
import re

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)

# Tablas relacionadas con evaluaciones
tablas_eval = [
    'banco_preguntas',
    'configuracion_evaluaciones', 
    'estadisticas_examen',
    'evaluaciones',
    'intentos_evaluacion',
    'preguntas_evaluacion',
    'respuestas_estudiante'
]

# Obtener info de BD
tablas_info = {}
for tabla in tablas_eval:
    cols = inspector.get_columns(tabla)
    tablas_info[tabla] = len(cols)

# Archivos y sus clases
archivos_clases = {
    'configuracion_antitrampa.py': ['ConfiguracionAntiTrampa', 'PlantillaConfiguracion'],
    'evaluacion_expandida.py': ['Evaluacion', 'PreguntaEvaluacion'],
    'examen.py': ['Examen', 'PreguntaExamen', 'BancoPregunta', 'IntentoExamen', 
                  'RespuestaEstudiante', 'ConfiguracionEvaluaciones', 
                  'EstadisticaExamen', 'EventoAntiTrampa'],
    'intento_respuesta_gamificacion.py': ['IntentoEvaluacion', 'RespuestaEstudiante',
                                            'EventoAntiTrampa', 'RegistroPuntosEvaluacion',
                                            'InsigniaEvaluacion', 'RankingEvaluacion']
}

print("="*100)
print("🔍 MAPEO: TABLAS BD ↔️ CLASES DE MODELO")
print("="*100)
print()

# Mapeo manual basado en nombres
mapeo = {
    'evaluaciones': {
        'clases': ['Evaluacion', 'Examen'],
        'archivos': ['evaluacion_expandida.py', 'examen.py'],
        'cols_bd': tablas_info['evaluaciones'],
        'status': '❓ DUPLICADO'
    },
    'preguntas_evaluacion': {
        'clases': ['PreguntaEvaluacion', 'PreguntaExamen'],
        'archivos': ['evaluacion_expandida.py', 'examen.py'],
        'cols_bd': tablas_info['preguntas_evaluacion'],
        'status': '❓ DUPLICADO'
    },
    'intentos_evaluacion': {
        'clases': ['IntentoEvaluacion', 'IntentoExamen'],
        'archivos': ['intento_respuesta_gamificacion.py', 'examen.py'],
        'cols_bd': tablas_info['intentos_evaluacion'],
        'status': '❓ DUPLICADO'
    },
    'respuestas_estudiante': {
        'clases': ['RespuestaEstudiante (x2)'],
        'archivos': ['intento_respuesta_gamificacion.py', 'examen.py'],
        'cols_bd': tablas_info['respuestas_estudiante'],
        'status': '❓ DUPLICADO'
    },
    'banco_preguntas': {
        'clases': ['BancoPregunta'],
        'archivos': ['examen.py'],
        'cols_bd': tablas_info['banco_preguntas'],
        'status': '✅ ÚNICO'
    },
    'configuracion_evaluaciones': {
        'clases': ['ConfiguracionEvaluaciones'],
        'archivos': ['examen.py'],
        'cols_bd': tablas_info['configuracion_evaluaciones'],
        'status': '✅ ÚNICO'
    },
    'estadisticas_examen': {
        'clases': ['EstadisticaExamen'],
        'archivos': ['examen.py'],
        'cols_bd': tablas_info['estadisticas_examen'],
        'status': '✅ ÚNICO'
    }
}

for tabla, info in sorted(mapeo.items()):
    print(f"📊 {tabla.upper()} ({info['cols_bd']} cols) {info['status']}")
    print(f"   Clases:   {', '.join(info['clases'])}")
    print(f"   Archivos: {', '.join(info['archivos'])}")
    print()

print("="*100)
print("⚠️  PROBLEMA DETECTADO: DUPLICACIÓN DE MODELOS")
print("="*100)
print()
print("Hay 2 sistemas PARALELOS de evaluaciones:")
print()
print("1️⃣ SISTEMA 'examen.py' (8 clases):")
print("   • Examen, PreguntaExamen, IntentoExamen")
print("   • BancoPregunta, ConfiguracionEvaluaciones, EstadisticaExamen")
print("   • RespuestaEstudiante, EventoAntiTrampa")
print()
print("2️⃣ SISTEMA 'evaluacion_expandida.py' + 'intento_respuesta_gamificacion.py' (8 clases):")
print("   • Evaluacion, PreguntaEvaluacion")
print("   • IntentoEvaluacion, RespuestaEstudiante, EventoAntiTrampa")
print("   • RegistroPuntosEvaluacion, InsigniaEvaluacion, RankingEvaluacion")
print()
print("💡 RECOMENDACIÓN:")
print("   Debemos verificar cuál sistema se usa actualmente en las APIs")
print("   antes de hacer cambios, para no romper funcionalidad existente.")
