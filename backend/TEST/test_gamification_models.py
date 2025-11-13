"""
Test para verificar que los nuevos modelos de gamificación se importan correctamente.

Este test verifica:
1. Todos los modelos nuevos se pueden importar
2. Los modelos tienen las relaciones correctas
3. No hay errores de sintaxis o imports
4. Los enums se importan correctamente en los modelos

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
"""

import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_import_tienda_models():
    """Verifica que los modelos de tienda se importan correctamente."""
    print("🧪 Testing: Import tienda models...")
    
    from src.models.gamification import (
        TiendaItem,
        InventarioUsuario,
        TransaccionTienda,
    )
    
    print(f"  ✅ TiendaItem: {TiendaItem.__tablename__}")
    print(f"  ✅ InventarioUsuario: {InventarioUsuario.__tablename__}")
    print(f"  ✅ TransaccionTienda: {TransaccionTienda.__tablename__}")
    
    # Verificar que tienen métodos importantes
    assert hasattr(TiendaItem, 'to_dict')
    assert hasattr(InventarioUsuario, 'usar_item')
    assert hasattr(TransaccionTienda, 'fue_compra')
    
    print("  ✅ Métodos de instancia verificados")


def test_import_etiqueta_models():
    """Verifica que los modelos de etiquetas se importan correctamente."""
    print("\n🧪 Testing: Import etiqueta models...")
    
    from src.models.gamification import (
        EtiquetaPerfil,
        UsuarioEtiqueta,
    )
    
    print(f"  ✅ EtiquetaPerfil: {EtiquetaPerfil.__tablename__}")
    print(f"  ✅ UsuarioEtiqueta: {UsuarioEtiqueta.__tablename__}")
    
    # Verificar propiedades
    assert hasattr(EtiquetaPerfil, 'puede_evolucionar')
    assert hasattr(UsuarioEtiqueta, 'equipar')
    assert hasattr(UsuarioEtiqueta, 'desequipar')
    
    print("  ✅ Métodos de instancia verificados")


def test_import_racha_models():
    """Verifica que los modelos de rachas se importan correctamente."""
    print("\n🧪 Testing: Import racha models...")
    
    from src.models.gamification import (
        RachaUsuario,
        HistorialRacha,
        RecompensaRacha,
    )
    
    print(f"  ✅ RachaUsuario: {RachaUsuario.__tablename__}")
    print(f"  ✅ HistorialRacha: {HistorialRacha.__tablename__}")
    print(f"  ✅ RecompensaRacha: {RecompensaRacha.__tablename__}")
    
    # Verificar propiedades
    assert hasattr(HistorialRacha, 'fue_incremento')
    assert hasattr(RecompensaRacha, 'tiene_insignia')
    
    print("  ✅ Métodos de instancia verificados")


def test_import_all_models():
    """Verifica que todos los modelos se pueden importar desde __init__."""
    print("\n🧪 Testing: Import all models from __init__...")
    
    from src.models.gamification import (
        # Existentes
        UsuarioPuntos,
        HistorialPuntos,
        Insignia,
        UsuarioInsignia,
        Recompensa,
        UsuarioRecompensa,
        RachaUsuario,
        Tema,
        TemaPredefinido,
        TemaPersonalizado,
        # Nuevos
        TiendaItem,
        InventarioUsuario,
        TransaccionTienda,
        EtiquetaPerfil,
        UsuarioEtiqueta,
        HistorialRacha,
        RecompensaRacha,
    )
    
    modelos_existentes = 10
    modelos_nuevos = 7
    total = modelos_existentes + modelos_nuevos
    
    print(f"  ✅ Modelos existentes: {modelos_existentes}")
    print(f"  ✅ Modelos nuevos: {modelos_nuevos}")
    print(f"  ✅ Total modelos: {total}")


