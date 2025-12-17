#!/bin/bash

# =====================================================
# Script para ejecutar procedimientos almacenados
# Sistema: Acadify
# Base de datos: PostgreSQL
# =====================================================

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Instalación de Procedimientos Almacenados${NC}"
echo -e "${BLUE}  Sistema: Acadify${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Obtener credenciales de la base de datos
# Lee el archivo .env automáticamente
if [ -f ../.env ]; then
    export $(cat ../.env | grep -E '^DATABASE_URL=' | xargs)
fi

# Si DATABASE_URL está configurada, usarla
if [ -n "$DATABASE_URL" ]; then
    echo -e "${GREEN}[1/3] Usando DATABASE_URL configurada${NC}"
    DB_CONNECTION=$DATABASE_URL
else
    # Solicitar credenciales manualmente
    echo -e "${BLUE}Por favor ingresa las credenciales de PostgreSQL:${NC}"
    read -p "Host (localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "Puerto (5432): " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -p "Base de datos: " DB_NAME
    
    read -p "Usuario: " DB_USER
    
    read -sp "Contraseña: " DB_PASS
    echo ""
    
    DB_CONNECTION="postgresql://$DB_USER:$DB_PASS@$DB_HOST:$DB_PORT/$DB_NAME"
fi

echo ""
echo -e "${GREEN}[2/3] Creando tabla de auditoría...${NC}"
psql "$DB_CONNECTION" -f create_auditoria_table.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tabla de auditoría creada exitosamente${NC}"
else
    echo -e "${RED}✗ Error al crear tabla de auditoría${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[3/3] Instalando procedimientos almacenados...${NC}"
psql "$DB_CONNECTION" -f stored_procedures.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Procedimientos almacenados instalados exitosamente${NC}"
else
    echo -e "${RED}✗ Error al instalar procedimientos almacenados${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✓ Instalación completada exitosamente${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}Procedimientos disponibles:${NC}"
echo "  • sp_obtener_estadisticas_usuario(usuario_id)"
echo "  • sp_obtener_estadisticas_institucion(institucion_id)"
echo "  • sp_registrar_auditoria(usuario_id, accion, tabla, registro_id)"
echo "  • sp_invalidar_sesiones_usuario(usuario_id)"
echo "  • sp_obtener_dashboard_coordinador(usuario_id)"
echo "  • sp_obtener_top_estudiantes(limite)"
echo "  • sp_calcular_progreso_curso(curso_id, estudiante_id)"
echo "  • sp_reporte_actividad_diaria(fecha)"
echo ""
echo -e "${BLUE}Ejemplo de uso:${NC}"
echo "  SELECT * FROM sp_obtener_dashboard_coordinador('uuid-del-coordinador');"
echo ""
