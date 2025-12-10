#!/bin/bash

# Obtener un token válido primero
echo "🔐 Obteniendo token..."
TOKEN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"seed_a99e64_a3008df6@test.unan.local","password":"password123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ No se pudo obtener el token"
  echo "Respuesta: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:50}..."

# Crear un archivo temporal de prueba
echo "📄 Creando archivo de prueba..."
TEST_FILE="/tmp/test_archivo.txt"
echo "Este es un archivo de prueba para la entrega de tarea" > $TEST_FILE

# ID de la tarea (usar el mismo del frontend)
TAREA_ID="9f5df54d-983f-4885-b4e6-2209c7a23d47"

# Hacer request multipart/form-data
echo ""
echo "📤 Enviando request multipart/form-data..."
curl -v -X POST "http://127.0.0.1:8000/api/cursos/tareas/tareas/$TAREA_ID/entregar" \
  -H "Authorization: Bearer $TOKEN" \
  -F "contenido=Test desde curl" \
  -F "archivo=@$TEST_FILE"

echo ""
echo "✅ Test completado"
