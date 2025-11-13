"""
Análisis final: Mapeo completo de modelos vs tablas reales
"""
from sqlalchemy import create_engine, inspect
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
inspector = inspect(engine)
tablas_bd = inspector.get_table_names()

print("="*100)
print("🔍 ANÁLISIS FINAL: Mapeo Completo Modelos ↔ Tablas BD")
print("="*100)
print()

# Definir el mapeo completo
mapeo_completo = {
    "examen.py": {
        "Examen": {"tablename": "examenes", "existe_bd": "examenes" in tablas_bd},
        "PreguntaExamen": {"tablename": "preguntas_examen", "existe_bd": "preguntas_examen" in tablas_bd},
        "BancoPregunta": {"tablename": "banco_preguntas", "existe_bd": "banco_preguntas" in tablas_bd},
        "IntentoExamen": {"tablename": "intentos_examen", "existe_bd": "intentos_examen" in tablas_bd},
        "RespuestaEstudiante": {"tablename": "respuestas_estudiante", "existe_bd": "respuestas_estudiante" in tablas_bd},
        "ConfiguracionEvaluaciones": {"tablename": "configuracion_evaluaciones", "existe_bd": "configuracion_evaluaciones" in tablas_bd},
        "EstadisticaExamen": {"tablename": "estadisticas_examen", "existe_bd": "estadisticas_examen" in tablas_bd},
        "EventoAntiTrampa": {"tablename": "eventos_anti_trampa", "existe_bd": "eventos_anti_trampa" in tablas_bd}
    },
    "evaluacion_expandida.py": {
        "Evaluacion": {"tablename": "evaluaciones", "existe_bd": "evaluaciones" in tablas_bd},
        "PreguntaEvaluacion": {"tablename": "preguntas_evaluacion", "existe_bd": "preguntas_evaluacion" in tablas_bd}
    },
    "intento_respuesta_gamificacion.py": {
        "IntentoEvaluacion": {"tablename": "intentos_evaluacion", "existe_bd": "intentos_evaluacion" in tablas_bd},
        "RespuestaEstudiante": {"tablename": "respuestas_estudiante", "existe_bd": "respuestas_estudiante" in tablas_bd},
        "EventoAntiTrampa": {"tablename": "eventos_anti_trampa", "existe_bd": "eventos_anti_trampa" in tablas_bd}
    }
}

for archivo, clases in mapeo_completo.items():
    print(f"📄 {archivo}")
    print("-"*100)
    for clase, info in clases.items():
        status = "✅" if info["existe_bd"] else "❌"
        tabla = info["tablename"]
        
        if info["existe_bd"]:
            cols = len(inspector.get_columns(tabla))
            print(f"   {status} {clase:30s} → {tabla:35s} ({cols:2d} cols)")
        else:
            print(f"   {status} {clase:30s} → {tabla:35s} (NO EXISTE)")
    print()

# Resumen
print("="*100)
print("📊 RESUMEN DE COMPATIBILIDAD")
print("="*100)
print()

print("🔴 MODELOS CON TABLAS INEXISTENTES (examen.py):")
for clase, info in mapeo_completo["examen.py"].items():
    if not info["existe_bd"]:
        print(f"   • {clase:30s} → {info['tablename']}")

print()
print("🟢 MODELOS CON TABLAS EXISTENTES (evaluacion_expandida.py + intento_respuesta_gamificacion.py):")
archivos_ok = ["evaluacion_expandida.py", "intento_respuesta_gamificacion.py"]
for archivo in archivos_ok:
    for clase, info in mapeo_completo[archivo].items():
        if info["existe_bd"]:
            print(f"   • {clase:30s} → {info['tablename']}")

print()
print("🟡 TABLAS COMPARTIDAS (ambos sistemas apuntan a la misma tabla):")
print("   • respuestas_estudiante (usada por RespuestaEstudiante en ambos)")
print("   • eventos_anti_trampa (usada por EventoAntiTrampa en ambos)")

print()
print("="*100)
print("💡 CONCLUSIÓN Y PLAN DE ACCIÓN")
print("="*100)
print()

print("✅ MODELOS A SINCRONIZAR (existen en BD):")
print()
print("   1. Evaluacion (evaluacion_expandida.py) → evaluaciones (82 cols)")
print("   2. PreguntaEvaluacion (evaluacion_expandida.py) → preguntas_evaluacion (42 cols)")
print("   3. IntentoEvaluacion (intento_respuesta_gamificacion.py) → intentos_evaluacion (68 cols)")
print("   4. RespuestaEstudiante (intento_respuesta_gamificacion.py) → respuestas_estudiante (47 cols)")
print("   5. BancoPregunta (examen.py) → banco_preguntas (33 cols)")
print("   6. ConfiguracionEvaluaciones (examen.py) → configuracion_evaluaciones (23 cols)")
print("   7. EstadisticaExamen (examen.py) → estadisticas_examen (24 cols)")
print()

print("❌ MODELOS A IGNORAR (no existen en BD):")
print()
print("   • Examen → examenes (NO EXISTE)")
print("   • PreguntaExamen → preguntas_examen (NO EXISTE)")
print("   • IntentoExamen → intentos_examen (NO EXISTE)")
print("   • EventoAntiTrampa → eventos_anti_trampa (NO EXISTE)")
print()

print("📋 ORDEN DE SINCRONIZACIÓN RECOMENDADO:")
print()
print("   Paso 1: Evaluacion (82 cols) - Modelo principal")
print("   Paso 2: PreguntaEvaluacion (42 cols) - Relacionado con Evaluacion")
print("   Paso 3: IntentoEvaluacion (68 cols) - Intentos de estudiantes")
print("   Paso 4: RespuestaEstudiante (47 cols) - Respuestas individuales")
print("   Paso 5: BancoPregunta (33 cols) - Banco de preguntas")
print("   Paso 6: ConfiguracionEvaluaciones (23 cols) - Configuración")
print("   Paso 7: EstadisticaExamen (24 cols) - Estadísticas")
print()

total_cols = 82 + 42 + 68 + 47 + 33 + 23 + 24
print(f"📊 Total: 7 modelos, {total_cols} columnas a sincronizar")
