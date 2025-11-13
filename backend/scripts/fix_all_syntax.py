"""
Script de emergencia para arreglar TODOS los errores de sintaxis en tests

Aplica las siguientes correcciones:
1. Elimina comas antes de paréntesis de cierre
2. Elimina dobles comas
3. Arregla comillas sin cerrar
4. Arregla paréntesis sin cerrar
5. Elimina trailing commas problemáticas
"""

import re
from pathlib import Path

def fix_syntax_errors(content: str) -> str:
    """Aplica correcciones de sintaxis comunes"""
    
    # 1. Eliminar coma antes de paréntesis de cierre: ),
    content = re.sub(r',(\s*\))', r'\1', content)
    
    # 2. Eliminar coma antes de corchete de cierre: ],
    content = re.sub(r',(\s*\])', r'\1', content)
    
    # 3. Eliminar dobles comas: ,,
    content = re.sub(r',,+', ',', content)
    
    # 4. Arreglar comillas sin cerrar en líneas
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Si tiene comillas impares y no es comentario
        if line.strip() and not line.strip().startswith('#'):
            # Contar comillas dobles
            double_quotes = line.count('"') - line.count('\\"')
            single_quotes = line.count("'") - line.count("\\'")
            
            # Si hay comillas impares y no es docstring
            if double_quotes % 2 != 0 and '"""' not in line:
                # Intentar cerrar al final si termina con coma
                if line.rstrip().endswith(','):
                    line = line.rstrip()[:-1] + '",\n'
                elif not line.rstrip().endswith('"'):
                    line = line.rstrip() + '"\n'
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # 5. Arreglar patrones específicos problemáticos
    # Campo obligatorio, seguido de texto → eliminar
    content = re.sub(r'#\s*Campo obligatorio,\s*(\w)', r'# Campo obligatorio\n        \1', content)
    
    # Múltiples argumentos en una línea sin formato correcto
    # puntuacion=20.0, dos partes → split
    content = re.sub(
        r'(\w+)\s*=\s*([^,]+),\s+([a-zA-Z]+\s+[^"]*)"',
        r'\1=\2  # \3',
        content
    )
    
    return content

def main():
    """Procesa todos los archivos de test"""
    test_files = [
        "TEST/test_calificacion_service.py",
        "TEST/test_evaluacion_service.py",
        "TEST/test_intento_service.py"
    ]
    
    for test_file in test_files:
        path = Path(test_file)
        if not path.exists():
            print(f"❌ No existe: {test_file}")
            continue
        
        print(f"🔧 Procesando: {test_file}")
        
        # Leer contenido
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Aplicar correcciones
        fixed_content = fix_syntax_errors(original_content)
        
        # Guardar
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Contar cambios
        changes = sum(1 for a, b in zip(original_content, fixed_content) if a != b)
        print(f"   ✅ {changes} caracteres modificados")
    
    print("\n✨ Proceso completado")

if __name__ == "__main__":
    main()
