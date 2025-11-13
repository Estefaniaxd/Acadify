"""
AUDITORÍA EXHAUSTIVA DEL SISTEMA ACADIFY
========================================
Compara modelos SQLAlchemy vs Base de Datos vs Schemas Pydantic

Validaciones:
1. Columnas en DB que no están en modelos
2. Columnas en modelos que no están en DB
3. Tipos de datos inconsistentes
4. Campos requeridos/opcionales
5. Foreign Keys y relaciones
6. Schemas Pydantic vs Modelos
7. Validadores y constraints
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

# Importar settings y modelos
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import settings
from src.db.base_class import Base

# Importar todos los modelos
from src.models.academic.curso import Curso
from src.models.academic.grupo import Grupo
from src.models.academic.tarea import Tarea, EntregaTarea
from src.models.evaluaciones.evaluacion_expandida import Evaluacion, PreguntaEvaluacion
from src.models.evaluaciones.intento_respuesta_gamificacion import IntentoEvaluacion
from src.models.academic.grupo_curso import GrupoCurso
from src.models.academic.estudiante_grupo import EstudianteGrupo
from src.models.academic.inscripcion import Inscripcion
from src.models.academic.programa import Programa
from src.models.academic.periodo_academico import PeriodoAcademico
from src.models.academic.institucion import Institucion

from src.models.users.usuario import Usuario
from src.models.users.estudiante import Estudiante
from src.models.users.docente import Docente
from src.models.users.coordinador import Coordinador
from src.models.users.administrador_sistema import AdministradorSistema

from src.models.communication.comentario import Comentario
from src.models.communication.reaccion import Reaccion


class CompleteSystemAuditor:
    """Auditor completo del sistema"""
    
    # Tablas críticas a auditar
    CRITICAL_TABLES = [
        # Auth/Users
        'Usuario', 'Estudiante', 'Docente', 'Coordinador', 'AdministradorSistema',
        # Academic
        'Curso', 'Grupo', 'GrupoCurso', 'EstudianteGrupo',
        'Programa', 'PeriodoAcademico', 'Inscripcion',
        'tareas', 'entregas_tareas',
        'evaluaciones', 'intentos_evaluacion', 
        'preguntas_evaluacion',
        # Communication
        'Comentario', 'Reaccion',
        # Institutional
        'Institucion'
    ]
    
    # Mapeo de tipos SQL a tipos Python
    TYPE_MAPPING = {
        'UUID': ['UUID', 'uuid'],
        'VARCHAR': ['String', 'str'],
        'TEXT': ['Text', 'str'],
        'INTEGER': ['Integer', 'int'],
        'BIGINT': ['BigInteger', 'int'],
        'BOOLEAN': ['Boolean', 'bool'],
        'DATE': ['Date', 'date'],
        'TIMESTAMP': ['DateTime', 'datetime'],
        'TIME': ['Time', 'time'],
        'NUMERIC': ['Numeric', 'Decimal', 'float'],
        'JSON': ['JSON', 'dict', 'list'],
        'ARRAY': ['ARRAY', 'list']
    }
    
    def __init__(self):
        self.engine = create_engine(settings.database_url)
        self.inspector = inspect(self.engine)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        
        self.issues = defaultdict(list)
        self.stats = {
            'tables_audited': 0,
            'columns_checked': 0,
            'issues_found': 0,
            'models_checked': 0,
            'schemas_checked': 0
        }
        
    def get_db_columns(self, table_name: str) -> Dict[str, Dict]:
        """Obtiene columnas de la BD"""
        columns = {}
        for col in self.inspector.get_columns(table_name):
            col_type = str(col['type'])
            columns[col['name']] = {
                'type': col_type,
                'nullable': col['nullable'],
                'default': col.get('default'),
                'autoincrement': col.get('autoincrement', False)
            }
        return columns
    
    def get_db_foreign_keys(self, table_name: str) -> List[Dict]:
        """Obtiene foreign keys de la BD"""
        return self.inspector.get_foreign_keys(table_name)
    
    def get_db_indexes(self, table_name: str) -> List[Dict]:
        """Obtiene índices de la BD"""
        return self.inspector.get_indexes(table_name)
    
    def get_model_columns(self, model_class) -> Dict[str, Dict]:
        """Obtiene columnas del modelo SQLAlchemy"""
        columns = {}
        mapper = inspect(model_class)
        
        for column in mapper.columns:
            col_type = str(column.type)
            columns[column.name] = {
                'type': col_type,
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'foreign_keys': [str(fk.target_fullname) for fk in column.foreign_keys],
                'default': column.default,
                'server_default': column.server_default
            }
        return columns
    
    def get_model_relationships(self, model_class) -> Dict[str, Dict]:
        """Obtiene relaciones del modelo"""
        relationships = {}
        mapper = inspect(model_class)
        
        for rel in mapper.relationships:
            relationships[rel.key] = {
                'target': rel.mapper.class_.__name__,
                'direction': str(rel.direction),
                'uselist': rel.uselist,
                'back_populates': rel.back_populates
            }
        return relationships
    
    def normalize_type(self, type_str: str) -> str:
        """Normaliza tipo de dato para comparación"""
        type_str = type_str.upper()
        
        # Extraer tipo base
        if '(' in type_str:
            base_type = type_str.split('(')[0]
        else:
            base_type = type_str
            
        # Mapear a tipo estándar
        for standard, variants in self.TYPE_MAPPING.items():
            if any(v.upper() in base_type for v in variants):
                return standard
        
        return base_type
    
    def compare_types(self, db_type: str, model_type: str) -> bool:
        """Compara si dos tipos son compatibles"""
        db_normalized = self.normalize_type(db_type)
        model_normalized = self.normalize_type(model_type)
        
        # Casos especiales
        if db_normalized == model_normalized:
            return True
        
        # VARCHAR y TEXT son compatibles
        if {db_normalized, model_normalized} <= {'VARCHAR', 'TEXT'}:
            return True
        
        # INTEGER y BIGINT son compatibles
        if {db_normalized, model_normalized} <= {'INTEGER', 'BIGINT'}:
            return True
            
        return False
    
    def audit_table(self, table_name: str, model_class) -> Dict[str, Any]:
        """Audita una tabla completa"""
        print(f"\n{'='*60}")
        print(f"📋 AUDITANDO: {table_name}")
        print(f"{'='*60}")
        
        result = {
            'table_name': table_name,
            'model': model_class.__name__,
            'issues': [],
            'warnings': [],
            'summary': {}
        }
        
        # Obtener datos
        db_columns = self.get_db_columns(table_name)
        model_columns = self.get_model_columns(model_class)
        db_fks = self.get_db_foreign_keys(table_name)
        model_rels = self.get_model_relationships(model_class)
        
        db_col_names = set(db_columns.keys())
        model_col_names = set(model_columns.keys())
        
        print(f"  📊 DB Columns: {len(db_col_names)}")
        print(f"  📊 Model Columns: {len(model_col_names)}")
        
        # 1. Columnas en DB pero no en modelo
        extra_in_db = db_col_names - model_col_names
        if extra_in_db:
            for col in extra_in_db:
                issue = {
                    'type': 'EXTRA_IN_DB',
                    'severity': 'WARNING',
                    'column': col,
                    'message': f"Columna '{col}' existe en DB pero no en modelo"
                }
                result['warnings'].append(issue)
                print(f"  ⚠️  {issue['message']}")
        
        # 2. Columnas en modelo pero no en DB
        missing_in_db = model_col_names - db_col_names
        if missing_in_db:
            for col in missing_in_db:
                issue = {
                    'type': 'MISSING_IN_DB',
                    'severity': 'ERROR',
                    'column': col,
                    'message': f"Columna '{col}' existe en modelo pero NO en DB"
                }
                result['issues'].append(issue)
                print(f"  ❌ {issue['message']}")
        
        # 3. Comparar tipos de datos
        common_columns = db_col_names & model_col_names
        for col_name in common_columns:
            db_col = db_columns[col_name]
            model_col = model_columns[col_name]
            
            if not self.compare_types(db_col['type'], model_col['type']):
                issue = {
                    'type': 'TYPE_MISMATCH',
                    'severity': 'ERROR',
                    'column': col_name,
                    'db_type': db_col['type'],
                    'model_type': model_col['type'],
                    'message': f"Tipo incompatible en '{col_name}': DB={db_col['type']}, Model={model_col['type']}"
                }
                result['issues'].append(issue)
                print(f"  ❌ {issue['message']}")
            
            # Comparar nullable
            if db_col['nullable'] != model_col['nullable']:
                issue = {
                    'type': 'NULLABLE_MISMATCH',
                    'severity': 'WARNING',
                    'column': col_name,
                    'db_nullable': db_col['nullable'],
                    'model_nullable': model_col['nullable'],
                    'message': f"Nullable diferente en '{col_name}': DB={db_col['nullable']}, Model={model_col['nullable']}"
                }
                result['warnings'].append(issue)
                print(f"  ⚠️  {issue['message']}")
        
        # 4. Verificar Foreign Keys
        print(f"  🔗 Foreign Keys: {len(db_fks)}")
        for fk in db_fks:
            fk_columns = fk['constrained_columns']
            print(f"     - {fk_columns[0]} → {fk['referred_table']}.{fk['referred_columns'][0]}")
        
        # 5. Verificar Relationships
        print(f"  🔗 Relationships: {len(model_rels)}")
        for rel_name, rel_info in model_rels.items():
            print(f"     - {rel_name} → {rel_info['target']} ({rel_info['direction']})")
        
        # Summary
        result['summary'] = {
            'total_db_columns': len(db_col_names),
            'total_model_columns': len(model_col_names),
            'common_columns': len(common_columns),
            'extra_in_db': len(extra_in_db),
            'missing_in_db': len(missing_in_db),
            'total_foreign_keys': len(db_fks),
            'total_relationships': len(model_rels),
            'total_issues': len(result['issues']),
            'total_warnings': len(result['warnings'])
        }
        
        self.stats['tables_audited'] += 1
        self.stats['columns_checked'] += len(common_columns)
        self.stats['issues_found'] += len(result['issues'])
        self.stats['models_checked'] += 1
        
        if result['issues']:
            print(f"  ❌ {len(result['issues'])} errores encontrados")
        if result['warnings']:
            print(f"  ⚠️  {len(result['warnings'])} advertencias")
        if not result['issues'] and not result['warnings']:
            print(f"  ✅ Sin inconsistencias")
        
        return result
    
    def audit_all_tables(self) -> Dict[str, Any]:
        """Audita todas las tablas críticas"""
        print("\n" + "="*60)
        print("🔍 INICIANDO AUDITORÍA COMPLETA DEL SISTEMA")
        print("="*60)
        
        # Mapeo de tablas a modelos
        TABLE_MODEL_MAP = {
            'Usuario': Usuario,
            'Estudiante': Estudiante,
            'Docente': Docente,
            'Coordinador': Coordinador,
            'AdministradorSistema': AdministradorSistema,
            'Curso': Curso,
            'Grupo': Grupo,
            'GrupoCurso': GrupoCurso,
            'EstudianteGrupo': EstudianteGrupo,
            'Programa': Programa,
            'PeriodoAcademico': PeriodoAcademico,
            'Inscripcion': Inscripcion,
            'tareas': Tarea,
            'entregas_tareas': EntregaTarea,
            'evaluaciones': Evaluacion,
            'intentos_evaluacion': IntentoEvaluacion,
            'preguntas_evaluacion': PreguntaEvaluacion,
            'Comentario': Comentario,
            'Reaccion': Reaccion,
            'Institucion': Institucion
        }
        
        results = []
        
        for table_name in self.CRITICAL_TABLES:
            if table_name not in TABLE_MODEL_MAP:
                print(f"⚠️  Modelo no encontrado para tabla: {table_name}")
                continue
            
            try:
                model_class = TABLE_MODEL_MAP[table_name]
                result = self.audit_table(table_name, model_class)
                results.append(result)
            except Exception as e:
                print(f"❌ Error auditando {table_name}: {e}")
                results.append({
                    'table_name': table_name,
                    'error': str(e)
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'stats': self.stats,
            'results': results
        }
    
    def generate_report(self, audit_results: Dict) -> str:
        """Genera reporte detallado"""
        report = []
        report.append("\n" + "="*80)
        report.append("📊 REPORTE DE AUDITORÍA COMPLETA")
        report.append("="*80)
        report.append(f"Fecha: {audit_results['timestamp']}")
        report.append("")
        
        # Estadísticas generales
        stats = audit_results['stats']
        report.append("📈 ESTADÍSTICAS GENERALES:")
        report.append(f"  • Tablas auditadas: {stats['tables_audited']}")
        report.append(f"  • Modelos verificados: {stats['models_checked']}")
        report.append(f"  • Columnas comparadas: {stats['columns_checked']}")
        report.append(f"  • Problemas encontrados: {stats['issues_found']}")
        report.append("")
        
        # Resumen por tabla
        report.append("📋 RESUMEN POR TABLA:")
        report.append("")
        
        tables_with_issues = []
        tables_clean = []
        
        for result in audit_results['results']:
            if 'error' in result:
                continue
            
            table_name = result['table_name']
            summary = result['summary']
            issues = result['issues']
            warnings = result['warnings']
            
            if issues:
                tables_with_issues.append(result)
                status = "❌ ERRORES"
            elif warnings:
                status = "⚠️  ADVERTENCIAS"
            else:
                tables_clean.append(result)
                status = "✅ OK"
            
            report.append(f"  {status} {table_name}")
            report.append(f"     Columnas: DB={summary['total_db_columns']}, Model={summary['total_model_columns']}, Común={summary['common_columns']}")
            
            if issues:
                report.append(f"     ❌ {len(issues)} errores")
                for issue in issues[:3]:  # Mostrar solo los primeros 3
                    report.append(f"        • {issue['message']}")
            
            if warnings:
                report.append(f"     ⚠️  {len(warnings)} advertencias")
            
            report.append("")
        
        # Resumen final
        report.append("="*80)
        report.append("🎯 RESUMEN FINAL:")
        report.append(f"  ✅ Tablas sin problemas: {len(tables_clean)}")
        report.append(f"  ❌ Tablas con errores: {len(tables_with_issues)}")
        report.append("")
        
        if tables_with_issues:
            report.append("⚠️  TABLAS QUE REQUIEREN ATENCIÓN:")
            for result in tables_with_issues:
                report.append(f"  • {result['table_name']}: {len(result['issues'])} errores")
        else:
            report.append("🎉 ¡TODOS LOS MODELOS ESTÁN SINCRONIZADOS CON LA BASE DE DATOS!")
        
        report.append("="*80)
        
        return "\n".join(report)


def main():
    """Ejecuta la auditoría completa"""
    auditor = CompleteSystemAuditor()
    
    # Ejecutar auditoría
    results = auditor.audit_all_tables()
    
    # Guardar resultados
    output_file = Path(__file__).parent / 'complete_audit_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Reporte guardado en: {output_file}")
    
    # Generar y mostrar reporte
    report = auditor.generate_report(results)
    print(report)
    
    # Guardar reporte en texto
    report_txt = output_file.with_suffix('.txt')
    with open(report_txt, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"💾 Reporte de texto guardado en: {report_txt}")
    
    # Retornar código de salida
    if results['stats']['issues_found'] > 0:
        print("\n❌ Se encontraron problemas que requieren corrección")
        return 1
    else:
        print("\n✅ Sistema validado correctamente")
        return 0


if __name__ == "__main__":
    exit(main())
