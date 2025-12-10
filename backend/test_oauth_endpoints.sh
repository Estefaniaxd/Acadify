#!/bin/bash

# Script de prueba para OAuth endpoints
# Verifica que todos los endpoints estén funcionando correctamente

echo "🔍 Probando OAuth Endpoints..."
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_URL="http://localhost:8000/api/v1"

# Función para probar un endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint" 2>&1)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ OK${NC} (Status: $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $response)"
        return 1
    fi
}

# Verificar que el servidor esté corriendo
echo "1. Verificando que el servidor backend esté corriendo..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" 2>&1 | grep -q "200\|404"; then
    echo -e "${GREEN}✓ Servidor backend está corriendo${NC}"
else
    echo -e "${RED}✗ Servidor backend NO está corriendo${NC}"
    echo ""
    echo "Por favor inicia el servidor con:"
    echo "  cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend"
    echo "  uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
    exit 1
fi

echo ""
echo "2. Probando endpoints de OAuth..."

# Test 1: Login endpoint (debe redirigir - 307)
test_endpoint "/auth/google/login" "307" "Google Login (debe redirigir)"

# Test 2: Callback sin código (debe dar error - 422)
test_endpoint "/auth/google/callback" "422" "Callback sin código (debe fallar)"

# Test 3: Status sin autenticación (debe dar 401)
test_endpoint "/auth/google/status" "401" "Status sin auth (debe dar 401)"

# Test 4: Unlink sin autenticación (debe dar 401)
curl -s -o /dev/null -w "%{http_code}" -X DELETE "$BASE_URL/auth/google/unlink" 2>&1 | grep -q "401"
if [ $? -eq 0 ]; then
    echo -e "Testing Unlink sin auth... ${GREEN}✓ OK${NC} (Status: 401)"
else
    echo -e "Testing Unlink sin auth... ${RED}✗ FAIL${NC}"
fi

echo ""
echo "3. Verificando configuración de OAuth..."

# Verificar que las variables de entorno estén configuradas
if grep -q "GOOGLE_CLIENT_ID" /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/.env 2>/dev/null; then
    echo -e "${GREEN}✓ GOOGLE_CLIENT_ID configurado${NC}"
else
    echo -e "${RED}✗ GOOGLE_CLIENT_ID NO configurado${NC}"
fi

if grep -q "GOOGLE_CLIENT_SECRET" /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/.env 2>/dev/null; then
    echo -e "${GREEN}✓ GOOGLE_CLIENT_SECRET configurado${NC}"
else
    echo -e "${RED}✗ GOOGLE_CLIENT_SECRET NO configurado${NC}"
fi

if grep -q "ENABLE_OAUTH=true" /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/.env 2>/dev/null; then
    echo -e "${GREEN}✓ ENABLE_OAUTH=true${NC}"
else
    echo -e "${RED}✗ ENABLE_OAUTH NO está en true${NC}"
fi

echo ""
echo "4. Probando URL completa de login..."
echo "URL: $BASE_URL/auth/google/login"

# Obtener la URL de redirección
redirect_url=$(curl -s -I "$BASE_URL/auth/google/login" 2>&1 | grep -i "location:" | cut -d' ' -f2 | tr -d '\r')

if [[ $redirect_url == *"accounts.google.com"* ]]; then
    echo -e "${GREEN}✓ Redirige correctamente a Google${NC}"
    echo "  URL de redirección: ${redirect_url:0:80}..."
else
    echo -e "${YELLOW}⚠ No se detectó redirección a Google${NC}"
    echo "  Respuesta: $redirect_url"
fi

echo ""
echo "✅ Pruebas completadas"
echo ""
echo "📝 Próximos pasos:"
echo "  1. Asegúrate de que el backend esté corriendo"
echo "  2. Asegúrate de que el frontend esté corriendo"
echo "  3. Abre http://localhost:3000/login en tu navegador"
echo "  4. Haz clic en 'Continuar con Google'"
echo "  5. Deberías ser redirigido a Google para autorizar"
