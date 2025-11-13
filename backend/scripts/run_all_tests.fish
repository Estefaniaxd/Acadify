#!/usr/bin/env fish
# Script para ejecutar todos los tests del sistema de evaluaciones
# Fecha: 31 de octubre 2025

echo "🧪 EJECUTANDO SUITE COMPLETA DE TESTS - SISTEMA DE EVALUACIONES"
echo "================================================================="
echo ""

# Colores
set -g GREEN '\033[0;32m'
set -g RED '\033[0;31m'
set -g YELLOW '\033[1;33m'
set -g BLUE '\033[0;34m'
set -g NC '\033[0m' # No Color

# Activar entorno virtual si existe
if test -d "venv"
    echo "📦 Activando entorno virtual..."
    source venv/bin/activate.fish
else
    echo "⚠️  No se encontró entorno virtual en ./venv"
end

# Configurar PYTHONPATH para que encuentre el módulo src
set -x PYTHONPATH (pwd):$PYTHONPATH
echo "✅ PYTHONPATH configurado: "(pwd)

echo ""
echo "📋 Tests a ejecutar:"
echo "  1. test_puntos_integration.py (15 tests)"
echo "  2. test_evaluacion_service.py (40+ tests)"
echo "  3. test_intento_service.py (30+ tests)"
echo "  4. test_evaluation_lifecycle.py (1 test E2E)"
echo "  5. test_calificacion_service.py (60+ tests)"
echo ""
echo "🎯 Total estimado: 145+ tests"
echo ""
echo "⏱️  Iniciando en 3 segundos..."
sleep 3

# Timestamp inicio
set START_TIME (date +%s)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 1/5: test_puntos_integration.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
env PYTHONPATH=(pwd) pytest TEST/test_puntos_integration.py -v --tb=short --color=yes
set TEST1_STATUS $status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 2/5: test_evaluacion_service.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
env PYTHONPATH=(pwd) pytest TEST/test_evaluacion_service.py -v --tb=short --color=yes
set TEST2_STATUS $status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 3/5: test_intento_service.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
env PYTHONPATH=(pwd) pytest TEST/test_intento_service.py -v --tb=short --color=yes
set TEST3_STATUS $status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 4/5: test_evaluation_lifecycle.py (E2E)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
env PYTHONPATH=(pwd) pytest TEST/test_evaluation_lifecycle.py -v -s --tb=short --color=yes -m e2e
set TEST4_STATUS $status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 TEST 5/5: test_calificacion_service.py"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
env PYTHONPATH=(pwd) pytest TEST/test_calificacion_service.py -v --tb=short --color=yes
set TEST5_STATUS $status

# Timestamp fin
set END_TIME (date +%s)
set DURATION (math $END_TIME - $START_TIME)

echo ""
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "📊 RESUMEN DE EJECUCIÓN"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Función para mostrar status
function print_status
    if test $argv[1] -eq 0
        echo -e "  ✅ $argv[2]: "$GREEN"PASSED"$NC
    else
        echo -e "  ❌ $argv[2]: "$RED"FAILED"$NC
    end
end

print_status $TEST1_STATUS "test_puntos_integration.py"
print_status $TEST2_STATUS "test_evaluacion_service.py"
print_status $TEST3_STATUS "test_intento_service.py"
print_status $TEST4_STATUS "test_evaluation_lifecycle.py"
print_status $TEST5_STATUS "test_calificacion_service.py"

echo ""
echo "⏱️  Tiempo total: $DURATION segundos"
echo ""

# Calcular resultado final
set TOTAL_FAILURES (math $TEST1_STATUS + $TEST2_STATUS + $TEST3_STATUS + $TEST4_STATUS + $TEST5_STATUS)

if test $TOTAL_FAILURES -eq 0
    echo -e $GREEN"🎉 TODOS LOS TESTS PASARON EXITOSAMENTE"$NC
    echo ""
    echo "✨ Estado del sistema: ESTABLE"
    echo "📈 Próximo paso: Continuar con tests pendientes"
    echo ""
    exit 0
else
    echo -e $RED"⚠️  ALGUNOS TESTS FALLARON"$NC
    echo ""
    echo "🔍 Revisa los logs arriba para más detalles"
    echo "💡 Ejecuta tests individuales con:"
    echo "   pytest TEST/<nombre_test>.py -v -s"
    echo ""
    exit 1
end
