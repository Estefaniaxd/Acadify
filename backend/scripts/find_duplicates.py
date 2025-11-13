#!/usr/bin/env python3
"""Encuentra argumentos duplicados en fixtures"""
import sys

def find_duplicates(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    in_call = False
    call_lines = []
    start_line = 0
    
    for i, line in enumerate(lines, 1):
        if 'PreguntaEvaluacion(' in line or 'Evaluacion(' in line or 'IntentoEvaluacion(' in line:
            in_call = True
            start_line = i
            call_lines = [line]
        elif in_call:
            call_lines.append(line)
            if ')' in line and not line.strip().startswith('#'):
                # Check for duplicate
                text = ''.join(call_lines)
                if text.count('evaluacion_id=') > 1:
                    print(f"\n❌ DUPLICADO evaluacion_id en {filename}:{start_line}-{i}")
                    print(''.join(call_lines[:8]))
                    print("...")
                if text.count('intento_id=') > 1:
                    print(f"\n❌ DUPLICADO intento_id en {filename}:{start_line}-{i}")
                    print(''.join(call_lines[:8]))
                in_call = False
                call_lines = []

if __name__ == "__main__":
    for f in ['TEST/test_evaluacion_service.py', 'TEST/test_intento_service.py']:
        print(f"\n🔍 Verificando {f}...")
        find_duplicates(f)
