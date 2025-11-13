#!/bin/bash

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

BASE_URL="http://127.0.0.1:8000"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}🧪  TESTING AUTHENTICATION ENDPOINTS${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Test 1: Health Check
echo -e "${YELLOW}[TEST 1] Health Check${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ Server is running${NC}"
else
    echo -e "${RED}❌ Server error (HTTP $RESPONSE)${NC}"
    exit 1
fi
echo ""

# Test 2: Register Users
echo -e "${YELLOW}[TEST 2] Register Users${NC}"

# Docente
echo -e "${BLUE}Registering Docente...${NC}"
curl -X POST "$BASE_URL/auth/register" \
-H "Content-Type: application/json" \
-d "{
  \"correo_institucional\": \"docente.${TIMESTAMP}@universidad.edu.co\",
  \"username\": \"docente_${TIMESTAMP}\",
  \"nombres\": \"María\",
  \"apellidos\": \"García López\",
  \"tipo_documento\": \"CC\",
  \"numero_documento\": \"1234567890\",
  \"password\": \"DocenteTest123!\",
  \"rol\": \"docente\",
  \"telefono\": \"+57 300 123 4567\",
  \"descripcion\": \"Docente de matemáticas\"
}" -s -w "\nHTTP Status: %{http_code}\n\n" | python3 -m json.tool 2>/dev/null || echo "Response not JSON"

# Estudiante
echo -e "${BLUE}Registering Estudiante...${NC}"
curl -X POST "$BASE_URL/auth/register" \
-H "Content-Type: application/json" \
-d "{
  \"correo_institucional\": \"estudiante.${TIMESTAMP}@universidad.edu.co\",
  \"username\": \"estudiante_${TIMESTAMP}\",
  \"nombres\": \"Juan\",
  \"apellidos\": \"Pérez González\",
  \"tipo_documento\": \"TI\",
  \"numero_documento\": \"9876543210\",
  \"password\": \"EstudianteTest123!\",
  \"rol\": \"estudiante\",
  \"telefono\": \"+57 301 234 5678\",
  \"descripcion\": \"Estudiante de ingeniería\"
}" -s -w "\nHTTP Status: %{http_code}\n\n" | python3 -m json.tool 2>/dev/null || echo "Response not JSON"

# Coordinador
echo -e "${BLUE}Registering Coordinador...${NC}"
curl -X POST "$BASE_URL/auth/register" \
-H "Content-Type: application/json" \
-d "{
  \"correo_institucional\": \"coordinador.${TIMESTAMP}@universidad.edu.co\",
  \"username\": \"coordinador_${TIMESTAMP}\",
  \"nombres\": \"Ana María\",
  \"apellidos\": \"Martínez Gómez\",
  \"tipo_documento\": \"CC\",
  \"numero_documento\": \"5555555555\",
  \"password\": \"CoordinadorTest123!\",
  \"rol\": \"coordinador\",
  \"telefono\": \"+57 302 345 6789\",
  \"descripcion\": \"Coordinadora académica\"
}" -s -w "\nHTTP Status: %{http_code}\n\n" | python3 -m json.tool 2>/dev/null || echo "Response not JSON"

echo ""
echo -e "${GREEN}✅ Registration tests completed${NC}"
echo ""

# Test 3: Login
echo -e "${YELLOW}[TEST 3] Login${NC}"
LOGIN_RESPONSE=$(curl -X POST "$BASE_URL/auth/login" \
-H "Content-Type: application/json" \
-d "{
  \"identifier\": \"docente_${TIMESTAMP}\",
  \"password\": \"DocenteTest123!\"
}" -s)

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract token if present
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✅ Login successful${NC}"
    echo ""
    
    # Test 4: Auth /me
    echo -e "${YELLOW}[TEST 4] Get Current User (/auth/me)${NC}"
    curl -X GET "$BASE_URL/auth/me" \
    -H "Authorization: Bearer $TOKEN" \
    -s | python3 -m json.tool
    echo ""
    echo -e "${GREEN}✅ /auth/me successful${NC}"
else
    echo -e "${RED}❌ Login failed${NC}"
fi

echo ""
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}✅  Tests completed${NC}"
echo -e "${BLUE}===============================================${NC}"
