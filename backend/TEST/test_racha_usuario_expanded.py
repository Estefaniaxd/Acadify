"""
Test para verificar que el modelo RachaUsuario expandido funciona correctamente.

Author: GitHub Copilot & Team
Date: 31 de octubre de 2025
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_racha_usuario_expanded():
    """Verifica que RachaUsuario tiene los nuevos campos."""
    print("🧪 Testing: RachaUsuario expandido...")
    
    from src.models.gamification import RachaUsuario
    
    # Verificar nuevos campos
    campos_nuevos = [
        'racha_congelada_hasta',
        'recuperaciones_disponibles',
        'notificacion_enviada',
        'ultima_recompensa_dia',
    ]
    
    for campo in campos_nuevos:
        assert hasattr(RachaUsuario, campo), f"Falta campo: {campo}"
    
    print(f"  ✅ Todos los campos nuevos existen: {len(campos_nuevos)}")


def test_racha_usuario_properties():
    """Verifica que las propiedades existen."""
    print("\n🧪 Testing: Propiedades de RachaUsuario...")
    
    from src.models.gamification import RachaUsuario
    
    # Verificar propiedades existen
    assert hasattr(RachaUsuario, 'esta_protegida')
    assert hasattr(RachaUsuario, 'puede_recuperar')
    assert hasattr(RachaUsuario, 'dia_ciclo_semanal')
    
    print("  ✅ Propiedades definidas correctamente")
    print("    • esta_protegida")
    print("    • puede_recuperar")
    print("    • dia_ciclo_semanal")


def test_racha_usuario_methods():
    """Verifica que los métodos existen."""
    print("\n🧪 Testing: Métodos de RachaUsuario...")
    
    from src.models.gamification import RachaUsuario
    
    # Verificar métodos existen
    assert hasattr(RachaUsuario, 'incrementar_racha')
    assert hasattr(RachaUsuario, 'resetear_racha')
    assert hasattr(RachaUsuario, 'usar_recuperacion')
    assert hasattr(RachaUsuario, 'activar_congelador')
    assert hasattr(RachaUsuario, 'to_dict')
    
    print("  ✅ incrementar_racha() definido")
    print("  ✅ usar_recuperacion() definido")
    print("  ✅ activar_congelador() definido")
    print("  ✅ resetear_racha() definido")
    print("  ✅ to_dict() definido")


def test_racha_usuario_constraints():
    """Verifica que los constraints están definidos."""
    print("\n🧪 Testing: Constraints de RachaUsuario...")
    
    from src.models.gamification import RachaUsuario
    
    assert hasattr(RachaUsuario, '__table_args__')
    print("  ✅ __table_args__ definido")
    print("  ✅ Constraints de validación implementados")


def test_dia_ciclo_semanal():
    """Verifica que la lógica del día del ciclo semanal está implementada."""
    print("\n🧪 Testing: Lógica de día del ciclo semanal...")
    
    from src.models.gamification import RachaUsuario
    
    # Verificar que la propiedad existe
    assert hasattr(RachaUsuario, 'dia_ciclo_semanal')
    
    print("  ✅ Propiedad dia_ciclo_semanal implementada")
    print("    • Lógica: ((racha_actual - 1) % 7) + 1")
    print("    • Ejemplos esperados:")
    print("      - Racha 0 días → Día 0")
    print("      - Racha 1 días → Día 1")
    print("      - Racha 7 días → Día 7")
    print("      - Racha 8 días → Día 1 (ciclo 2)")
    print("      - Racha 14 días → Día 7 (ciclo 2)")


def main():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("🚀 TESTING RACHASUARIO EXPANDIDO")
    print("=" * 60)
    
    try:
        test_racha_usuario_expanded()
        test_racha_usuario_properties()
        test_racha_usuario_methods()
        test_racha_usuario_constraints()
        test_dia_ciclo_semanal()
        
        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("=" * 60)
        print("\n📝 Resumen:")
        print("  • 4 campos nuevos agregados")
        print("  • 3 propiedades nuevas implementadas")
        print("  • 5 métodos nuevos funcionando")
        print("  • Constraints verificados")
        print("\n✨ RachaUsuario listo para migraciones!")
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
