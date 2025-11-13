#!/usr/bin/env python3
"""
Script de verificación post-refactorización
Verifica que todos los cambios funcionen correctamente
"""

import sys
from pathlib import Path

def test_imports():
    """Verifica que todos los imports funcionen"""
    print("\n" + "="*80)
    print("🧪 VERIFICACIÓN DE IMPORTS")
    print("="*80)
    
    tests = []
    
    # Test 1: Main app
    try:
        from src.main import app
        tests.append(("✅", "Main app", f"{len(app.routes)} rutas"))
    except Exception as e:
        tests.append(("❌", "Main app", str(e)))
    
    # Test 2: Nuevos routers de cursos
    try:
        from src.api.routes.academic.cursos import router as cursos_router
        from src.api.routes.academic.inscripciones import router as inscripciones_router
        from src.api.routes.academic.curso_comentarios import router as comentarios_router
        from src.api.routes.academic.curso_tareas import router as tareas_router
        from src.api.routes.academic.curso_archivos import router as archivos_router
        from src.api.routes.academic.curso_reacciones import router as reacciones_router
        tests.append(("✅", "Routers de cursos (6)", "OK"))
    except Exception as e:
        tests.append(("❌", "Routers de cursos", str(e)))
    
    # Test 3: Service de cursos
    try:
        from src.services.academic.curso_service import curso_service
        tests.append(("✅", "Curso Service", "OK"))
    except Exception as e:
        tests.append(("❌", "Curso Service", str(e)))
    
    # Test 4: Routers reorganizados
    try:
        from src.api.routes.auth.auth_main import router as auth_router
        from src.api.routes.users.avatar import router as avatar_router
        tests.append(("✅", "Routers reorganizados", "OK"))
    except Exception as e:
        tests.append(("❌", "Routers reorganizados", str(e)))
    
    # Mostrar resultados
    print()
    for status, name, detail in tests:
        print(f"{status} {name:30} {detail}")
    
    # Contar éxitos
    success_count = sum(1 for t in tests if t[0] == "✅")
    total = len(tests)
    
    print(f"\n📊 Resultado: {success_count}/{total} tests pasados")
    
    return success_count == total

def verify_files():
    """Verifica que los archivos existan"""
    print("\n" + "="*80)
    print("📁 VERIFICACIÓN DE ARCHIVOS")
    print("="*80)
    
    backend = Path("/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend")
    
    files_to_check = [
        # Archivos nuevos
        ("src/api/routes/academic/cursos.py", "Gestión de cursos"),
        ("src/api/routes/academic/inscripciones.py", "Inscripciones"),
        ("src/api/routes/academic/curso_comentarios.py", "Comentarios"),
        ("src/api/routes/academic/curso_tareas.py", "Tareas"),
        ("src/api/routes/academic/curso_archivos.py", "Archivos"),
        ("src/api/routes/academic/curso_reacciones.py", "Reacciones"),
        
        # Service
        ("src/services/academic/curso_service.py", "Service de cursos"),
        
        # Backups
        ("src/api/routes/academic/curso_backup_1761699705.py", "Backup curso.py"),
        
        # Archivos reorganizados
        ("src/api/routes/auth/auth_main.py", "Auth main"),
        ("src/api/routes/users/avatar.py", "Avatar"),
        ("src/api/routes/users/avatar_service_complete.py", "Avatar complete"),
        
        # Scripts
        ("scripts/split_curso_file.py", "Script de división"),
        ("scripts/audit_structure.py", "Script de auditoría"),
        ("scripts/analyze_performance.py", "Script de performance"),
        
        # Reportes
        ("audit_report.json", "Reporte de auditoría"),
        ("performance_report.json", "Reporte de performance"),
        ("REFACTORING_SUMMARY.md", "Resumen de refactorización"),
    ]
    
    print()
    all_exist = True
    for rel_path, description in files_to_check:
        full_path = backend / rel_path
        if full_path.exists():
            size = full_path.stat().st_size
            size_kb = size / 1024
            print(f"✅ {description:30} ({size_kb:.1f} KB)")
        else:
            print(f"❌ {description:30} (NO ENCONTRADO)")
            all_exist = False
    
    return all_exist

