"""
Script para analizar los 79 campos faltantes y categorizarlos.

Ayuda a decidir qué campos:
- Deben agregarse a BD (funcionalidad legítima)
- Deben eliminarse de modelos (obsoletos/no usados)
- Necesitan investigación adicional
"""

import asyncio
import asyncpg
from collections import defaultdict
from pathlib import Path
import re
from typing import Dict, List, Set

from src.core.config import settings


# Categorías de campos según su propósito
FIELD_CATEGORIES = {
    # Campos de auditoría estándar (probablemente legítimos)
    'audit': ['fecha_creacion', 'fecha_actualizacion', 'fecha_modificacion', 
              'creado_por', 'actualizado_por', 'creado_por_id', 'modificado_por_id'],
    
    # Campos de estado/control (probablemente legítimos)
    'status': ['estado', 'es_activa', 'esta_activa', 'activa', 'es_activo'],
    
    # Campos de código de acceso (feature específico)
    'access_code': ['codigo_acceso', 'estado_codigo', 'fecha_vencimiento_codigo'],
    
    # Campos de Google Drive sync (feature específico)
    'google_drive': ['google_drive_id', 'google_drive_url', 'sincronizado_drive', 
                     'fecha_ultima_sync'],
    
    # Campos de versionado (feature específico)
    'versioning': ['version', 'es_version_actual', 'material_original_id'],
    
    # Campos de notificaciones (feature específico)
    'notifications': ['notificaciones_activas', 'mensajes_importantes', 'menciones',
                     'menciones_email', 'urgentes_email', 'resumen_diario_email',
                     'dias_activos', 'horario_inicio', 'horario_fin'],
    
    # Campos de chat avanzado (feature específico)
    'chat_advanced': ['es_respuesta', 'total_respuestas', 'datos_adjuntos',
                     'es_moderador', 'es_admin', 'sonido_activo', 'mensajes_no_leidos',
                     'requiere_aprobacion', 'max_participantes', 'total_mensajes',
                     'configuracion'],
    
    # Campos de tareas (feature específico)
    'tasks': ['tipo_tarea', 'categoria', 'fecha_pre_inscripcion'],
}


