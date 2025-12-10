import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

try:
    from src.enums.academic.tareas import EstadoEntrega
    print(f"EstadoEntrega loaded successfully.")
    if "cancelada" in [e.value for e in EstadoEntrega]:
        print("✅ SUCCESS: 'cancelada' is present in EstadoEntrega enum.")
    else:
        print("❌ FAILURE: 'cancelada' is MISSING from EstadoEntrega enum.")
except Exception as e:
    print(f"❌ ERROR: Could not import EstadoEntrega: {e}")
