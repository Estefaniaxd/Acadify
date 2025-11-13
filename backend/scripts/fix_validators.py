#!/usr/bin/env python3
"""Script para corregir validators que usan self en vez de cls."""

import re
from pathlib import Path

count = 0

# Buscar todos los archivos Python en src
for path in Path('src').rglob('*.py'):
    content = path.read_text()
    original = content
    
    # Cambiar @validator y @field_validator def xxx(self a def xxx(cls
    # Pero mantener @model_validator(mode="after") def xxx(self
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Si es @validator o @field_validator (NO model_validator after)
        if ('@validator(' in line or '@field_validator(' in line) and 'model_validator' not in line:
            # Revisar la siguiente línea
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # Cambiar def xxx(self a def xxx(cls si contiene (self
                if 'def ' in next_line and '(self' in next_line and '(cls' not in next_line:
                    lines[i + 1] = re.sub(r'\(self\b', '(cls', next_line)
                    count += 1
        
        i += 1
    
    new_content = '\n'.join(lines)
    
    if new_content != original:
        path.write_text(new_content)
        print(f'✅ Fixed: {path}')

print(f'✅ Done! {count} validators corregidos')
