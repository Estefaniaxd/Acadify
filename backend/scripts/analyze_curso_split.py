#!/usr/bin/env python3
"""
Analiza el archivo curso.py y genera el plan de división en módulos más pequeños.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

def analyze_curso_file():
    """Analiza el contenido del archivo curso.py"""
    
    curso_path = Path("/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/src/api/routes/academic/curso.py")
    
    with open(curso_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    print("="*90)
    print("📊 ANÁLISIS DEL ARCHIVO CURSO.PY (2804 líneas)")
    print("="*90)
    
    # Encontrar todas las rutas
    routes = []
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('@router.'):
            # Obtener el método y path
            match = re.search(r'@router\.(\w+)\("([^"]+)"', line)
            if match:
                method = match.group(1)
                path = match.group(2)
                
                # Obtener el nombre de la función
                func_line_idx = i  # Siguiente línea
                if func_line_idx < len(lines):
                    func_match = re.search(r'async def (\w+)\(', lines[func_line_idx])
                    if func_match:
                        func_name = func_match.group(1)
                        routes.append({
                            'line': i,
                            'method': method.upper(),
                            'path': path,
                            'function': func_name
                        })
    
    print(f"\n📌 Total de endpoints: {len(routes)}\n")
    
    # Categorizar endpoints
    categories = {
        'inscripcion': [],
        'cursos': [],
        'programas': [],
        'comentarios': [],
        'tareas': [],
        'archivos': [],
        'reacciones': [],
        'debug': []
    }
    
    for route in routes:
        path = route['path']
        func = route['function']
        
        if 'debug' in path or 'debug' in func:
            categories['debug'].append(route)
        elif 'comentario' in path or 'comentario' in func or 'respuesta' in func:
            categories['comentarios'].append(route)
        elif 'tarea' in path or 'tarea' in func:
            categories['tareas'].append(route)
        elif 'archivo' in path or 'archivo' in func:
            categories['archivos'].append(route)
        elif 'reacci' in path or 'reacci' in func:
            categories['reacciones'].append(route)
        elif 'programa' in path or 'programa' in func:
            categories['programas'].append(route)
        elif 'inscrib' in func or 'vincular' in func or 'codigo' in func or 'confirmar' in func:
            categories['inscripcion'].append(route)
        else:
            categories['cursos'].append(route)
    
    # Mostrar categorización
    for category, items in categories.items():
        if items:
            print(f"\n📁 {category.upper()} ({len(items)} endpoints):")
            for item in items:
                print(f"   {item['method']:6} {item['path']:40} → {item['function']}")
    
    # Plan de división
    print("\n" + "="*90)
    print("📋 PLAN DE DIVISIÓN DE ARCHIVOS")
    print("="*90)
    
    division_plan = [
        {
            'file': 'cursos.py',
            'description': 'Gestión básica de cursos (listado, detalle)',
            'categories': ['cursos'],
            'endpoints': categories['cursos']
        },
        {
            'file': 'inscripciones.py',
            'description': 'Inscripción, vinculación y códigos de acceso',
            'categories': ['inscripcion', 'programas'],
            'endpoints': categories['inscripcion'] + categories['programas']
        },
        {
            'file': 'comentarios.py',
            'description': 'Sistema de comentarios y respuestas',
            'categories': ['comentarios'],
            'endpoints': categories['comentarios']
        },
        {
            'file': 'tareas.py',
            'description': 'Gestión de tareas del curso',
            'categories': ['tareas'],
            'endpoints': categories['tareas']
        },
        {
            'file': 'archivos.py',
            'description': 'Subida y gestión de archivos',
            'categories': ['archivos'],
            'endpoints': categories['archivos']
        },
        {
            'file': 'reacciones.py',
            'description': 'Sistema de reacciones',
            'categories': ['reacciones'],
            'endpoints': categories['reacciones']
        }
    ]
    
    for i, plan in enumerate(division_plan, 1):
        print(f"\n{i}. 📄 {plan['file']}")
        print(f"   Descripción: {plan['description']}")
        print(f"   Endpoints: {len(plan['endpoints'])}")
        for endpoint in plan['endpoints'][:3]:  # Mostrar primeros 3
            print(f"   - {endpoint['method']:6} {endpoint['path']}")
        if len(plan['endpoints']) > 3:
            print(f"   ... y {len(plan['endpoints']) - 3} más")
    
    print("\n" + "="*90)
    print("🎯 SERVICIOS NECESARIOS")
    print("="*90)
    
    services = [
        ('curso_service.py', 'Lógica de negocio de cursos, inscripciones'),
        ('comentario_service.py', 'Lógica de comentarios y respuestas'),
        ('tarea_service.py', 'Lógica de gestión de tareas'),
        ('archivo_service.py', 'Procesamiento y almacenamiento de archivos'),
        ('reaccion_service.py', 'Gestión de reacciones'),
    ]
    
    for service, desc in services:
        print(f"\n📦 {service}")
        print(f"   {desc}")
    
    print("\n" + "="*90)
    print("✅ SIGUIENTE PASO")
    print("="*90)
    print("\n¿Deseas que genere automáticamente estos archivos?")
    print("Se creará:")
    print("  - 6 archivos de rutas separados")
    print("  - 5 archivos de servicios")
    print("  - Script de actualización de imports")
    print("\n" + "="*90)
    
    return division_plan, services

if __name__ == "__main__":
    analyze_curso_file()
