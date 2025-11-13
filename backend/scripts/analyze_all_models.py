#!/usr/bin/env python3
"""
Script para analizar TODOS los modelos del sistema y detectar cuáles faltan sincronizar.
Genera reporte completo con estadísticas por sistema.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from src.db.session import engine


def get_all_tables():
    """Obtiene todas las tablas de la base de datos."""
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    return sorted(all_tables)


def categorize_tables(tables):
    """Categoriza las tablas por sistema."""
    systems = {
        'authentication': [],
        'users': [],
        'academic': [],
        'evaluation': [],
        'communication': [],
        'gamification': [],
        'avatar': [],
        'otros': []
    }
    
    for table in tables:
        table_lower = table.lower()
        
        # Authentication & Users
        if any(x in table_lower for x in ['usuario', 'user', 'rol', 'permiso', 'sesion', 'session']):
            if any(x in table_lower for x in ['avatar']):
                systems['avatar'].append(table)
            else:
                systems['users'].append(table)
        
        # Academic
        elif any(x in table_lower for x in ['institucion', 'curso', 'clase', 'materia', 'programa', 
                                            'grupo', 'asistencia', 'tarea', 'archivo', 'calificacion']):
            systems['academic'].append(table)
        
        # Evaluation
        elif any(x in table_lower for x in ['examen', 'pregunta', 'respuesta', 'evaluacion', 
                                            'banco', 'intento', 'resultado']):
            systems['evaluation'].append(table)
        
        # Communication
        elif any(x in table_lower for x in ['mensaje', 'chat', 'notificacion', 'comentario', 
                                            'reaccion', 'sala', 'participante']):
            systems['communication'].append(table)
        
        # Gamification
        elif any(x in table_lower for x in ['punto', 'insignia', 'logro', 'racha', 'recompensa',
                                            'tienda', 'item', 'inventario', 'etiqueta', 'tema',
                                            'transaccion', 'historial']):
            systems['gamification'].append(table)
        
        # Avatar
        elif any(x in table_lower for x in ['avatar']):
            systems['avatar'].append(table)
        
        # Otros
        else:
            systems['otros'].append(table)
    
    return systems


def get_table_info(table_name):
    """Obtiene información básica de una tabla."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    foreign_keys = inspector.get_foreign_keys(table_name)
    
    # Contar registros
    try:
        with engine.connect() as conn:
            # Use quoted identifiers for PostgreSQL case-sensitivity
            result = conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))
            row_count = result.scalar()
    except Exception as e:
        print(f"⚠️  Error contando registros en {table_name}: {e}")
        row_count = 0

    return {
        'table': table_name,
        'columns': len(columns),
        'foreign_keys': len(foreign_keys),
        'rows': row_count
    }
def find_model_for_table(table_name):
    """Busca si existe un modelo para una tabla."""
    # Mapeo de tablas conocidas a modelos
    known_models = {
        # Users
        'Usuario': 'Usuario',
        'Rol': 'Rol',
        'Permiso': 'Permiso',
        'UsuarioPermiso': 'UsuarioPermiso',
        'Session': 'Session',
        
        # Academic
        'Institucion': 'Institucion',
        'Programa': 'Programa',
        'Curso': 'Curso',
        'Clase': 'Clase',
        'Grupo': 'Grupo',
        'Asistencia': 'Asistencia',
        'Tarea': 'Tarea',
        'ArchivoCurso': 'ArchivoCurso',
        'CalificacionTarea': 'CalificacionTarea',
        
        # Evaluation
        'BancoPregunta': 'BancoPregunta',
        'Pregunta': 'Pregunta',
        'Examen': 'Examen',
        'ExamenPregunta': 'ExamenPregunta',
        'IntentoExamen': 'IntentoExamen',
        'RespuestaEstudiante': 'RespuestaEstudiante',
        'ResultadoExamen': 'ResultadoExamen',
        
        # Communication
        'Mensaje': 'Mensaje',
        'ChatGrupo': 'ChatGrupo',
        'SalaChat': 'SalaChat',
        'ParticipanteSala': 'ParticipanteSala',
        'Comentario': 'Comentario',
        'Notificacion': 'Notificacion',
        'ConfiguracionNotificaciones': 'ConfiguracionNotificaciones',
        'ArchivoChat': 'ArchivoChat',
        'ChatBot': 'ChatBot',
        'ReaccionMensaje': 'ReaccionMensaje',
        'Reacciones': 'Reacciones',
        
        # Gamification
        'UsuarioPuntos': 'UsuarioPuntos',
        'HistorialPuntos': 'HistorialPuntos',
        'Insignia': 'Insignia',
        'UsuarioInsignia': 'UsuarioInsignia',
        'Recompensa': 'Recompensa',
        'UsuarioRecompensa': 'UsuarioRecompensa',
        'RachaUsuario': 'RachaUsuario',
        'RecompensaRacha': 'RecompensaRacha',
        'HistorialRacha': 'HistorialRacha',
        'TiendaItem': 'TiendaItem',
        'InventarioUsuario': 'InventarioUsuario',
        'TransaccionTienda': 'TransaccionTienda',
        'EtiquetaPerfil': 'EtiquetaPerfil',
        'UsuarioEtiqueta': 'UsuarioEtiqueta',
        'Tema': 'Tema',
        'TemaPredefinido': 'TemaPredefinido',
        'TemaPersonalizado': 'TemaPersonalizado',
        
        # Avatar
        'avatar_asset': 'AvatarAsset',
        'user_avatar': 'UserAvatar',
    }
    
    return known_models.get(table_name, None)


