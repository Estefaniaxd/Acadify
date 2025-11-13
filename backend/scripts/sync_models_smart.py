#!/usr/bin/env python3
"""
Script inteligente para sincronizar modelos con BD
Extrae columnas por clase específica
"""
import os
import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

# Mapeo: tabla_bd -> (archivo, clase, sincronizado)
TABLE_CLASS_MAP = {
    # ✅ Sincronizados
    'Clase': ('src/models/academic/clase.py', 'Clase', True),
    'Curso': ('src/models/academic/curso.py', 'Curso', True),
    'Grupo': ('src/models/academic/grupo.py', 'Grupo', True),
    'Programa': ('src/models/academic/programa.py', 'Programa', True),
    'Institucion': ('src/models/academic/institucion.py', 'Institucion', True),
    'MaterialEducativo': ('src/models/academic/material_educativo.py', 'MaterialEducativo', True),
    'tareas': ('src/models/academic/tarea.py', 'Tarea', True),
    'mensajes': ('src/models/communication/mensaje.py', 'Mensaje', True),
    'racha_usuario': ('src/models/gamification/racha_usuario.py', 'RachaUsuario', True),
    'inscripciones': ('src/models/academic/inscripcion.py', 'Inscripcion', True),
    'periodos_academicos': ('src/models/academic/periodo_academico.py', 'PeriodoAcademico', True),
    'inventario_usuario': ('src/models/gamification/inventario_usuario.py', 'InventarioUsuario', True),
    'etiquetas_perfil': ('src/models/gamification/etiqueta_perfil.py', 'EtiquetaPerfil', True),
    
    # 🔴 Pendientes
    'Usuario': ('src/models/users/usuario.py', 'Usuario', False),
    'evaluaciones': ('src/models/evaluaciones/examen.py', 'Examen', False),
    'intentos_evaluacion': ('src/models/evaluaciones/intento_respuesta_gamificacion.py', 'IntentoEvaluacion', False),
    'respuestas_estudiante': ('src/models/evaluaciones/intento_respuesta_gamificacion.py', 'RespuestaEstudiante', False),
    'preguntas_evaluacion': ('src/models/assessment/pregunta.py', 'Pregunta', False),
    'configuraciones_antitrampa': ('src/models/evaluaciones/configuracion_antitrampa.py', 'ConfiguracionAntiTrampa', False),
    'salas_chat': ('src/models/communication/chat.py', 'SalaChat', False),
    'participantes_sala': ('src/models/communication/chat.py', 'ParticipanteSala', False),
    'notificaciones': ('src/models/communication/chat.py', 'Notificacion', False),
    'videollamadas': ('src/models/communication/videollamada.py', 'Videollamada', False),
    'tienda_item': ('src/models/gamification/tienda_item.py', 'TiendaItem', False),
    'recompensa_racha': ('src/models/gamification/recompensa_racha.py', 'RecompensaRacha', False),
}

def get_columns_for_class(file_path, class_name):
    """Extrae columnas de una clase específica"""
    if not os.path.exists(file_path):
        return set()
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Encontrar la clase específica
    class_pattern = rf'class\s+{class_name}\s*\([^)]+\):\s*\n((?:\s+.*\n)*?)(?=\nclass\s|\Z)'
    match = re.search(class_pattern, content, re.MULTILINE)
    
    if not match:
        return set()
    
    class_content = match.group(1)
    
    # Extraer columnas
    column_pattern = r'^\s+(\w+)\s*=\s*Column\('
    columns = set(re.findall(column_pattern, class_content, re.MULTILINE))
    
    return columns

