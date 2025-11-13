#!/usr/bin/env python3
"""
Script de auditoría completa de la estructura del proyecto Acadify.
Analiza routes, services, crud y models para identificar problemas estructurales.
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class ProjectAuditor:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.routes_path = self.backend_path / "src" / "api" / "routes"
        self.services_path = self.backend_path / "src" / "services"
        self.crud_path = self.backend_path / "src" / "crud"
        self.models_path = self.backend_path / "src" / "models"
        
        self.issues = defaultdict(list)
        self.stats = defaultdict(int)
        
    def analyze_file(self, file_path: Path) -> Dict:
        """Analiza un archivo Python y extrae información clave"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
            info = {
                'imports': [],
                'functions': [],
                'classes': [],
                'routes': [],
                'db_queries': [],
                'has_crud_logic': False,
                'has_business_logic': False,
                'lines': len(content.split('\n'))
            }
            
            for node in ast.walk(tree):
                # Imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        info['imports'].append(module)
                        
                        # Detectar imports de CRUD en routes
                        if 'crud' in module and 'routes' in str(file_path):
                            info['has_crud_logic'] = True
                        
                        # Detectar imports de DB en services
                        if any(x in module for x in ['sqlalchemy', 'Session', 'db.session']) and 'services' in str(file_path):
                            info['db_queries'].append(f"Import DB: {module}")
                
                # Funciones
                elif isinstance(node, ast.FunctionDef):
                    info['functions'].append(node.name)
                    
                    # Detectar decoradores de rutas
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Attribute):
                            if decorator.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                info['routes'].append(node.name)
                        elif isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Attribute):
                                if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                    info['routes'].append(node.name)
                
                # Clases
                elif isinstance(node, ast.ClassDef):
                    info['classes'].append(node.name)
            
            # Detectar queries directas en código
            if re.search(r'db\.query\(|session\.query\(|\.filter\(|\.all\(\)|\.first\(\)', content):
                info['db_queries'].append("Direct DB query detected")
            
            # Detectar lógica de negocio compleja
            if re.search(r'(if|for|while).{20,}|try:.{50,}except', content, re.DOTALL):
                info['has_business_logic'] = True
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def audit_routes(self):
        """Audita la carpeta de routes"""
        print("\n" + "="*80)
        print("📂 AUDITANDO API/ROUTES")
        print("="*80)
        
        routes_files = list(self.routes_path.rglob("*.py"))
        
        # Archivos que deberían estar en módulos
        root_files = [f for f in routes_files if f.parent == self.routes_path and f.name != "__init__.py"]
        
        if root_files:
            print(f"\n⚠️  ARCHIVOS FUERA DE MÓDULOS EN routes/ ({len(root_files)}):")
            for file in root_files:
                print(f"   - {file.name}")
                self.issues['routes_misplaced'].append(str(file.relative_to(self.backend_path)))
        
        # Analizar cada archivo de ruta
        routes_with_crud = []
        routes_with_db = []
        large_routes = []
        
        for file in routes_files:
            if file.name == "__init__.py":
                continue
                
            info = self.analyze_file(file)
            if 'error' in info:
                continue
            
            # Rutas con lógica de CRUD directa
            if info['has_crud_logic'] or 'db.query' in str(info['db_queries']):
                routes_with_crud.append(file.relative_to(self.backend_path))
                self.issues['routes_with_crud'].append(str(file.relative_to(self.backend_path)))
            
            # Rutas con queries directas
            if info['db_queries']:
                routes_with_db.append(file.relative_to(self.backend_path))
                self.issues['routes_with_db'].append(str(file.relative_to(self.backend_path)))
            
            # Rutas muy grandes (>500 líneas)
            if info['lines'] > 500:
                large_routes.append((file.relative_to(self.backend_path), info['lines']))
                self.issues['large_routes'].append(f"{file.relative_to(self.backend_path)} ({info['lines']} lines)")
        
        if routes_with_crud:
            print(f"\n⚠️  RUTAS CON LÓGICA CRUD DIRECTA ({len(routes_with_crud)}):")
            for route in routes_with_crud[:5]:
                print(f"   - {route}")
            if len(routes_with_crud) > 5:
                print(f"   ... y {len(routes_with_crud) - 5} más")
        
        if large_routes:
            print(f"\n⚠️  RUTAS MUY GRANDES ({len(large_routes)}):")
            for route, lines in large_routes:
                print(f"   - {route}: {lines} líneas")
        
        self.stats['total_routes'] = len(routes_files)
        self.stats['misplaced_routes'] = len(root_files)
        self.stats['routes_with_crud'] = len(routes_with_crud)
        self.stats['large_routes'] = len(large_routes)
    
    def audit_services(self):
        """Audita la carpeta de services"""
        print("\n" + "="*80)
        print("📂 AUDITANDO SERVICES")
        print("="*80)
        
        if not self.services_path.exists():
            print("❌ Carpeta services no encontrada")
            return
        
        services_files = list(self.services_path.rglob("*.py"))
        services_with_db = []
        services_without_crud = []
        
        for file in services_files:
            if file.name == "__init__.py":
                continue
            
            info = self.analyze_file(file)
            if 'error' in info:
                continue
            
            # Services con queries directas (deberían usar CRUD)
            if info['db_queries']:
                services_with_db.append(file.relative_to(self.backend_path))
                self.issues['services_with_db'].append(str(file.relative_to(self.backend_path)))
            
            # Services sin imports de CRUD (posible problema)
            has_crud_import = any('crud' in imp for imp in info['imports'])
            if not has_crud_import and len(info['functions']) > 2:
                services_without_crud.append(file.relative_to(self.backend_path))
        
        if services_with_db:
            print(f"\n⚠️  SERVICES CON QUERIES DIRECTAS ({len(services_with_db)}):")
            for service in services_with_db[:5]:
                print(f"   - {service}")
            if len(services_with_db) > 5:
                print(f"   ... y {len(services_with_db) - 5} más")
        
        if services_without_crud:
            print(f"\n💡 SERVICES SIN IMPORTS DE CRUD ({len(services_without_crud)}):")
            for service in services_without_crud[:3]:
                print(f"   - {service}")
        
        self.stats['total_services'] = len(services_files)
        self.stats['services_with_db'] = len(services_with_db)
    
    def audit_crud(self):
        """Audita la carpeta de CRUD"""
        print("\n" + "="*80)
        print("📂 AUDITANDO CRUD")
        print("="*80)
        
        if not self.crud_path.exists():
            print("❌ Carpeta crud no encontrada")
            return
        
        crud_files = list(self.crud_path.rglob("*.py"))
        crud_with_business_logic = []
        
        for file in crud_files:
            if file.name == "__init__.py":
                continue
            
            info = self.analyze_file(file)
            if 'error' in info:
                continue
            
            # CRUD con lógica de negocio compleja (debería estar en services)
            if info['has_business_logic']:
                crud_with_business_logic.append(file.relative_to(self.backend_path))
                self.issues['crud_with_logic'].append(str(file.relative_to(self.backend_path)))
        
        if crud_with_business_logic:
            print(f"\n⚠️  CRUD CON LÓGICA DE NEGOCIO ({len(crud_with_business_logic)}):")
            for crud in crud_with_business_logic[:5]:
                print(f"   - {crud}")
        
        self.stats['total_crud'] = len(crud_files)
        self.stats['crud_with_logic'] = len(crud_with_business_logic)
    
    def generate_report(self):
        """Genera reporte final"""
        print("\n" + "="*80)
        print("📊 RESUMEN DE AUDITORÍA")
        print("="*80)
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   - Total de rutas: {self.stats['total_routes']}")
        print(f"   - Total de services: {self.stats['total_services']}")
        print(f"   - Total de CRUD: {self.stats['total_crud']}")
        
        print(f"\n⚠️  PROBLEMAS ENCONTRADOS:")
        print(f"   - Archivos fuera de módulos: {self.stats['misplaced_routes']}")
        print(f"   - Rutas con lógica CRUD: {self.stats['routes_with_crud']}")
        print(f"   - Rutas muy grandes (>500 líneas): {self.stats['large_routes']}")
        print(f"   - Services con queries directas: {self.stats['services_with_db']}")
        print(f"   - CRUD con lógica de negocio: {self.stats['crud_with_logic']}")
        
        total_issues = sum([
            self.stats['misplaced_routes'],
            self.stats['routes_with_crud'],
            self.stats['large_routes'],
            self.stats['services_with_db'],
            self.stats['crud_with_logic']
        ])
        
        print(f"\n📌 TOTAL DE PROBLEMAS: {total_issues}")
        
        # Prioridades de refactorización
        print(f"\n🎯 PRIORIDADES DE REFACTORIZACIÓN:")
        if self.stats['misplaced_routes'] > 0:
            print(f"   1. ALTA: Organizar {self.stats['misplaced_routes']} archivos fuera de módulos")
        if self.stats['routes_with_crud'] > 0:
            print(f"   2. ALTA: Mover lógica CRUD de rutas a services")
        if self.stats['services_with_db'] > 0:
            print(f"   3. MEDIA: Refactorizar {self.stats['services_with_db']} services para usar CRUD")
        if self.stats['large_routes'] > 0:
            print(f"   4. MEDIA: Dividir {self.stats['large_routes']} rutas grandes")
        if self.stats['crud_with_logic'] > 0:
            print(f"   5. BAJA: Mover lógica de negocio de CRUD a services")
        
        return self.issues

def main():
    print("\n" + "="*80)
    print("🔍 AUDITORÍA DE ESTRUCTURA DEL PROYECTO ACADIFY")
    print("="*80)
    
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    
    auditor = ProjectAuditor(backend_path)
    
    auditor.audit_routes()
    auditor.audit_services()
    auditor.audit_crud()
    
    issues = auditor.generate_report()
    
    # Guardar reporte detallado
    report_path = Path(backend_path) / "audit_report.json"
    import json
    with open(report_path, 'w') as f:
        json.dump({
            'issues': dict(issues),
            'stats': dict(auditor.stats)
        }, f, indent=2)
    
    print(f"\n💾 Reporte detallado guardado en: {report_path}")
    print("\n✅ Auditoría completada")

if __name__ == "__main__":
    main()
