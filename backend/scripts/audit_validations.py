"""
Script de auditoría para validaciones en servicios.
Identifica métodos que reciben strings y verifica si validan contenido vacío.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def find_python_files(directory: str) -> List[Path]:
    """Encuentra todos los archivos Python en un directorio"""
    path = Path(directory)
    return list(path.rglob("*.py"))

def extract_method_signatures(content: str) -> List[Tuple[int, str]]:
    """Extrae firmas de métodos de un archivo"""
    methods = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Buscar definiciones de métodos
        if re.match(r'\s*def\s+\w+\s*\(', line):
            # Capturar método multi-línea
            method_sig = line
            j = i
            while j < len(lines) and not re.search(r'\):', lines[j]):
                j += 1
                if j < len(lines):
                    method_sig += lines[j]
            methods.append((i, method_sig.strip()))
    
    return methods

def has_string_parameter(signature: str) -> List[str]:
    """Detecta parámetros tipo string que podrían necesitar validación"""
    suspicious_params = []
    
    # Parámetros sospechosos que deberían validarse
    patterns = [
        r'contenido:\s*str',
        r'titulo:\s*str',
        r'descripcion:\s*str',
        r'texto:\s*str',
        r'mensaje:\s*str',
        r'nombre:\s*str',
        r'codigo:\s*str',
    ]
    
    for pattern in patterns:
        if re.search(pattern, signature):
            match = re.search(r'(\w+):\s*str', signature)
            if match:
                suspicious_params.append(match.group(1))
    
    return suspicious_params

def check_validation(content: str, method_line: int, param_name: str) -> bool:
    """Verifica si existe validación de vacío para un parámetro"""
    lines = content.split('\n')
    
    # Buscar en las siguientes 20 líneas después del método
    search_range = lines[method_line:method_line + 20]
    search_text = '\n'.join(search_range)
    
    # Patrones de validación común
    validation_patterns = [
        rf'if\s+not\s+{param_name}',
        rf'{param_name}\.strip\(\)',
        rf'_validar.*{param_name}',
        rf'validar.*\({param_name}\)',
    ]
    
    for pattern in validation_patterns:
        if re.search(pattern, search_text, re.IGNORECASE):
            return True
    
    return False

def audit_service(file_path: Path) -> List[Dict]:
    """Audita un archivo de servicio"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        methods = extract_method_signatures(content)
        
        for line_num, signature in methods:
            # Solo revisar métodos públicos que crean/actualizan
            if any(keyword in signature.lower() for keyword in ['crear', 'actualizar', 'agregar', 'registrar', 'guardar', 'entregar']):
                params = has_string_parameter(signature)
                
                for param in params:
                    has_validation = check_validation(content, line_num, param)
                    
                    if not has_validation:
                        findings.append({
                            'file': str(file_path),
                            'line': line_num,
                            'method': signature.split('(')[0].replace('def ', '').strip(),
                            'parameter': param,
                            'severity': 'MEDIUM' if param in ['contenido', 'titulo', 'mensaje'] else 'LOW',
                            'signature': signature[:100] + '...' if len(signature) > 100 else signature
                        })
    
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
    
    return findings

def main():
    """Función principal"""
    print("🔍 Auditoría de Validaciones en Servicios")
    print("=" * 70)
    
    # Directorios a auditar
    service_dirs = [
        'src/services/academic',
        'src/services/evaluaciones',
        'src/services/auth',
    ]
    
    all_findings = []
    
    for service_dir in service_dirs:
        if os.path.exists(service_dir):
            print(f"\n📂 Auditando: {service_dir}")
            files = find_python_files(service_dir)
            
            for file_path in files:
                if file_path.name.endswith('_service.py'):
                    findings = audit_service(file_path)
                    all_findings.extend(findings)
    
    # Resumen
    print("\n" + "=" * 70)
    print(f"📊 RESULTADOS: {len(all_findings)} posibles problemas encontrados")
    print("=" * 70)
    
    # Agrupar por severidad
    by_severity = {}
    for finding in all_findings:
        severity = finding['severity']
        by_severity.setdefault(severity, []).append(finding)
    
    for severity in ['HIGH', 'MEDIUM', 'LOW']:
        if severity in by_severity:
            print(f"\n⚠️  {severity}: {len(by_severity[severity])} casos")
            for finding in by_severity[severity]:
                file_name = Path(finding['file']).name
                print(f"  • {file_name}:{finding['line']} - {finding['method']}()")
                print(f"    Parámetro sin validación aparente: '{finding['parameter']}'")
    
    # Recomendaciones
    print("\n" + "=" * 70)
    print("💡 RECOMENDACIONES:")
    print("=" * 70)
    print("1. Revisar manualmente cada método identificado")
    print("2. Agregar validaciones: if not param or not param.strip()")
    print("3. Considerar validaciones de longitud mínima/máxima")
    print("4. Crear tests unitarios para validaciones")
    print("5. Documentar validaciones en docstrings")
    
    # Guardar reporte
    with open('validation_audit_report.txt', 'w', encoding='utf-8') as f:
        f.write("REPORTE DE AUDITORÍA DE VALIDACIONES\n")
        f.write("=" * 70 + "\n\n")
        
        for finding in all_findings:
            f.write(f"Archivo: {finding['file']}\n")
            f.write(f"Línea: {finding['line']}\n")
            f.write(f"Método: {finding['method']}()\n")
            f.write(f"Parámetro: {finding['parameter']}\n")
            f.write(f"Severidad: {finding['severity']}\n")
            f.write(f"Firma: {finding['signature']}\n")
            f.write("-" * 70 + "\n\n")
    
    print(f"\n✅ Reporte guardado en: validation_audit_report.txt")

if __name__ == "__main__":
    main()