def main():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print('='*80)
    print('🎯 SINCRONIZACIÓN INTELIGENTE DE MODELOS')
    print('='*80)
    print()
    
    sincronizados = []
    criticos = []
    importantes = []
    menores = []
    errores = []
    
    for table_name, (model_file, class_name, is_synced) in sorted(TABLE_CLASS_MAP.items()):
        try:
            bd_cols_list = inspector.get_columns(table_name)
            bd_cols = len(bd_cols_list)
        except:
            continue
        
        model_cols_set = get_columns_for_class(model_file, class_name)
        model_cols = len(model_cols_set)
        diff = bd_cols - model_cols  # Diferencia: positivo = faltan campos, negativo = sobran
        
        if not os.path.exists(model_file):
            errores.append((table_name, bd_cols, model_file))
            print(f'❌ {table_name:30} BD: {bd_cols:3} | Archivo NO EXISTE')
            continue
        
        if model_cols == 0:
            errores.append((table_name, bd_cols, f"Clase {class_name} no encontrada"))
            print(f'⚠️  {table_name:30} BD: {bd_cols:3} | CLASE NO ENCONTRADA: {class_name}')
            continue
        
        if diff == 0:
            sincronizados.append((table_name, bd_cols, model_cols))
            print(f'✅ {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3}')
        elif diff > 20:
            criticos.append((table_name, bd_cols, model_cols, diff))
            print(f'🔴 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Faltan: {diff:3}')
        elif diff > 10 or diff < -10:
            importantes.append((table_name, bd_cols, model_cols, diff))
            if diff > 0:
                print(f'🟡 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Faltan: {diff:3}')
            else:
                print(f'🟡 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Sobran: {-diff:3}')
        else:
            menores.append((table_name, bd_cols, model_cols, diff))
            if diff > 0:
                print(f'🟢 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Faltan: {diff:3}')
            elif diff < 0:
                print(f'🟢 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Sobran: {-diff:3}')
            else:
                print(f'🟢 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3}')
    
    print()
    print('='*80)
    print('📊 RESUMEN')
    print('='*80)
    print(f'✅ Sincronizados:    {len(sincronizados)} modelos')
    print(f'🔴 Críticos:         {len(criticos)} modelos (>20 campos)')
    print(f'🟡 Importantes:      {len(importantes)} modelos (10-20 campos)')
    print(f'🟢 Menores:          {len(menores)} modelos (<10 campos)')
    print(f'❌ Errores:          {len(errores)} modelos')
    print()
    
    if criticos:
        print('🎯 MODELOS CRÍTICOS (requieren sincronización urgente):')
        print('-'*80)
        for tabla, bd, modelo, diff in sorted(criticos, key=lambda x: x[3], reverse=True):
            print(f'   • {tabla:30} Faltan {diff:3} campos ({bd} en BD, {modelo} en modelo)')
        print()
    
    if importantes:
        print('📋 MODELOS IMPORTANTES:')
        print('-'*80)
        for tabla, bd, modelo, diff in sorted(importantes, key=lambda x: abs(x[3]), reverse=True):
            if diff > 0:
                print(f'   • {tabla:30} Faltan {diff:3} campos')
            else:
                print(f'   • {tabla:30} Sobran {-diff:3} campos')
        print()
    
    if menores:
        print('✅ MODELOS CON AJUSTES MENORES:')
        print('-'*80)
        for tabla, bd, modelo, diff in menores:
            if diff > 0:
                print(f'   • {tabla:30} Faltan {diff:2} campos')
            elif diff < 0:
                print(f'   • {tabla:30} Sobran {-diff:2} campos')
        print()
    
    total_synced_cols = sum(bd for _, bd, _ in sincronizados)
    total_critical_missing = sum(diff for _, _, _, diff in criticos)
    
    print(f'📈 Columnas sincronizadas: {total_synced_cols}')
    print(f'🚨 Campos críticos faltantes: {total_critical_missing}')
    print()
    
    # Mostrar qué campos específicos faltan en los críticos
    if criticos:
        print('='*80)
        print('🔍 DETALLES DE CAMPOS FALTANTES EN MODELOS CRÍTICOS')
        print('='*80)
        print()
        
        for tabla, bd_cols, modelo_cols, diff in criticos[:3]:  # Top 3
            model_file, class_name, _ = TABLE_CLASS_MAP[tabla]
            
            bd_cols_list = inspector.get_columns(tabla)
            bd_col_names = {col['name'] for col in bd_cols_list}
            model_col_names = get_columns_for_class(model_file, class_name)
            
            missing = bd_col_names - model_col_names
            extra = model_col_names - bd_col_names
            
            print(f'📦 {tabla} ({class_name}):')
            print(f'   Archivo: {model_file}')
            if missing:
                print(f'   ❌ Faltan {len(missing)} campos:')
                for col in sorted(missing)[:10]:  # Max 10
                    print(f'      • {col}')
                if len(missing) > 10:
                    print(f'      ... y {len(missing) - 10} más')
            if extra:
                print(f'   ⚠️  Sobran {len(extra)} campos:')
                for col in sorted(extra)[:5]:
                    print(f'      • {col}')
            print()

if __name__ == "__main__":
    main()
