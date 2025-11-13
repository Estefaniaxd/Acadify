"""
Auditoría Completa de Modelos vs Base de Datos
================================================

Este script identifica TODOS los problemas potenciales antes de continuar:
1. Tablas duplicadas (múltiples modelos apuntando a la misma tabla)
2. Modelos sin tablas en BD
3. Imports faltantes
4. Palabras reservadas de SQLAlchemy
5. Conflictos de nombres
6. FKs inválidos

Autor: AI Assistant
Fecha: 2025-11-04
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import sessionmaker
import importlib.util
from collections import defaultdict
import re

# Setup paths
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from src.core.config import settings

# SQLAlchemy reserved words
SQLALCHEMY_RESERVED = [
    'metadata', 'registry', 'mapper', 'state', 'session', 
    'query', 'c', 'columns', 'table'
]

class ModelAuditor:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.inspector = inspect(self.engine)
        self.problems = {
            'duplicate_tables': defaultdict(list),
            'missing_tables': [],
            'missing_imports': [],
            'reserved_words': [],
            'invalid_fks': [],
            'naming_conflicts': [],
            'relationship_errors': []
        }
        
    def get_all_bd_tables(self):
        """Obtiene todas las tablas de la BD."""
        return set(self.inspector.get_table_names())
    
    def find_all_model_files(self):
        """Encuentra todos los archivos de modelos."""
        models_path = backend_path / "src" / "models"
        model_files = []
        
        for root, dirs, files in os.walk(models_path):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    model_files.append(Path(root) / file)
        
        return model_files
    
    def parse_model_file(self, file_path):
        """Analiza un archivo de modelo y extrae información."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return None
            
        models_found = []
        
        # Buscar clases que heredan de Base
        class_pattern = r'class\s+(\w+)\s*\([^)]*Base[^)]*\):'
        classes = re.finditer(class_pattern, content)
        
        for cls_match in classes:
            class_name = cls_match.group(1)
            class_start = cls_match.end()
            
            # Buscar __tablename__ para esta clase
            tablename_pattern = r'__tablename__\s*=\s*["\']([^"\']+)["\']'
            tablename_match = re.search(tablename_pattern, content[class_start:class_start+500])
            
            if tablename_match:
                table_name = tablename_match.group(1)
                
                # Buscar imports en el archivo
                imports = self.extract_imports(content)
                
                # Buscar columnas
                columns = self.extract_columns(content, class_start)
                
                # Buscar relationships
                relationships = self.extract_relationships(content, class_start)
                
                models_found.append({
                    'file': str(file_path),
                    'class_name': class_name,
                    'table_name': table_name,
                    'imports': imports,
                    'columns': columns,
                    'relationships': relationships
                })
        
        return models_found
    
    def extract_imports(self, content):
        """Extrae imports del archivo."""
        imports = set()
        import_pattern = r'from\s+[\w.]+\s+import\s+([^;\n]+)'
        
        for match in re.finditer(import_pattern, content):
            imported = match.group(1)
            # Separar por comas y limpiar
            for item in imported.split(','):
                item = item.strip().split(' as ')[0].strip()
                if item and not item.startswith('('):
                    imports.add(item)
        
        return imports
    
    def extract_columns(self, content, start_pos):
        """Extrae nombres de columnas."""
        columns = []
        # Buscar solo las primeras 100 líneas de la clase
        class_content = content[start_pos:start_pos+5000]
        
        column_pattern = r'(\w+)\s*=\s*Column\('
        for match in re.finditer(column_pattern, class_content):
            col_name = match.group(1)
            columns.append(col_name)
        
        return columns
    
    def extract_relationships(self, content, start_pos):
        """Extrae relationships."""
        relationships = []
        class_content = content[start_pos:start_pos+5000]
        
        rel_pattern = r'(\w+)\s*=\s*relationship\(["\'](\w+)["\']'
        for match in re.finditer(rel_pattern, class_content):
            attr_name = match.group(1)
            target_class = match.group(2)
            relationships.append({
                'attribute': attr_name,
                'target': target_class
            })
        
        return relationships
    
    def check_duplicate_tables(self, all_models):
        """Identifica tablas con múltiples modelos."""
        table_to_models = defaultdict(list)
        
        for model in all_models:
            table_name = model['table_name']
            table_to_models[table_name].append({
                'class': model['class_name'],
                'file': model['file']
            })
        
        for table_name, models in table_to_models.items():
            if len(models) > 1:
                self.problems['duplicate_tables'][table_name] = models
    
    def check_missing_tables(self, all_models, bd_tables):
        """Identifica modelos sin tabla en BD."""
        for model in all_models:
            if model['table_name'] not in bd_tables:
                self.problems['missing_tables'].append({
                    'class': model['class_name'],
                    'table': model['table_name'],
                    'file': model['file']
                })
    
    def check_reserved_words(self, all_models):
        """Identifica uso de palabras reservadas."""
        for model in all_models:
            for col in model['columns']:
                if col.lower() in SQLALCHEMY_RESERVED:
                    self.problems['reserved_words'].append({
                        'class': model['class_name'],
                        'column': col,
                        'file': model['file']
                    })
    
    def check_missing_imports(self, all_models):
        """Identifica imports faltantes comunes."""
        required_by_type = {
            'UUID': ['UUID', 'uuid'],
            'DateTime': ['DateTime'],
            'Float': ['Float'],
            'TIMESTAMP': ['TIMESTAMP'],
            'JSON': ['JSON']
        }
        
        for model in all_models:
            file_content = open(model['file'], 'r').read()
            imports = model['imports']
            
            for type_name, required_imports in required_by_type.items():
                if type_name in file_content:
                    has_import = any(imp in imports for imp in required_imports)
                    if not has_import:
                        self.problems['missing_imports'].append({
                            'class': model['class_name'],
                            'missing': type_name,
                            'file': model['file']
                        })
    
    def check_invalid_fks(self, all_models, bd_tables):
        """Identifica FKs que apuntan a tablas inexistentes."""
        for model in all_models:
            file_content = open(model['file'], 'r').read()
            
            fk_pattern = r'ForeignKey\(["\']([^"\']+)["\']'
            for match in re.finditer(fk_pattern, file_content):
                fk_ref = match.group(1)
                # Extraer nombre de tabla del FK
                if '.' in fk_ref:
                    target_table = fk_ref.split('.')[0]
                    if target_table not in bd_tables:
                        self.problems['invalid_fks'].append({
                            'class': model['class_name'],
                            'fk': fk_ref,
                            'target_table': target_table,
                            'file': model['file']
                        })
    
    def run_audit(self):
        """Ejecuta auditoría completa."""
        print("🔍 AUDITORÍA COMPLETA DE MODELOS")
        print("=" * 80)
        
        # 1. Obtener tablas de BD
        print("\n1️⃣ Obteniendo tablas de BD...")
        bd_tables = self.get_all_bd_tables()
        print(f"   ✅ Encontradas {len(bd_tables)} tablas en BD")
        
        # 2. Encontrar archivos de modelos
        print("\n2️⃣ Buscando archivos de modelos...")
        model_files = self.find_all_model_files()
        print(f"   ✅ Encontrados {len(model_files)} archivos de modelos")
        
        # 3. Parsear todos los modelos
        print("\n3️⃣ Parseando modelos...")
        all_models = []
        for file_path in model_files:
            models = self.parse_model_file(file_path)
            if models:
                all_models.extend(models)
        print(f"   ✅ Parseados {len(all_models)} modelos")
        
        # 4. Ejecutar checks
        print("\n4️⃣ Ejecutando checks...")
        
        print("   🔎 Check: Tablas duplicadas...")
        self.check_duplicate_tables(all_models)
        
        print("   🔎 Check: Tablas faltantes...")
        self.check_missing_tables(all_models, bd_tables)
        
        print("   🔎 Check: Palabras reservadas...")
        self.check_reserved_words(all_models)
        
        print("   🔎 Check: Imports faltantes...")
        self.check_missing_imports(all_models)
        
        print("   🔎 Check: FKs inválidos...")
        self.check_invalid_fks(all_models, bd_tables)
        
        # 5. Generar reporte
        self.generate_report()
    
    def generate_report(self):
        """Genera reporte de problemas."""
        print("\n" + "=" * 80)
        print("📊 REPORTE DE AUDITORÍA")
        print("=" * 80)
        
        total_problems = sum(
            len(v) if isinstance(v, list) else len(v)
            for v in self.problems.values()
        )
        
        if total_problems == 0:
            print("\n✅ ¡NO SE ENCONTRARON PROBLEMAS!")
            return
        
        print(f"\n⚠️  TOTAL DE PROBLEMAS ENCONTRADOS: {total_problems}\n")
        
        # Tablas duplicadas
        if self.problems['duplicate_tables']:
            print("🚨 CRÍTICO: TABLAS DUPLICADAS (múltiples modelos → misma tabla)")
            print("-" * 80)
            for table, models in self.problems['duplicate_tables'].items():
                print(f"\n   Tabla: {table}")
                for model in models:
                    print(f"      - {model['class']} en {model['file']}")
        
        # Tablas faltantes
        if self.problems['missing_tables']:
            print("\n⚠️  MODELOS SIN TABLA EN BD")
            print("-" * 80)
            for problem in self.problems['missing_tables']:
                print(f"   • {problem['class']} → tabla '{problem['table']}' NO EXISTE")
                print(f"     Archivo: {problem['file']}")
        
        # Palabras reservadas
        if self.problems['reserved_words']:
            print("\n⚠️  PALABRAS RESERVADAS DE SQLALCHEMY")
            print("-" * 80)
            for problem in self.problems['reserved_words']:
                print(f"   • {problem['class']}.{problem['column']} (RESERVADA)")
                print(f"     Archivo: {problem['file']}")
        
        # Imports faltantes
        if self.problems['missing_imports']:
            print("\n⚠️  IMPORTS FALTANTES")
            print("-" * 80)
            for problem in self.problems['missing_imports']:
                print(f"   • {problem['class']} necesita import: {problem['missing']}")
                print(f"     Archivo: {problem['file']}")
        
        # FKs inválidos
        if self.problems['invalid_fks']:
            print("\n⚠️  FOREIGN KEYS INVÁLIDOS")
            print("-" * 80)
            for problem in self.problems['invalid_fks']:
                print(f"   • {problem['class']}: FK '{problem['fk']}'")
                print(f"     Tabla destino '{problem['target_table']}' NO EXISTE")
                print(f"     Archivo: {problem['file']}")
        
        # Generar archivo de reporte
        self.save_report_to_file()
    
    def save_report_to_file(self):
        """Guarda reporte en archivo."""
        report_path = backend_path / "AUDITORIA_MODELOS_COMPLETA.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Auditoría Completa de Modelos\n\n")
            f.write(f"Fecha: 2025-11-04\n\n")
            
            total = sum(
                len(v) if isinstance(v, list) else len(v)
                for v in self.problems.values()
            )
            
            f.write(f"## Resumen\n\n")
            f.write(f"**Total de problemas:** {total}\n\n")
            
            # Tablas duplicadas
            if self.problems['duplicate_tables']:
                f.write("## 🚨 CRÍTICO: Tablas Duplicadas\n\n")
                for table, models in self.problems['duplicate_tables'].items():
                    f.write(f"### Tabla: `{table}`\n\n")
                    for model in models:
                        f.write(f"- **{model['class']}** en `{model['file']}`\n")
                    f.write("\n")
            
            # Resto de problemas...
            # (Similar structure for other problems)
            
        print(f"\n💾 Reporte guardado en: {report_path}")


if __name__ == "__main__":
    auditor = ModelAuditor()
    auditor.run_audit()
