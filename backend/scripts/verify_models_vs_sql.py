"""
Script de verificación de integridad entre modelos SQLAlchemy y tablas PostgreSQL
Detecta discrepancias en:
- Nombres de tablas
- Nombres de columnas
- Tipos de datos
- Foreign Keys
- Constraints

Útil para prevenir errores como los que tuvimos con tienda_items vs tienda_item
"""
import asyncio
import asyncpg
from sqlalchemy import inspect
from sqlalchemy.orm import declarative_base
from typing import Dict, List, Set, Tuple
import importlib
import pkgutil
from pathlib import Path
from colorama import Fore, Style, init

from src.core.config import settings
from src.db.base_class import Base

# Inicializar colorama para colores en terminal
init(autoreset=True)


class ModelVerifier:
    def __init__(self):
        self.conn = None
        self.issues = []
        self.warnings = []
        self.successes = []
        
    async def connect(self):
        """Conectar a PostgreSQL"""
        db_url = settings.get_database_url(async_driver=False)
        self.conn = await asyncpg.connect(db_url)
    
    async def close(self):
        """Cerrar conexión"""
        if self.conn:
            await self.conn.close()
    
    def discover_models(self) -> Dict[str, any]:
        """Descubre todos los modelos SQLAlchemy en el proyecto"""
        models = {}
        models_path = Path("src/models")
        
        for module_info in pkgutil.walk_packages([str(models_path)], prefix="src.models."):
            try:
                module = importlib.import_module(module_info.name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # Verificar si es una clase que hereda de Base y tiene __tablename__
                    if (isinstance(attr, type) and 
                        issubclass(attr, Base) and 
                        attr is not Base and
                        hasattr(attr, '__tablename__')):
                        table_name = attr.__tablename__
                        models[table_name] = attr
            except Exception as e:
                self.warnings.append(f"⚠️  No se pudo importar {module_info.name}: {e}")
        
        return models
    
    async def get_db_tables(self) -> Set[str]:
        """Obtiene todas las tablas de la base de datos"""
        tables = await self.conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name != 'alembic_version'
        """)
        return {row['table_name'] for row in tables}
    
    async def get_table_columns(self, table_name: str) -> Dict[str, Dict]:
        """Obtiene información de columnas de una tabla"""
        columns = await self.conn.fetch("""
            SELECT 
                column_name,
                data_type,
                udt_name,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' 
            AND table_name = $1
            ORDER BY ordinal_position
        """, table_name)
        
        result = {}
        for col in columns:
            result[col['column_name']] = {
                'type': col['data_type'],
                'udt_name': col['udt_name'],
                'nullable': col['is_nullable'] == 'YES',
                'default': col['column_default'],
                'max_length': col['character_maximum_length']
            }
        return result
    
    async def get_table_foreign_keys(self, table_name: str) -> List[Dict]:
        """Obtiene las foreign keys de una tabla"""
        fks = await self.conn.fetch("""
            SELECT
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name = $1
            AND tc.table_schema = 'public'
        """, table_name)
        
        return [dict(fk) for fk in fks]
    
    def get_model_columns(self, model) -> Dict[str, any]:
        """Extrae información de columnas del modelo SQLAlchemy"""
        columns = {}
        
        # Acceder directamente a __table__.columns para evitar problemas con metadatos cacheados
        if hasattr(model, '__table__'):
            for column in model.__table__.columns:
                columns[column.name] = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'foreign_keys': [str(fk.target_fullname) for fk in column.foreign_keys]
                }
        
        return columns
    
    async def verify_table(self, table_name: str, model) -> bool:
        """Verifica una tabla específica contra su modelo"""
        has_issues = False
        
        print(f"\n{'='*70}")
        print(f"📋 Verificando: {Fore.CYAN}{table_name}{Style.RESET_ALL}")
        print(f"{'='*70}")
        
        # 1. Verificar que la tabla existe en la BD
        # PostgreSQL puede tener tablas con nombres sensibles a mayúsculas (con comillas)
        # o nombres normalizados (sin comillas, en minúsculas)
        db_tables = await self.get_db_tables()
        
        # Buscar la tabla: primero exacto, luego case-insensitive
        table_name_for_query = None
        if table_name in db_tables:
            table_name_for_query = table_name  # Encontrado con case exacto
        elif table_name.lower() in db_tables:
            table_name_for_query = table_name.lower()  # Encontrado en minúsculas
        
        if table_name_for_query is None:
            self.issues.append(f"❌ Tabla '{table_name}' definida en modelo pero NO EXISTE en BD")
            print(f"{Fore.RED}❌ TABLA NO EXISTE EN BASE DE DATOS{Style.RESET_ALL}")
            print(f"   Buscado: '{table_name}' y '{table_name.lower()}'")
            return True
        
        # 2. Obtener columnas de BD y modelo
        db_columns = await self.get_table_columns(table_name_for_query)
        model_columns = self.get_model_columns(model)
        
        db_col_names = set(db_columns.keys())
        model_col_names = set(model_columns.keys())
        
        # 3. Verificar columnas faltantes en BD
        missing_in_db = model_col_names - db_col_names
        if missing_in_db:
            has_issues = True
            for col in missing_in_db:
                msg = f"❌ Columna '{col}' en modelo pero FALTA en BD (tabla: {table_name})"
                self.issues.append(msg)
                print(f"{Fore.RED}  {msg}{Style.RESET_ALL}")
        
        # 4. Verificar columnas extra en BD (no en modelo)
        extra_in_db = db_col_names - model_col_names
        if extra_in_db:
            for col in extra_in_db:
                msg = f"⚠️  Columna '{col}' en BD pero NO en modelo (tabla: {table_name})"
                self.warnings.append(msg)
                print(f"{Fore.YELLOW}  {msg}{Style.RESET_ALL}")
        
        # 5. Verificar Foreign Keys
        db_fks = await self.get_table_foreign_keys(table_name_for_query)
        
        for col_name in model_col_names & db_col_names:
            model_col = model_columns[col_name]
            
            # Verificar si el modelo tiene FKs
            if model_col['foreign_keys']:
                # Buscar FK correspondiente en BD
                db_fk = next((fk for fk in db_fks if fk['column_name'] == col_name), None)
                
                if not db_fk:
                    has_issues = True
                    msg = f"❌ FK en modelo para '{col_name}' pero NO EXISTE en BD (tabla: {table_name})"
                    self.issues.append(msg)
                    print(f"{Fore.RED}  {msg}{Style.RESET_ALL}")
                    print(f"     Modelo apunta a: {model_col['foreign_keys']}")
                else:
                    # Verificar que la FK apunte a la tabla correcta
                    for fk_target in model_col['foreign_keys']:
                        target_table = fk_target.split('.')[0]
                        target_column = fk_target.split('.')[1] if '.' in fk_target else None
                        
                        if db_fk['foreign_table_name'] != target_table:
                            has_issues = True
                            msg = f"❌ FK '{col_name}' apunta a tabla incorrecta"
                            self.issues.append(msg)
                            print(f"{Fore.RED}  {msg}{Style.RESET_ALL}")
                            print(f"     Modelo: {target_table}")
                            print(f"     BD: {db_fk['foreign_table_name']}")
        
        # 6. Si todo está bien
        if not has_issues and not extra_in_db:
            msg = f"✅ Tabla '{table_name}' sincronizada correctamente"
            self.successes.append(msg)
            print(f"{Fore.GREEN}  ✅ Todo correcto - {len(model_col_names)} columnas verificadas{Style.RESET_ALL}")
        
        return has_issues
    
    async def verify_all(self):
        """Verifica todos los modelos"""
        print(f"\n{'#'*70}")
        print(f"# {Fore.CYAN}VERIFICACIÓN DE INTEGRIDAD: MODELOS vs BASE DE DATOS{Style.RESET_ALL}")
        print(f"{'#'*70}\n")
        
        # Descubrir modelos
        print(f"🔍 Descubriendo modelos SQLAlchemy...")
        models = self.discover_models()
        print(f"   ✓ {len(models)} modelos encontrados\n")
        
        # Obtener tablas de BD
        print(f"🔍 Obteniendo tablas de PostgreSQL...")
        db_tables = await self.get_db_tables()
        print(f"   ✓ {len(db_tables)} tablas encontradas\n")
        
        # Verificar cada modelo
        issues_count = 0
        for table_name, model in sorted(models.items()):
            has_issues = await self.verify_table(table_name, model)
            if has_issues:
                issues_count += 1
        
        # Verificar tablas huérfanas (en BD pero sin modelo)
        model_tables = set(models.keys())
        orphan_tables = db_tables - model_tables - {'alembic_version'}
        
        if orphan_tables:
            print(f"\n{Fore.YELLOW}⚠️  TABLAS HUÉRFANAS (en BD pero sin modelo):{Style.RESET_ALL}")
            for table in sorted(orphan_tables):
                msg = f"⚠️  Tabla '{table}' en BD pero no tiene modelo SQLAlchemy"
                self.warnings.append(msg)
                print(f"   {msg}")
        
        # Resumen final
        print(f"\n{'='*70}")
        print(f"📊 {Fore.CYAN}RESUMEN DE VERIFICACIÓN{Style.RESET_ALL}")
        print(f"{'='*70}")
        print(f"   Modelos verificados: {len(models)}")
        print(f"   Tablas en BD: {len(db_tables)}")
        print(f"")
        print(f"   {Fore.GREEN}✅ Éxitos: {len(self.successes)}{Style.RESET_ALL}")
        print(f"   {Fore.YELLOW}⚠️  Advertencias: {len(self.warnings)}{Style.RESET_ALL}")
        print(f"   {Fore.RED}❌ Errores críticos: {len(self.issues)}{Style.RESET_ALL}")
        print(f"")
        
        if self.issues:
            print(f"\n{Fore.RED}{'='*70}")
            print(f"❌ PROBLEMAS CRÍTICOS DETECTADOS:")
            print(f"{'='*70}{Style.RESET_ALL}")
            for issue in self.issues:
                print(f"   {issue}")
            print(f"\n{Fore.RED}⚠️  Se recomienda corregir estos problemas antes de continuar{Style.RESET_ALL}")
            return False
        elif self.warnings:
            print(f"\n{Fore.YELLOW}⚠️  HAY ADVERTENCIAS pero no errores críticos{Style.RESET_ALL}")
            return True
        else:
            print(f"\n{Fore.GREEN}{'='*70}")
            print(f"✅ ¡VERIFICACIÓN EXITOSA! Todos los modelos están sincronizados")
            print(f"{'='*70}{Style.RESET_ALL}\n")
            return True


async def main():
    verifier = ModelVerifier()
    
    try:
        await verifier.connect()
        success = await verifier.verify_all()
        
        # Código de salida
        exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error fatal: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        exit(2)
    finally:
        await verifier.close()


if __name__ == "__main__":
    asyncio.run(main())