def verify_structure():
    """Verifica la estructura de directorios"""
    print("\n" + "="*80)
    print("🏗️ VERIFICACIÓN DE ESTRUCTURA")
    print("="*80)
    
    backend = Path("/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend")
    
    directories = [
        "src/api/routes/academic",
        "src/api/routes/auth",
        "src/api/routes/users",
        "src/api/routes/dev",
        "src/services/academic",
        "scripts",
    ]
    
    print()
    for dir_path in directories:
        full_path = backend / dir_path
        if full_path.exists() and full_path.is_dir():
            file_count = len(list(full_path.glob("*.py")))
            print(f"✅ {dir_path:30} ({file_count} archivos Python)")
        else:
            print(f"❌ {dir_path:30} (NO EXISTE)")

def show_statistics():
    """Muestra estadísticas del proyecto"""
    print("\n" + "="*80)
    print("📊 ESTADÍSTICAS DEL PROYECTO")
    print("="*80)
    
    backend = Path("/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend")
    
    # Contar archivos Python
    all_py_files = list(backend.rglob("*.py"))
    routes_files = list((backend / "src/api/routes").rglob("*.py"))
    services_files = list((backend / "src/services").rglob("*.py"))
    models_files = list((backend / "src/models").rglob("*.py"))
    crud_files = list((backend / "src/crud").rglob("*.py"))
    
    print(f"""
    📄 Total archivos Python: {len(all_py_files)}
    🛣️  Archivos de rutas: {len(routes_files)}
    📦 Archivos de services: {len(services_files)}
    🗃️  Archivos de modelos: {len(models_files)}
    💾 Archivos de CRUD: {len(crud_files)}
    """)
    
    # Contar líneas en archivos de cursos
    curso_files = {
        "cursos.py": backend / "src/api/routes/academic/cursos.py",
        "inscripciones.py": backend / "src/api/routes/academic/inscripciones.py",
        "curso_comentarios.py": backend / "src/api/routes/academic/curso_comentarios.py",
        "curso_tareas.py": backend / "src/api/routes/academic/curso_tareas.py",
        "curso_archivos.py": backend / "src/api/routes/academic/curso_archivos.py",
        "curso_reacciones.py": backend / "src/api/routes/academic/curso_reacciones.py",
    }
    
    print("    📏 Tamaño de archivos divididos:")
    total_lines = 0
    for name, path in curso_files.items():
        if path.exists():
            with open(path, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"       {name:25} {lines:4} líneas")
    
    print(f"\n    📊 Total líneas en 6 archivos: {total_lines}")
    print(f"    📊 Archivo original (curso.py): 2804 líneas")
    print(f"    📈 Reducción promedio por archivo: {2804 / 6:.0f} → {total_lines / 6:.0f} líneas")

def main():
    """Ejecuta todas las verificaciones"""
    print("="*80)
    print("🔍 VERIFICACIÓN POST-REFACTORIZACIÓN DE ACADIFY")
    print("="*80)
    print("\nEste script verifica que todos los cambios se hayan aplicado correctamente")
    
    # Ejecutar verificaciones
    imports_ok = test_imports()
    files_ok = verify_files()
    verify_structure()
    show_statistics()
    
    # Resultado final
    print("\n" + "="*80)
    print("🏁 RESULTADO FINAL")
    print("="*80)
    
    if imports_ok and files_ok:
        print("\n✅ ÉXITO: Todos los tests pasaron")
        print("\n🎉 La refactorización se completó exitosamente")
        print("\nPróximos pasos:")
        print("  1. Crear los 5 services restantes")
        print("  2. Refactorizar rutas para usar services")
        print("  3. Implementar paginación global")
        print("  4. Agregar tests unitarios")
        print("\n📖 Ver REFACTORING_SUMMARY.md para más detalles")
        return 0
    else:
        print("\n⚠️ ADVERTENCIA: Algunos tests fallaron")
        print("Revisa los errores anteriores para más detalles")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
