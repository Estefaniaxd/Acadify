#!/bin/bash

# Test script para debugging del endpoint de entrega
# Prueba: POST /api/cursos/tareas/tareas/{id}/entregar con FormData

set -e

echo "🧪 Test de Entrega de Tarea - Debug"
echo "===================================="
echo ""

# Configuración
API_URL="http://127.0.0.1:8000"
EMAIL="estudiante1@example.com"
PASSWORD="Password123!"
TAREA_ID="9f5df54d-983f-4885-b4e6-2209c7a23d47"  # Cambia según tu ID real

# Paso 1: Login
echo "📝 PASO 1: Loguearse"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Login fallido. Respuesta:"
  echo "$LOGIN_RESPONSE" | jq .
  exit 1
fi

echo "✅ Token obtenido: ${ACCESS_TOKEN:0:20}..."
echo ""

# Paso 2: Crear archivo temporal de test
echo "📝 PASO 2: Crear archivo de test"
TEST_FILE=$(mktemp)
echo "Contenido de prueba - $(date)" > "$TEST_FILE"
echo "✅ Archivo creado: $TEST_FILE"
echo ""

# Paso 3: Enviar entrega
echo "📝 PASO 3: Enviar entrega (POST /api/cursos/tareas/tareas/$TAREA_ID/entregar)"
echo ""

RESPONSE=$(curl -s -X POST "$API_URL/api/cursos/tareas/tareas/$TAREA_ID/entregar" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "contenido=Test entrega con archivo" \
  -F "archivo=@$TEST_FILE" \
  -w "\n%{http_code}")

# Separar body y status code
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

echo "HTTP Status: $HTTP_CODE"
echo ""
echo "Response Body:"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""

# Verificar resultado
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
  echo "✅ Entrega exitosa"
else
  echo "❌ Error: HTTP $HTTP_CODE"
fi

# Cleanup
rm -f "$TEST_FILE"
