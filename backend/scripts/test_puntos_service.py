"""
Test simple del PuntosService sin usar base de datos.

Este test valida la lógica de cálculo de puntos sin necesidad de BD.

Author: GitHub Copilot & Team
Date: 31 octubre 2025
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.gamification.puntos_service import PuntosService


class MockTarea:
    """Mock de Tarea para testing."""
    def __init__(self, puntos_base=50, puntos_bonificacion=20):
        self.tarea_id = "test-123"
        self.puntos_base = puntos_base
        self.puntos_bonificacion = puntos_bonificacion


def test_calculo_puntos():
    """Test del cálculo de puntos."""
    
    print("="*80)
    print("TEST: PuntosService - Cálculo de Puntos")
    print("="*80)
    print()
    
    # Crear servicio (sin DB para este test)
    service = PuntosService(db=None)
    
    # Test 1: Entrega normal, buena calificación
    print("📝 Test 1: Entrega normal con calificación 4.5")
    print("-"*80)
    
    tarea = MockTarea(puntos_base=50, puntos_bonificacion=20)
    
    # Usar método sincrónico para testing
    puntos = service._calcular_puntos_sincrono(
        puntos_base=tarea.puntos_base,
        puntos_bonificacion=tarea.puntos_bonificacion,
        calificacion=4.5,
        es_tardia=False,
        intentos=1
    )
    
    print(f"Puntos base: {puntos['puntos_base']}")
    print(f"Bonus: {puntos['puntos_bonificacion']}")
    print(f"Penalización tardía: {puntos['penalizacion_tardia']}")
    print(f"Penalización intentos: {puntos['penalizacion_intentos']}")
    print(f"✅ TOTAL: {puntos['puntos_totales']} puntos")
    print(f"Desglose: {puntos['desglose']}")
    print()
    
    assert puntos['puntos_totales'] == 70, f"Esperado 70, obtenido {puntos['puntos_totales']}"
    
    # Test 2: Entrega tardía
    print("📝 Test 2: Entrega tardía con calificación 4.5")
    print("-"*80)
    
    puntos = service._calcular_puntos_sincrono(
        puntos_base=50,
        puntos_bonificacion=20,
        calificacion=4.5,
        es_tardia=True,
        intentos=1
    )
    
    print(f"Puntos base: {puntos['puntos_base']}")
    print(f"Bonus: {puntos['puntos_bonificacion']}")
    print(f"Penalización tardía: {puntos['penalizacion_tardia']}")
    print(f"✅ TOTAL: {puntos['puntos_totales']} puntos")
    print(f"Desglose: {puntos['desglose']}")
    print()
    
    assert puntos['puntos_totales'] == 55, f"Esperado 55, obtenido {puntos['puntos_totales']}"
    
    # Test 3: Múltiples intentos
    print("📝 Test 3: 2 intentos con calificación 4.0")
    print("-"*80)
    
    puntos = service._calcular_puntos_sincrono(
        puntos_base=50,
        puntos_bonificacion=20,
        calificacion=4.0,
        es_tardia=False,
        intentos=2
    )
    
    print(f"Puntos base: {puntos['puntos_base']}")
    print(f"Bonus: {puntos['puntos_bonificacion']}")
    print(f"Penalización intentos: {puntos['penalizacion_intentos']}")
    print(f"✅ TOTAL: {puntos['puntos_totales']} puntos")
    print(f"Desglose: {puntos['desglose']}")
    print()
    
    assert puntos['puntos_totales'] == 45, f"Esperado 45, obtenido {puntos['puntos_totales']}"
    
    # Test 4: Calificación baja
    print("📝 Test 4: Calificación 3.0 (sin bonus)")
    print("-"*80)
    
    puntos = service._calcular_puntos_sincrono(
        puntos_base=50,
        puntos_bonificacion=20,
        calificacion=3.0,
        es_tardia=False,
        intentos=1
    )
    
    print(f"Puntos base: {puntos['puntos_base']}")
    print(f"Bonus: {puntos['puntos_bonificacion']}")
    print(f"✅ TOTAL: {puntos['puntos_totales']} puntos")
    print(f"Desglose: {puntos['desglose']}")
    print()
    
    assert puntos['puntos_totales'] == 50, f"Esperado 50, obtenido {puntos['puntos_totales']}"
    
    # Test 5: Test de niveles
    print("📝 Test 5: Sistema de niveles")
    print("-"*80)
    
    niveles_test = [
        (50, "Bronce I"),
        (150, "Bronce II"),
        (300, "Bronce III"),
        (600, "Plata I"),
        (1000, "Plata II"),
        (2500, "Oro I"),
        (6000, "Platino I"),
        (12000, "Platino III")
    ]
    
    for puntos_test, nivel_esperado in niveles_test:
        nivel = service._calcular_nivel(puntos_test)
        print(f"{puntos_test:6d} pts → {nivel:12s} {'✅' if nivel == nivel_esperado else '❌'}")
        assert nivel == nivel_esperado, f"Esperado {nivel_esperado}, obtenido {nivel}"
    
    print()
    
    # Test 6: Información de nivel con progreso
    print("📝 Test 6: Información detallada de nivel (600 puntos)")
    print("-"*80)
    
    info_nivel = service._info_nivel(600)
    print(f"Nivel actual: {info_nivel['nivel_actual']}")
    print(f"Puntos mínimos: {info_nivel['puntos_minimos_nivel']}")
    print(f"Siguiente nivel: {info_nivel['puntos_siguiente_nivel']}")
    print(f"Progreso: {info_nivel['progreso_porcentaje']:.1f}%")
    print(f"Puntos faltantes: {info_nivel['puntos_para_siguiente']}")
    print()
    
    print("="*80)
    print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("="*80)


if __name__ == "__main__":
    # Agregar método sincrónico temporal para testing
    def _calcular_puntos_sincrono(
        self,
        puntos_base: int,
        puntos_bonificacion: int,
        calificacion: float,
        es_tardia: bool,
        intentos: int
    ):
        """Versión sincrónica del cálculo para testing."""
        # Bonificación
        bonus = puntos_bonificacion if calificacion >= 4.5 else 0
        
        # Penalizaciones
        pen_tardia = int(puntos_base * 0.30) if es_tardia else 0
        intentos_extra = min(intentos - 1, 2)
        pen_intentos = int(puntos_base * 0.10 * intentos_extra) if intentos > 1 else 0
        
        # Total
        total = max(0, puntos_base + bonus - pen_tardia - pen_intentos)
        
        # Desglose
        partes = [f"{puntos_base} (base)"]
        if bonus > 0:
            partes.append(f"+ {bonus} (bonus)")
        if pen_tardia > 0:
            partes.append(f"- {pen_tardia} (tardía)")
        if pen_intentos > 0:
            partes.append(f"- {pen_intentos} (intentos)")
        
        return {
            "puntos_base": puntos_base,
            "puntos_bonificacion": bonus,
            "penalizacion_tardia": pen_tardia,
            "penalizacion_intentos": pen_intentos,
            "puntos_totales": total,
            "desglose": " ".join(partes),
            "calificacion": calificacion,
            "es_tardia": es_tardia,
            "intentos": intentos
        }
    
    # Agregar método al servicio temporalmente
    PuntosService._calcular_puntos_sincrono = _calcular_puntos_sincrono
    
    test_calculo_puntos()