def analyze_system(system_name, tables):
    """Analiza un sistema completo."""
    print(f"\n{'='*80}")
    print(f"SISTEMA: {system_name.upper()}")
    print(f"{'='*80}")
    
    if not tables:
        print("❌ No hay tablas en este sistema")
        return {'total': 0, 'with_model': 0, 'without_model': 0}
    
    print(f"\nTablas encontradas: {len(tables)}")
    
    with_model = []
    without_model = []
    
    for table in tables:
        info = get_table_info(table)
        model = find_model_for_table(table)
        
        status = "✅" if model else "⚠️"
        model_status = f"Modelo: {model}" if model else "❌ SIN MODELO"
        
        print(f"{status} {table:40} {info['columns']:3} campos  {info['rows']:6} registros  {model_status}")
        
        if model:
            with_model.append(table)
        else:
            without_model.append(table)
    
    print(f"\n📊 Resumen {system_name}:")
    print(f"  Con modelo: {len(with_model)}/{len(tables)} ({len(with_model)/len(tables)*100:.0f}%)")
    print(f"  Sin modelo: {len(without_model)}/{len(tables)}")
    
    if without_model:
        print(f"\n⚠️  Tablas sin modelo:")
        for table in without_model:
            print(f"    - {table}")
    
    return {
        'total': len(tables),
        'with_model': len(with_model),
        'without_model': len(without_model),
        'tables_without_model': without_model
    }


def generate_final_report(all_stats):
    """Genera reporte final consolidado."""
    print(f"\n{'='*80}")
    print("📊 REPORTE FINAL - TODOS LOS SISTEMAS")
    print(f"{'='*80}")
    
    total_tables = sum(s['total'] for s in all_stats.values())
    total_with_model = sum(s['with_model'] for s in all_stats.values())
    total_without_model = sum(s['without_model'] for s in all_stats.values())
    
    print(f"\n📈 ESTADÍSTICAS GLOBALES:")
    print(f"  Total de tablas: {total_tables}")
    print(f"  Con modelo: {total_with_model} ({total_with_model/total_tables*100:.1f}%)")
    print(f"  Sin modelo: {total_without_model} ({total_without_model/total_tables*100:.1f}%)")
    
    print(f"\n🗂️  DETALLE POR SISTEMA:")
    for system, stats in all_stats.items():
        if stats['total'] > 0:
            percentage = (stats['with_model'] / stats['total'] * 100) if stats['total'] > 0 else 0
            status = "✅" if stats['without_model'] == 0 else "⚠️"
            print(f"  {status} {system:20} {stats['with_model']:2}/{stats['total']:2} tablas  [{percentage:5.1f}%]")
    
    print(f"\n⚠️  SISTEMAS QUE NECESITAN ATENCIÓN:")
    needs_attention = {k: v for k, v in all_stats.items() if v['without_model'] > 0}
    
    if not needs_attention:
        print("  🎉 ¡TODOS LOS SISTEMAS ESTÁN COMPLETOS!")
    else:
        for system, stats in needs_attention.items():
            print(f"\n  📌 {system.upper()} ({stats['without_model']} tablas sin modelo):")
            for table in stats['tables_without_model']:
                print(f"      - {table}")
    
    print()


def main():
    """Función principal."""
    print("🔍 ANÁLISIS COMPLETO DE MODELOS DEL SISTEMA")
    print("="*80)
    
    try:
        # Obtener todas las tablas
        all_tables = get_all_tables()
        print(f"\n✅ Total de tablas en BD: {len(all_tables)}")
        
        # Categorizar tablas
        systems = categorize_tables(all_tables)
        
        # Analizar cada sistema
        all_stats = {}
        
        # Orden de análisis
        system_order = [
            'users',
            'academic', 
            'evaluation',
            'communication',
            'gamification',
            'avatar',
            'otros'
        ]
        
        for system in system_order:
            if systems[system]:
                all_stats[system] = analyze_system(system, systems[system])
        
        # Generar reporte final
        generate_final_report(all_stats)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
