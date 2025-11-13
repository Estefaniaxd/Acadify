#!/usr/bin/env fish
# Script para verificar que los endpoints de instituciones funcionen correctamente
# Uso: ./test_instituciones.sh

echo "🧪 Testing Instituciones Endpoints"
echo "=================================="
echo ""

# Colores
set -x GREEN '\033[0;32m'
set -x RED '\033[0;31m'
set -x YELLOW '\033[1;33m'
set -x NC '\033[0m' # No Color

# 1. Test GET /api/instituciones (público)
echo "1️⃣  Probando GET /api/instituciones (público)..."
set response (curl -s -w "\n%{http_code}" http://localhost:8000/api/instituciones?skip=0&limit=10)
set status_code (echo $response | tail -n1)
set body (echo $response | head -n-1)

if test $status_code -eq 200
    echo "$GREEN✅ GET /api/instituciones funciona correctamente$NC"
    echo "Instituciones encontradas:"
    echo $body | python -m json.tool 2>/dev/null || echo $body
else
    echo "$RED❌ Error: Status code $status_code$NC"
    echo "Respuesta: $body"
    if test $status_code -eq 405
        echo "$YELLOW⚠️  Error 405: El backend NO se reinició después de los cambios$NC"
        echo "$YELLOW   Ejecuta: Ctrl+C en el terminal del backend, luego:$NC"
        echo "$YELLOW   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000$NC"
    end
end

echo ""
echo "=================================="
echo ""

# 2. Test POST /admin/instituciones (requiere auth)
echo "2️⃣  Para probar POST /admin/instituciones necesitas:"
echo "  1. Hacer login como admin y obtener el token"
echo "  2. Ejecutar:"
echo ""
echo "     curl -X POST http://localhost:8000/admin/instituciones \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -H 'Authorization: Bearer <TU_TOKEN>' \\"
echo "       -d '{"
echo "         \"nombre\": \"Universidad de Prueba\","
echo "         \"tipo_institucion\": \"universidad\","
echo "         \"usa_programas\": true,"
echo "         \"nivel_educativo\": \"superior\","
echo "         \"sector\": \"publico\","
echo "         \"pais\": \"Colombia\","
echo "         \"correo_institucional\": \"info@universidad.edu.co\","
echo "         \"telefono\": \"+57 1 234 5678\""
echo "       }'"
echo ""

# 3. Verificar rutas en /docs
echo "3️⃣  Abre la documentación interactiva:"
echo "   http://localhost:8000/docs"
echo ""
echo "   Busca:"
echo "   - GET  /api/instituciones (debe estar listado)"
echo "   - POST /admin/instituciones (debe estar listado)"
echo ""

echo "=================================="
echo ""

if test $status_code -eq 200
    echo "$GREEN🎉 El endpoint GET funciona correctamente$NC"
    echo "$GREEN   Ahora prueba desde el frontend:$NC"
    echo "   1. Login como admin"
    echo "   2. Ve a /admin/instituciones"
    echo "   3. Crea una institución"
    echo "   4. Haz clic en el botón verde 'Invitar' para invitar coordinador"
else
    echo "$RED⚠️  PROBLEMA: El backend necesita reiniciarse$NC"
    echo "$RED   Los cambios en admin_institucion.py no están activos$NC"
end