class FieldAnalyzer:
    def __init__(self):
        self.conn = None
        self.missing_fields_by_table = defaultdict(list)
        
    async def connect(self):
        """Conectar a PostgreSQL"""
        db_url = settings.get_database_url(async_driver=False)
        self.conn = await asyncpg.connect(db_url)
    
    async def close(self):
        """Cerrar conexión"""
        if self.conn:
            await self.conn.close()
    
    def categorize_field(self, field_name: str) -> str:
        """Categoriza un campo según su nombre"""
        for category, patterns in FIELD_CATEGORIES.items():
            if field_name in patterns:
                return category
        return 'other'
    
    def analyze_field_usage(self, model_file: Path, field_name: str) -> Dict:
        """
        Analiza si un campo se usa en el código.
        
        Returns:
            Dict con información de uso del campo
        """
        usage_info = {
            'found_in_code': False,
            'locations': [],
            'category': self.categorize_field(field_name)
        }
        
        # Buscar en CRUD, schemas, routes
        search_paths = [
            Path('src/crud'),
            Path('src/schemas'),
            Path('src/api/routes'),
            Path('src/services'),
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for py_file in search_path.rglob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    # Buscar referencias al campo (nombre exacto o en dot notation)
                    if re.search(rf'\b{field_name}\b', content):
                        usage_info['found_in_code'] = True
                        usage_info['locations'].append(str(py_file.relative_to(Path.cwd())))
                except:
                    pass
        
        return usage_info
    
    async def get_table_columns(self, table_name: str) -> Set[str]:
        """Obtiene columnas de una tabla (case-insensitive)"""
        # Intentar con nombre exacto y en minúsculas
        for name_variant in [table_name, table_name.lower()]:
            columns = await self.conn.fetch("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = $1
                ORDER BY ordinal_position
            """, name_variant)
            
            if columns:
                return {row['column_name'] for row in columns}
        
        return set()
    
    def get_model_fields(self, model_file: Path) -> Set[str]:
        """Extrae nombres de campos de un modelo"""
        try:
            content = model_file.read_text(encoding='utf-8')
            # Buscar definiciones de columnas
            matches = re.findall(r'(\w+)\s*=\s*Column\(', content)
            return set(matches)
        except:
            return set()
    
    async def analyze_table(self, model_file: Path, table_name: str):
        """Analiza una tabla específica"""
        db_columns = await self.get_table_columns(table_name)
        if not db_columns:
            print(f"⚠️  Tabla '{table_name}' no encontrada en BD")
            return
        
        model_fields = self.get_model_fields(model_file)
        missing_in_db = model_fields - db_columns
        
        if not missing_in_db:
            return
        
        print(f"\n{'='*70}")
        print(f"📋 Tabla: {table_name} ({len(missing_in_db)} campos faltantes)")
        print(f"{'='*70}")
        
        # Analizar cada campo faltante
        for field in sorted(missing_in_db):
            usage = self.analyze_field_usage(model_file, field)
            
            self.missing_fields_by_table[table_name].append({
                'field': field,
                'category': usage['category'],
                'used_in_code': usage['found_in_code'],
                'locations': usage['locations']
            })
            
            # Imprimir análisis
            category_icon = {
                'audit': '📝',
                'status': '🔄',
                'access_code': '🔐',
                'google_drive': '☁️',
                'versioning': '📦',
                'notifications': '🔔',
                'chat_advanced': '💬',
                'tasks': '✅',
                'other': '❓'
            }
            
            icon = category_icon.get(usage['category'], '❓')
            used_marker = '✓ USADO' if usage['found_in_code'] else '✗ No usado'
            
            print(f"  {icon} {field}")
            print(f"     Categoría: {usage['category']}")
            print(f"     {used_marker}")
            if usage['locations']:
                print(f"     Ubicaciones: {', '.join(usage['locations'][:3])}")
    
    async def generate_report(self):
        """Genera reporte final con recomendaciones"""
        print("\n\n" + "="*70)
        print("📊 REPORTE DE ANÁLISIS")
        print("="*70)
        
        # Agrupar por categoría
        by_category = defaultdict(list)
        for table, fields in self.missing_fields_by_table.items():
            for field_info in fields:
                by_category[field_info['category']].append({
                    'table': table,
                    **field_info
                })
        
        # Recomendaciones por categoría
        recommendations = {
            'audit': '✅ AGREGAR - Campos de auditoría estándar',
            'status': '✅ AGREGAR - Campos de control de estado',
            'access_code': '🔍 REVISAR - Feature de código de acceso para clases',
            'google_drive': '🔍 REVISAR - Integración con Google Drive',
            'versioning': '🔍 REVISAR - Sistema de versionado de materiales',
            'notifications': '🔍 REVISAR - Sistema de notificaciones avanzado',
            'chat_advanced': '🔍 REVISAR - Features avanzados de chat',
            'tasks': '✅ AGREGAR - Campos básicos de tareas',
            'other': '❓ INVESTIGAR - Campos sin categoría clara',
        }
        
        for category, fields_list in sorted(by_category.items()):
            used_count = sum(1 for f in fields_list if f['used_in_code'])
            total_count = len(fields_list)
            
            print(f"\n{category.upper()}: {total_count} campos")
            print(f"  Recomendación: {recommendations.get(category, '❓ INVESTIGAR')}")
            print(f"  Usados en código: {used_count}/{total_count}")
            
            # Mostrar algunos ejemplos
            if total_count <= 5:
                for field_info in fields_list:
                    used = '✓' if field_info['used_in_code'] else '✗'
                    print(f"    {used} {field_info['table']}.{field_info['field']}")
        
        print("\n" + "="*70)
        print("💡 RECOMENDACIONES FINALES")
        print("="*70)
        print("\n1. AGREGAR A BD (via migración):")
        print("   - Todos los campos 'audit' y 'status'")
        print("   - Campos 'tasks' básicos")
        print("   - Campos usados en código de otras categorías")
        
        print("\n2. ELIMINAR DE MODELOS:")
        print("   - Campos 'other' no usados en código")
        print("   - Features completos no implementados (si no se van a usar)")
        
        print("\n3. INVESTIGAR:")
        print("   - Features parcialmente implementados")
        print("   - Campos con uso ambiguo")


async def main():
    analyzer = FieldAnalyzer()
    await analyzer.connect()
    
    # Tablas problemáticas identificadas en el último reporte
    problem_tables = {
        'Clase': Path('src/models/academic/clase.py'),
        'MaterialEducativo': Path('src/models/academic/material_educativo.py'),
        'configuracion_notificaciones': Path('src/models/communication/chat.py'),
        'mensajes': Path('src/models/communication/chat.py'),
        'notificaciones': Path('src/models/communication/chat.py'),
        'participantes_sala': Path('src/models/communication/chat.py'),
        'salas_chat': Path('src/models/communication/chat.py'),
        'tareas': Path('src/models/classes/tarea.py'),
        'rubricas': Path('src/models/academic/tarea.py'),
    }
    
    print("🔍 Analizando campos faltantes...")
    
    for table_name, model_file in problem_tables.items():
        if model_file.exists():
            await analyzer.analyze_table(model_file, table_name)
    
    await analyzer.generate_report()
    await analyzer.close()


if __name__ == "__main__":
    asyncio.run(main())
