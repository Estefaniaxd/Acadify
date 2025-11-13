#!/usr/bin/env python3
"""
Corrector Final de Fixtures - Basado en estructura REAL de modelos
"""
import re
from pathlib import Path


def fix_curso_fixture():
    """Corrige el fixture de Curso con campos correctos"""
    base = Path(__file__).parent.parent
    file_path = base / 'TEST/test_evaluacion_service.py'
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Reemplazar fixture de curso
    old_fixture = '''def curso_realista():
    """Curso de ejemplo realista"""
    return Curso(
        curso_id=uuid4(),
        nombre="Matemáticas Avanzadas",
        codigo="MAT-301",
        descripcion="Curso de cálculo diferencial e integral",
        institucion_id=uuid4(),
        coordinador_id=uuid4(),  # Cambiado de administrador_id
        fecha_inicio=datetime.now(timezone.utc),
        fecha_creacion=datetime.now(timezone.utc),
        activo=True
    )'''
    
    new_fixture = '''def curso_realista():
    """Curso de ejemplo realista"""
    return Curso(
        curso_id=uuid4(),
        nombre="Matemáticas Avanzadas",
        codigo_curso="MAT-301",  # Campo correcto
        descripcion="Curso de cálculo diferencial e integral",
        institucion_id=uuid4(),
        coordinador_id=uuid4(),
        fecha_inicio=datetime.now(timezone.utc),
        fecha_creacion=datetime.now(timezone.utc),
        estado="ACTIVO"  # Campo correcto, no activo
    )'''
    
    if old_fixture.replace(' ', '').replace('\n', '') in content.replace(' ', '').replace('\n', ''):
        content = content.replace(old_fixture, new_fixture)
        print("✅ Curso fixture corregido")
    else:
        # Intentar con regex más flexible
        pattern = r'def curso_realista\(\):.*?return Curso\([^)]+\)'
        if re.search(pattern, content, re.DOTALL):
            print("⚠️  Fixture encontrado pero estructura diferente, aplicando cambios manuales")
            content = re.sub(r'\bcodigo\s*=', 'codigo_curso=', content)
            content = re.sub(r'\bactivo\s*=\s*True', 'estado="ACTIVO"', content)
            print("✅ Cambios aplicados")
    
    with open(file_path, 'w') as f:
        f.write(content)


def fix_intento_evaluacion_fixtures():
    """Corrige campos de IntentoEvaluacion"""
    base = Path(__file__).parent.parent
    
    for test_file in ['TEST/test_evaluacion_service.py', 'TEST/test_intento_service.py']:
        file_path = base / test_file
        if not file_path.exists():
            continue
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        
        # estado_intento → estado
        content = re.sub(r'estado_intento\s*=\s*"FINALIZADO"', 'estado=EstadoIntento.FINALIZADO', content)
        content = re.sub(r'estado_intento\s*=\s*"EN_PROGRESO"', 'estado=EstadoIntento.EN_PROGRESO', content)
        content = re.sub(r'estado_intento\s*=\s*EstadoIntento\.', 'estado=EstadoIntento.', content)
        
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ {test_file}: IntentoEvaluacion corregido")


def fix_evaluacion_fixtures():
    """Corrige campos de Evaluacion"""
    base = Path(__file__).parent.parent
    
    for test_file in ['TEST/test_evaluacion_service.py', 'TEST/test_intento_service.py']:
        file_path = base / test_file
        if not file_path.exists():
            continue
            
        with open(file_path, 'r') as f:
            content = f.read()
        
        original = content
        
        # Evaluacion usa 'estado' no 'estado_evaluacion'
        # Y no tiene campo 'configuracion_antitrampa_id', sino que es una relación
        
        if content != original:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ {test_file}: Evaluacion corregido")


def main():
    print("="*70)
    print("🔧 CORRECTOR FINAL DE FIXTURES")
    print("="*70)
    
    fix_curso_fixture()
    fix_intento_evaluacion_fixtures()
    fix_evaluacion_fixtures()
    
    print("\n" + "="*70)
    print("✅ CORRECCIONES COMPLETADAS")
    print("="*70)


if __name__ == "__main__":
    main()
