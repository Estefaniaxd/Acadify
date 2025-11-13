#!/bin/bash
# ============================================================================
# Script de Ejecución - Migración Sistema de Misiones
# ============================================================================

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Sistema de Misiones - Migración DB${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Verificar si existe el archivo .env
if [ ! -f "../.env" ]; then
    echo -e "${RED}❌ Error: No se encuentra el archivo .env${NC}"
    echo -e "${YELLOW}Por favor, crea un archivo .env con las credenciales de la base de datos${NC}"
    exit 1
fi

# Cargar variables de entorno
export $(grep -v '^#' ../.env | xargs)

# Verificar variables requeridas
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL no está definida en .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Variables de entorno cargadas"
echo ""

# Extraer componentes de DATABASE_URL
# Formato: postgresql://usuario:password@host:puerto/database
DB_USER=$(echo $DATABASE_URL | sed -n 's|.*://\([^:]*\):.*|\1|p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')
DB_HOST=$(echo $DATABASE_URL | sed -n 's|.*@\([^:]*\):.*|\1|p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's|.*/\([^?]*\).*|\1|p')

echo -e "${BLUE}Configuración de Base de Datos:${NC}"
echo -e "  Host: ${DB_HOST}"
echo -e "  Puerto: ${DB_PORT}"
echo -e "  Database: ${DB_NAME}"
echo -e "  Usuario: ${DB_USER}"
echo ""

# Preguntar confirmación
read -p "$(echo -e ${YELLOW}"¿Ejecutar migración? (s/N): "${NC})" -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${RED}Migración cancelada${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}Ejecutando migración...${NC}"
echo ""

# Ejecutar migración
PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f 001_sistema_misiones.sql

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  ✓ Migración completada exitosamente${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "${BLUE}Verificando datos...${NC}"
    
    # Verificar misiones creadas
    PGPASSWORD=$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT COUNT(*) as total_misiones FROM misiones;"
    
    echo ""
    echo -e "${GREEN}✓ Sistema de misiones listo para usar${NC}"
else
    echo ""
    echo -e "${RED}============================================${NC}"
    echo -e "${RED}  ❌ Error al ejecutar la migración${NC}"
    echo -e "${RED}============================================${NC}"
    exit 1
fi
