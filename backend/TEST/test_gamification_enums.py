"""
Test para verificar que los enums de gamificación se crean e importan correctamente.

Este test verifica:
1. Todos los enums se pueden importar
2. Los valores de los enums son correctos
3. No hay errores de sintaxis

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_tienda_enums():
    """Verifica que los enums de tienda se importan correctamente."""
    print("🧪 Testing: Import tienda_enums...")
    
    from src.enums.gamification.tienda_enums import (
        CategoriaItem,
        RarezaItem,
        MetodoAdquisicion,
    )
    
    # Verificar categorías de items
    assert CategoriaItem.CABELLO.value == "cabello"
    assert CategoriaItem.ROPA_SUPERIOR.value == "ropa_superior"
    assert CategoriaItem.FUNCIONAL.value == "funcional"
    print(f"  ✅ CategoriaItem: {len(CategoriaItem)} categorías")
    
    # Verificar rareza
    assert RarezaItem.COMUN.value == "comun"
    assert RarezaItem.RARO.value == "raro"
    assert RarezaItem.EPICO.value == "epico"
    assert RarezaItem.LEGENDARIO.value == "legendario"
    print(f"  ✅ RarezaItem: {len(RarezaItem)} niveles de rareza")
    
    # Verificar método adquisición
    assert MetodoAdquisicion.COMPRA.value == "compra"
    assert MetodoAdquisicion.LOGRO.value == "logro"
    print(f"  ✅ MetodoAdquisicion: {len(MetodoAdquisicion)} métodos")


def test_import_etiqueta_enums():
    """Verifica que los enums de etiquetas se importan correctamente."""
    print("\n🧪 Testing: Import etiqueta_enums...")
    
    from src.enums.gamification.etiqueta_enums import (
        CategoriaEtiqueta,
        RarezaEtiqueta,
        TipoRequisito,
    )
    
    # Verificar categorías
    assert CategoriaEtiqueta.MATEMATICAS.value == "matematicas"
    assert CategoriaEtiqueta.PROGRAMACION.value == "programacion"
    assert CategoriaEtiqueta.LECTURA.value == "lectura"
    print(f"  ✅ CategoriaEtiqueta: {len(CategoriaEtiqueta)} categorías")
    
    # Verificar rareza
    assert RarezaEtiqueta.COMUN.value == "comun"
    assert RarezaEtiqueta.LEGENDARIO.value == "legendario"
    print(f"  ✅ RarezaEtiqueta: {len(RarezaEtiqueta)} niveles")
    
    # Verificar requisitos
    assert TipoRequisito.TAREAS_COMPLETADAS.value == "tareas_completadas"
    assert TipoRequisito.RACHA_DIAS.value == "racha_dias"
    print(f"  ✅ TipoRequisito: {len(TipoRequisito)} tipos")


def test_import_racha_enums():
    """Verifica que los enums de rachas se importan correctamente."""
    print("\n🧪 Testing: Import racha_enums...")
    
    from src.enums.gamification.racha_enums import (
        TipoEventoRacha,
        TipoMilestone,
        TipoActividadRacha,
    )
    
    # Verificar eventos
    assert TipoEventoRacha.INCREMENTO.value == "incremento"
    assert TipoEventoRacha.PERDIDA.value == "perdida"
    assert TipoEventoRacha.MILESTONE.value == "milestone"
    print(f"  ✅ TipoEventoRacha: {len(TipoEventoRacha)} tipos de eventos")
    
    # Verificar milestones
    assert TipoMilestone.DIARIO.value == "diario"
    assert TipoMilestone.SEMANAL.value == "semanal"
    print(f"  ✅ TipoMilestone: {len(TipoMilestone)} tipos de milestone")
    
    # Verificar actividades
    assert TipoActividadRacha.TAREA_COMPLETADA.value == "tarea_completada"
    assert TipoActividadRacha.EXAMEN_REALIZADO.value == "examen_realizado"
    print(f"  ✅ TipoActividadRacha: {len(TipoActividadRacha)} tipos")


def test_import_all_from_init():
    """Verifica que todos los enums se pueden importar desde __init__.py"""
    print("\n🧪 Testing: Import all from __init__...")
    
    from src.enums.gamification import (
        TipoInsignia,
        TipoRecompensa,
        CategoriaItem,
        RarezaItem,
        MetodoAdquisicion,
        CategoriaEtiqueta,
        RarezaEtiqueta,
        TipoRequisito,
        TipoEventoRacha,
        TipoMilestone,
        TipoActividadRacha,
    )
    
    print("  ✅ Todos los enums se importan desde __init__.py")
    print(f"  ✅ Total de enums: 11")


def test_enum_iteration():
    """Verifica que se pueden iterar los enums."""
    print("\n🧪 Testing: Enum iteration...")
    
    from src.enums.gamification import CategoriaItem, RarezaItem
    
    # Iterar categorías
    categorias = list(CategoriaItem)
    print(f"  ✅ CategoriaItem iterado: {len(categorias)} items")
    
    # Iterar rareza
    rareza_items = list(RarezaItem)
    print(f"  ✅ RarezaItem iterado: {len(rareza_items)} items")
    
    # Verificar que son instancias correctas
    assert all(isinstance(cat, CategoriaItem) for cat in categorias)
    print("  ✅ Todas las instancias son válidas")


def main():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("🚀 TESTING ENUMS DE GAMIFICACIÓN")
    print("=" * 60)
    
    try:
        test_import_tienda_enums()
        test_import_etiqueta_enums()
        test_import_racha_enums()
        test_import_all_from_init()
        test_enum_iteration()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ ERROR EN TESTS: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
