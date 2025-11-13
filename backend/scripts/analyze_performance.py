#!/usr/bin/env python3
"""
Script para analizar el consumo de recursos y detectar problemas de rendimiento.
"""

import ast
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class PerformanceAnalyzer:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.issues = defaultdict(list)
        
    def analyze_file(self, file_path: Path) -> Dict:
        """Analiza un archivo en busca de problemas de rendimiento"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            issues = {
                'n_plus_1': [],
                'missing_indexes': [],
                'no_limit_queries': [],
                'missing_eager_loading': [],
                'large_loops': [],
                'blocking_operations': [],
                'memory_leaks': []
            }
            
            # N+1 queries: bucles con queries dentro
            n_plus_1_pattern = r'for\s+\w+\s+in\s+.*:\s*.*?\.query\('
            if re.search(n_plus_1_pattern, content, re.DOTALL):
                issues['n_plus_1'].append("Posible N+1 query detectado")
            
            # Queries sin límite
            if re.search(r'\.all\(\)', content) and not re.search(r'\.limit\(', content):
                issues['no_limit_queries'].append("Query sin limit() puede traer todos los registros")
            
            # Falta de eager loading
            if re.search(r'\.query\(.*\)\.all\(\)', content) and not re.search(r'\.options\(|joinedload|selectinload', content):
                issues['missing_eager_loading'].append("Falta eager loading para relaciones")
            
            # Bucles grandes sin paginación
            large_loop_pattern = r'for\s+\w+\s+in\s+.*?\.all\(\)'
            if re.search(large_loop_pattern, content):
                issues['large_loops'].append("Bucle iterando sobre .all() sin paginación")
            
            # Operaciones bloqueantes en rutas async
            if re.search(r'async\s+def', content):
                if re.search(r'time\.sleep\(|requests\.get\(|open\(', content):
                    issues['blocking_operations'].append("Operación bloqueante en función async")
            
            # Posibles memory leaks
            if re.search(r'global\s+\w+\s*=\s*\[|\{\}', content):
                issues['memory_leaks'].append("Variable global mutable puede causar memory leak")
            
            return issues
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_routes(self):
        """Analiza rutas en busca de problemas de rendimiento"""
        print("\n" + "="*80)
        print("🔍 ANALIZANDO RENDIMIENTO DE RUTAS")
        print("="*80)
        
        routes_path = self.backend_path / "src" / "api" / "routes"
        routes_files = list(routes_path.rglob("*.py"))
        
        total_issues = 0
        files_with_issues = []
        
        for file in routes_files:
            if file.name == "__init__.py":
                continue
            
            issues = self.analyze_file(file)
            if 'error' in issues:
                continue
            
            file_issues = sum(len(v) for v in issues.values() if isinstance(v, list))
            if file_issues > 0:
                total_issues += file_issues
                files_with_issues.append((file, issues, file_issues))
        
        # Ordenar por cantidad de problemas
        files_with_issues.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n⚠️  Archivos con problemas de rendimiento: {len(files_with_issues)}")
        print(f"📊 Total de problemas detectados: {total_issues}\n")
        
        # Mostrar top 10
        for file, issues, count in files_with_issues[:10]:
            print(f"\n📁 {file.relative_to(self.backend_path)} ({count} problemas):")
            for issue_type, messages in issues.items():
                if messages:
                    print(f"   ⚠️  {issue_type}: {len(messages)} ocurrencias")
                    for msg in messages[:2]:
                        print(f"      - {msg}")
        
        return files_with_issues
    
    def analyze_models(self):
        """Analiza modelos en busca de falta de índices"""
        print("\n" + "="*80)
        print("🔍 ANALIZANDO MODELOS Y ÍNDICES")
        print("="*80)
        
        models_path = self.backend_path / "src" / "models"
        model_files = list(models_path.rglob("*.py"))
        
        models_without_indexes = []
        foreign_keys_without_index = []
        
        for file in model_files:
            if file.name == "__init__.py":
                continue
            
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar ForeignKey sin index=True
                fk_pattern = r'ForeignKey\([^)]+\)'
                fk_matches = re.findall(fk_pattern, content)
                
                for fk in fk_matches:
                    if 'index=True' not in fk:
                        foreign_keys_without_index.append(f"{file.name}: {fk}")
                
                # Buscar campos usados en queries sin índice
                if 'Column' in content and '__tablename__' in content:
                    if not re.search(r'Index\(|index=True', content):
                        models_without_indexes.append(file.relative_to(self.backend_path))
                
            except Exception as e:
                continue
        
        if foreign_keys_without_index:
            print(f"\n⚠️  Foreign Keys sin índice: {len(foreign_keys_without_index)}")
            for fk in foreign_keys_without_index[:5]:
                print(f"   - {fk}")
            if len(foreign_keys_without_index) > 5:
                print(f"   ... y {len(foreign_keys_without_index) - 5} más")
        
        if models_without_indexes:
            print(f"\n💡 Modelos sin índices explícitos: {len(models_without_indexes)}")
            for model in models_without_indexes[:5]:
                print(f"   - {model}")
        
        return foreign_keys_without_index, models_without_indexes
    
    def generate_optimization_plan(self, routes_issues, fk_issues, models_issues):
        """Genera un plan de optimización"""
        print("\n" + "="*80)
        print("📋 PLAN DE OPTIMIZACIÓN")
        print("="*80)
        
        print("\n🎯 ACCIONES INMEDIATAS (Alto impacto):")
        print("   1. Agregar límites a queries .all()")
        print("   2. Implementar eager loading en relaciones")
        print("   3. Agregar índices a Foreign Keys")
        print("   4. Implementar paginación en endpoints")
        
        print("\n🔧 ACCIONES A MEDIO PLAZO:")
        print("   5. Refactorizar N+1 queries")
        print("   6. Agregar caché Redis para queries frecuentes")
        print("   7. Implementar batch loading")
        
        print("\n💡 OPTIMIZACIONES AVANZADAS:")
        print("   8. Implementar índices compuestos en búsquedas complejas")
        print("   9. Agregar connection pooling optimizado")
        print("   10. Implementar lazy loading selectivo")
        
        # Generar archivo de recomendaciones
        recommendations = {
            'routes_with_performance_issues': len(routes_issues),
            'foreign_keys_without_index': len(fk_issues),
            'models_without_indexes': len(models_issues),
            'priority_actions': [
                'Add .limit() to all .all() queries',
                'Implement eager loading with joinedload/selectinload',
                'Add indexes to all ForeignKey columns',
                'Implement pagination in large result sets',
                'Add Redis caching for frequent queries'
            ]
        }
        
        import json
        report_path = self.backend_path / "performance_report.json"
        with open(report_path, 'w') as f:
            json.dump(recommendations, f, indent=2)
        
        print(f"\n💾 Reporte guardado en: {report_path}")

def main():
    print("\n" + "="*80)
    print("⚡ ANÁLISIS DE RENDIMIENTO Y CONSUMO DE RECURSOS")
    print("="*80)
    
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    analyzer = PerformanceAnalyzer(backend_path)
    
    routes_issues = analyzer.analyze_routes()
    fk_issues, models_issues = analyzer.analyze_models()
    
    analyzer.generate_optimization_plan(routes_issues, fk_issues, models_issues)
    
    print("\n✅ Análisis de rendimiento completado")

if __name__ == "__main__":
    main()
