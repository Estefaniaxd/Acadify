#!/usr/bin/env python3
"""
Script para corregir problemas específicos identificados
Siguiendo Clean Code: cada función hace UNA cosa
"""
import subprocess
from pathlib import Path


def fix_revisado_por_id():
    """Corrige revisado_por_id -> calificador_id"""
    print("🔧 Corrigiendo revisado_por_id...")
    cmd = "sed -i 's/revisado_por_id/calificador_id/g' TEST/test_calificacion_service.py"
    subprocess.run(cmd, shell=True)
    print("  ✅ Completado")


def fix_feedback_parameter():
    """El servicio calificar_manualmente no acepta feedback_automatico como parámetro"""
    print("\n🔧 Corrigiendo parámetro feedback en llamadas al servicio...")
    
    test_file = Path("TEST/test_calificacion_service.py")
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Buscar llamadas a calificar_manualmente con feedback=
    original = content
    content = content.replace('feedback_automatico="', 'feedback="')
    
    if content != original:
        with open(test_file, 'w') as f:
            f.write(content)
        print("  ✅ Completado")
    else:
        print("  ℹ️  No se encontraron cambios necesarios")


def fix_intento_id_in_constructors():
    """Corrige IntentoEvaluacion(id= que aún quedan"""
    print("\n🔧 Corrigiendo IntentoEvaluacion(id=...")
    
    cmds = [
        "sed -i '/IntentoEvaluacion(/,/)/{ s/\\bid=uuid4()/intento_id=uuid4()/g }' TEST/test_calificacion_service.py",
        "sed -i '/IntentoEvaluacion(/,/)/{ s/\\bid=/intento_id=/g }' TEST/test_calificacion_service.py",
    ]
    
    for cmd in cmds:
        subprocess.run(cmd, shell=True)
    
    print("  ✅ Completado")


def fix_pregunta_id_attribute():
    """Corrige .id cuando debería ser .pregunta_id"""
    print("\n🔧 Corrigiendo atributos .id en objetos pregunta...")
    
    test_file = Path("TEST/test_calificacion_service.py")
    with open(test_file, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        # Si la línea tiene pregunta.id o pregunta1.id etc
        if 'pregunta' in line and '.id' in line and 'pregunta_id' not in line:
            line = line.replace('.id', '.pregunta_id')
        new_lines.append(line)
    
    with open(test_file, 'w') as f:
        f.writelines(new_lines)
    
    print("  ✅ Completado")


def fix_mock_configurations():
    """Corrige configuraciones de mock que causan TypeError"""
    print("\n🔧 Verificando configuraciones de mock...")
    
    test_file = Path("TEST/test_calificacion_service.py")
    with open(test_file, 'r') as f:
        content = f.read()
    
    original = content
    
    # Asegurar que mocks que deberían retornar listas lo hagan
    # mock_db.query().filter().all() debe retornar lista, no Mock
    content = content.replace('.all.return_value = respuestas', '.all.return_value = [respuestas]')
    content = content.replace('.all.return_value = intentos', '.all.return_value = [intentos]')
    
    if content != original:
        with open(test_file, 'w') as f:
            f.write(content)
        print("  ✅ Correcciones aplicadas")
    else:
        print("  ℹ️  No se encontraron problemas")


def analyze_service_signature():
    """Analiza la firma del método calificar_manualmente"""
    print("\n🔍 Analizando firma de calificar_manualmente...")
    
    service_file = Path("src/services/evaluaciones/calificacion_service.py")
    with open(service_file, 'r') as f:
        content = f.read()
    
    # Buscar la definición del método
    import re
    pattern = r'def calificar_manualmente\((.*?)\):'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        params = match.group(1)
        print(f"  📋 Parámetros: {params[:200]}")
        
        if 'feedback' not in params:
            print("  ⚠️  El método NO acepta parámetro 'feedback'")
            print("  💡 Los tests deben usar el campo del modelo, no pasarlo como parámetro")
    else:
        print("  ❌ No se encontró el método")


def main():
    """Ejecuta todas las correcciones"""
    print("="*80)
    print("🚀 CORRECCIONES ESPECÍFICAS - CLEAN CODE")
    print("="*80)
    
    # Cambiar al directorio correcto
    import os
    os.chdir(Path(__file__).parent.parent)
    
    # Ejecutar correcciones
    fix_revisado_por_id()
    fix_feedback_parameter()
    fix_intento_id_in_constructors()
    fix_pregunta_id_attribute()
    fix_mock_configurations()
    analyze_service_signature()
    
    print("\n" + "="*80)
    print("✨ Correcciones completadas")
    print("="*80)
    print("\n💡 Ejecuta: venv/bin/python scripts/debug_tests.py para ver resultado\n")


if __name__ == "__main__":
    main()