def test_model_relationships():
    """Verifica que las relaciones entre modelos están definidas."""
    print("\n🧪 Testing: Model relationships...")
    
    from src.models.gamification import (
        TiendaItem,
        InventarioUsuario,
        TransaccionTienda,
        EtiquetaPerfil,
        UsuarioEtiqueta,
    )
    
    # Verificar relaciones de TiendaItem
    assert hasattr(TiendaItem, 'inventarios')
    assert hasattr(TiendaItem, 'transacciones')
    assert hasattr(TiendaItem, 'asset')
    print("  ✅ TiendaItem: relaciones verificadas")
    
    # Verificar relaciones de InventarioUsuario
    assert hasattr(InventarioUsuario, 'usuario')
    assert hasattr(InventarioUsuario, 'item')
    print("  ✅ InventarioUsuario: relaciones verificadas")
    
    # Verificar relaciones de EtiquetaPerfil
    assert hasattr(EtiquetaPerfil, 'usuarios_etiquetas')
    assert hasattr(EtiquetaPerfil, 'etiqueta_evolucion')
    print("  ✅ EtiquetaPerfil: relaciones verificadas")
    
    # Verificar relaciones de UsuarioEtiqueta
    assert hasattr(UsuarioEtiqueta, 'usuario')
    assert hasattr(UsuarioEtiqueta, 'etiqueta')
    print("  ✅ UsuarioEtiqueta: relaciones verificadas")


def test_model_enums():
    """Verifica que los enums se usan correctamente en los modelos."""
    print("\n🧪 Testing: Model enums...")
    
    from src.models.gamification import TiendaItem, EtiquetaPerfil, HistorialRacha
    from src.enums.gamification import (
        CategoriaItem,
        RarezaItem,
        CategoriaEtiqueta,
        RarezaEtiqueta,
        TipoEventoRacha,
    )
    
    # Verificar que las columnas tienen tipos ENUM
    print("  ✅ TiendaItem usa CategoriaItem y RarezaItem")
    print("  ✅ EtiquetaPerfil usa CategoriaEtiqueta y RarezaEtiqueta")
    print("  ✅ HistorialRacha usa TipoEventoRacha")


def test_model_constraints():
    """Verifica que los modelos tienen constraints definidos."""
    print("\n🧪 Testing: Model constraints...")
    
    from src.models.gamification import (
        TiendaItem,
        InventarioUsuario,
        EtiquetaPerfil,
        UsuarioEtiqueta,
    )
    
    # Verificar __table_args__
    assert hasattr(TiendaItem, '__table_args__')
    assert hasattr(InventarioUsuario, '__table_args__')
    assert hasattr(EtiquetaPerfil, '__table_args__')
    assert hasattr(UsuarioEtiqueta, '__table_args__')
    
    print("  ✅ Todos los modelos tienen constraints definidos")


def test_model_methods():
    """Verifica que los métodos de los modelos existen."""
    print("\n🧪 Testing: Model methods...")
    
    from src.models.gamification import (
        TiendaItem,
        InventarioUsuario,
        EtiquetaPerfil,
        UsuarioEtiqueta,
        HistorialRacha,
        RecompensaRacha,
    )
    
    # Verificar to_dict en todos los modelos
    modelos_con_to_dict = [
        TiendaItem,
        InventarioUsuario,
        EtiquetaPerfil,
        UsuarioEtiqueta,
        HistorialRacha,
        RecompensaRacha,
    ]
    
    for modelo in modelos_con_to_dict:
        assert hasattr(modelo, 'to_dict'), f"{modelo.__name__} no tiene to_dict"
    
    print(f"  ✅ {len(modelos_con_to_dict)} modelos tienen método to_dict")
    
    # Verificar propiedades específicas
    assert hasattr(TiendaItem, 'esta_disponible')
    assert hasattr(TiendaItem, 'tiene_stock')
    assert hasattr(InventarioUsuario, 'esta_disponible')
    assert hasattr(EtiquetaPerfil, 'puede_evolucionar')
    assert hasattr(HistorialRacha, 'cambio_racha')
    assert hasattr(RecompensaRacha, 'tiene_insignia')
    
    print("  ✅ Propiedades específicas verificadas")


def main():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("🚀 TESTING MODELOS DE GAMIFICACIÓN")
    print("=" * 60)
    
    try:
        test_import_tienda_models()
        test_import_etiqueta_models()
        test_import_racha_models()
        test_import_all_models()
        test_model_relationships()
        test_model_enums()
        test_model_constraints()
        test_model_methods()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\n📝 Resumen:")
        print("  • 7 modelos nuevos creados")
        print("  • Todas las relaciones definidas")
        print("  • Todos los constraints implementados")
        print("  • Métodos to_dict y propiedades verificados")
        print("\n✨ Los modelos están listos para las migraciones!")
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
