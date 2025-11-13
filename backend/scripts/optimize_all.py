#!/usr/bin/env python3
"""
Script maestro para ejecutar todas las optimizaciones del proyecto en orden.
"""

import subprocess
import sys
from pathlib import Path

class MasterOptimizer:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.scripts_path = self.backend_path / "scripts"
        self.python = self.backend_path / "venv" / "bin" / "python"
        
    def run_script(self, script_name: str, description: str) -> bool:
        """Ejecuta un script de Python"""
        print("\n" + "="*80)
        print(f"▶️  {description}")
        print("="*80)
        
        script_path = self.scripts_path / script_name
        if not script_path.exists():
            print(f"❌ Script no encontrado: {script_path}")
            return False
        
        try:
            result = subprocess.run(
                [str(self.python), str(script_path)],
                cwd=str(self.backend_path),
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            print(f"❌ Error ejecutando script: {e}")
            return False
    
    def run_optimization_pipeline(self):
        """Ejecuta el pipeline completo de optimización"""
        print("\n" + "="*90)
        print("🚀 PIPELINE DE OPTIMIZACIÓN COMPLETA DE ACADIFY")
        print("="*90)
        
        tasks = [
            ("audit_structure.py", "FASE 1: Auditoría de Estructura"),
            ("analyze_performance.py", "FASE 2: Análisis de Rendimiento"),
            # Los siguientes son interactivos, no los ejecutamos automáticamente
            # ("add_fk_indexes.py", "FASE 3: Agregar Índices a FK"),
            # ("reorganize_routes.py", "FASE 4: Reorganizar Rutas"),
        ]
        
        results = {}
        
        for script, description in tasks:
            success = self.run_script(script, description)
            results[description] = "✅" if success else "❌"
        
        # Resumen final
        print("\n" + "="*90)
        print("📊 RESUMEN DE OPTIMIZACIÓN")
        print("="*90 + "\n")
        
        for phase, status in results.items():
            print(f"{status} {phase}")
        
        # Pasos manuales pendientes
        print("\n" + "="*90)
        print("📋 PASOS MANUALES PENDIENTES")
        print("="*90)
        
        print("\n1️⃣  AGREGAR ÍNDICES A FOREIGN KEYS (Crítico - Alto impacto):")
        print("   python scripts/add_fk_indexes.py")
        print("   → Esto mejorará dramáticamente el rendimiento de las queries")
        
        print("\n2️⃣  REORGANIZAR ARCHIVOS EN ROUTES:")
        print("   python scripts/reorganize_routes.py")
        print("   → Mueve archivos fuera de módulos a sus ubicaciones correctas")
        
        print("\n3️⃣  OPTIMIZAR ARCHIVO CURSO.PY (2804 líneas):")
        print("   - Dividir en múltiples archivos por funcionalidad")
        print("   - Mover lógica de negocio a services")
        print("   - Crear CRUD específicos para cada operación")
        
        print("\n4️⃣  IMPLEMENTAR PAGINACIÓN:")
        print("   - Agregar .limit() y .offset() a todas las queries .all()")
        print("   - Implementar esquemas de paginación en responses")
        
        print("\n5️⃣  AGREGAR EAGER LOADING:")
        print("   - Usar joinedload() o selectinload() en relaciones")
        print("   - Evitar N+1 queries en bucles")
        
        print("\n6️⃣  HABILITAR CACHÉ REDIS:")
        print("   - Cachear resultados de queries frecuentes")
        print("   - Implementar TTL apropiado")
        
        print("\n" + "="*90)
        print("✅ Auditoría completada. Revisa los reportes generados:")
        print("   - audit_report.json")
        print("   - performance_report.json")
        print("="*90 + "\n")

def main():
    backend_path = "/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    optimizer = MasterOptimizer(backend_path)
    optimizer.run_optimization_pipeline()

if __name__ == "__main__":
    main()
