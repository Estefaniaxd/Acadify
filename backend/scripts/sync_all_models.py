#!/usr/bin/env python3
"""
Script para sincronizar TODOS los modelos importantes con BD
"""
import os
import re
from sqlalchemy import create_engine, inspect
from src.core.config import settings

# Mapeo de tablas a archivos de modelo (rutas corregidas)
TABLE_MODEL_MAP = {
    # Ya sincronizados ✅
    'Clase': ('src/models/academic/clase.py', True),
    'Curso': ('src/models/academic/curso.py', True),
    'Grupo': ('src/models/academic/grupo.py', True),
    'Programa': ('src/models/academic/programa.py', True),
    'Institucion': ('src/models/academic/institucion.py', True),
    'MaterialEducativo': ('src/models/academic/material_educativo.py', True),
    'tareas': ('src/models/academic/tarea.py', True),
    'mensajes': ('src/models/communication/mensaje.py', True),
    'racha_usuario': ('src/models/gamification/racha_usuario.py', True),
    'inscripciones': ('src/models/academic/inscripcion.py', True),
    'periodos_academicos': ('src/models/academic/periodo_academico.py', True),
    'inventario_usuario': ('src/models/gamification/inventario_usuario.py', True),
    'etiquetas_perfil': ('src/models/gamification/etiqueta_perfil.py', True),
    
    # Pendientes de sincronizar (rutas corregidas)
    'Usuario': ('src/models/users/usuario.py', False),
    'evaluaciones': ('src/models/evaluaciones/examen.py', False),  # Se llama examen.py
    'preguntas_evaluacion': ('src/models/evaluaciones/intento_respuesta_gamificacion.py', False),  # Integrado
    'intentos_evaluacion': ('src/models/evaluaciones/intento_respuesta_gamificacion.py', False),  # Integrado
    'respuestas_estudiante': ('src/models/evaluaciones/intento_respuesta_gamificacion.py', False),  # Integrado
    'configuraciones_antitrampa': ('src/models/evaluaciones/configuracion_antitrampa.py', False),
    'salas_chat': ('src/models/communication/chat.py', False),  # Se llama chat.py
    'notificaciones': ('src/models/communication/mensaje.py', False),  # Integrado en mensaje
    'participantes_sala': ('src/models/communication/chat.py', False),  # Integrado en chat
    'videollamadas': ('src/models/communication/videollamada.py', False),
    'tienda_item': ('src/models/gamification/tienda_item.py', False),
    'recompensa_racha': ('src/models/gamification/recompensa_racha.py', False),
}

def get_model_columns(file_path):
    """Extrae columnas del archivo de modelo"""
    if not os.path.exists(file_path):
        return set()
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    pattern = r'(\w+)\s*=\s*Column\('
    return set(re.findall(pattern, content))

def main():
    engine = create_engine(settings.DATABASE_URL)
    inspector = inspect(engine)
    
    print('='*80)
    print('📊 SINCRONIZACIÓN COMPLETA DE MODELOS')
    print('='*80)
    print()
    
    sincronizados = []
    pendientes = []
    no_encontrados = []
    
    for table_name, (model_file, is_synced) in sorted(TABLE_MODEL_MAP.items()):
        try:
            bd_cols = len(inspector.get_columns(table_name))
        except:
            continue
        
        if os.path.exists(model_file):
            model_cols = len(get_model_columns(model_file))
            diff = abs(bd_cols - model_cols)
            
            if is_synced and diff == 0:
                sincronizados.append((table_name, bd_cols, model_cols))
                print(f'✅ {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3}')
            elif is_synced and diff > 0:
                print(f'⚠️  {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Diff: {diff:3}')
            else:
                pendientes.append((table_name, bd_cols, model_cols, diff))
                if diff > 10:
                    print(f'🔴 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Diff: {diff:3}')
                elif diff > 5:
                    print(f'🟡 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Diff: {diff:3}')
                else:
                    print(f'🟢 {table_name:30} BD: {bd_cols:3} | Modelo: {model_cols:3} | Diff: {diff:3}')
        else:
            no_encontrados.append((table_name, bd_cols, model_file))
            print(f'❌ {table_name:30} BD: {bd_cols:3} | Modelo: NO ENCONTRADO')
    
    print()
    print('='*80)
    print('📈 RESUMEN')
    print('='*80)
    print(f'✅ Sincronizados:    {len(sincronizados)} modelos')
    print(f'🔴 Pendientes:       {len(pendientes)} modelos')
    print(f'❌ No encontrados:   {len(no_encontrados)} modelos')
    print()
    
    if pendientes:
        print('🎯 PRIORIDAD DE SINCRONIZACIÓN:')
        print('-'*80)
        print()
        
        # Ordenar por diferencia (mayor primero)
        pendientes_sorted = sorted(pendientes, key=lambda x: x[3], reverse=True)
        
        criticos = [p for p in pendientes_sorted if p[3] > 20]
        importantes = [p for p in pendientes_sorted if 10 < p[3] <= 20]
        menores = [p for p in pendientes_sorted if p[3] <= 10]
        
        if criticos:
            print('🔴 CRÍTICOS (>20 campos de diferencia):')
            for tabla, bd, modelo, diff in criticos:
                print(f'   • {tabla:30} Diferencia: {diff:3} campos')
            print()
        
        if importantes:
            print('🟡 IMPORTANTES (10-20 campos):')
            for tabla, bd, modelo, diff in importantes:
                print(f'   • {tabla:30} Diferencia: {diff:3} campos')
            print()
        
        if menores:
            print('🟢 MENORES (<10 campos):')
            for tabla, bd, modelo, diff in menores:
                print(f'   • {tabla:30} Diferencia: {diff:3} campos')
    
    # Calcular columnas totales
    total_cols_synced = sum(bd for _, bd, _ in sincronizados)
    print()
    print(f'📊 Total columnas sincronizadas: {total_cols_synced}')

if __name__ == "__main__":
    main()
