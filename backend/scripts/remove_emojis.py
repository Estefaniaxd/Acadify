"""
Elimina emojis de los archivos de test que causan SyntaxError
"""

import re
from pathlib import Path

def remove_emojis(text: str) -> str:
    """Elimina emojis y caracteres Unicode problemáticos"""
    # Patrón para emojis comunes
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', text)

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
            print(f"No existe: {test_file}")
            continue
        
        print(f"Procesando: {test_file}")
        
        # Leer
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_len = len(content)
        
        # Eliminar emojis
        clean_content = remove_emojis(content)
        
        # Guardar
        with open(path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        removed = original_len - len(clean_content)
        print(f"  Eliminados {removed} caracteres emoji")
    
    print("\nProceso completado")

if __name__ == "__main__":
    main()
