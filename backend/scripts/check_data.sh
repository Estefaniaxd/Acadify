#!/bin/bash

echo "🔍 Consultando datos de la base de datos..."

# Variables de conexión
DB_NAME="acadify_db"
DB_USER="acadify_user"
DB_HOST="localhost"
DB_PORT="5432"
export PGPASSWORD="acadify_password"

# Función para ejecutar SQL
execute_query() {
    echo "🔄 $1"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "$2"
    echo ""
}

echo "📚 CURSOS EXISTENTES:"
execute_query "Códigos de cursos disponibles" "
SELECT curso_id, nombre, codigo_acceso, modalidad, fecha_inicio, fecha_fin 
FROM \"Curso\" 
ORDER BY fecha_creacion DESC;"

echo "🏫 INSTITUCIONES EXISTENTES:"
execute_query "Instituciones en el sistema" "
SELECT institucion_id, nombre, codigo, estado 
FROM \"Institucion\" 
ORDER BY fecha_creacion DESC;"

echo "📋 PROGRAMAS EXISTENTES:"
execute_query "Programas por institución" "
SELECT p.programa_id, p.nombre as programa, i.nombre as institucion, p.nivel, p.tipo
FROM \"Programa\" p
JOIN \"Institucion\" i ON p.institucion_id = i.institucion_id
ORDER BY i.nombre, p.nombre;"

echo "👥 USUARIOS POR INSTITUCIÓN:"
execute_query "Usuarios y sus programas/instituciones" "
SELECT u.usuario_id, u.nombre_completo, u.rol, u.email,
       p.nombre as programa, i.nombre as institucion
FROM \"Usuario\" u
LEFT JOIN \"Estudiante\" e ON u.usuario_id = e.estudiante_id
LEFT JOIN \"Programa\" p ON e.programa_id = p.programa_id
LEFT JOIN \"Institucion\" i ON p.institucion_id = i.institucion_id
ORDER BY i.nombre, u.nombre_completo
LIMIT 10;"

echo "🔗 RELACIÓN CURSOS-INSTITUCIONES:"
execute_query "Cursos y sus instituciones" "
SELECT c.nombre as curso, c.codigo_acceso, i.nombre as institucion, p.nombre as programa
FROM \"Curso\" c
JOIN \"Programa\" p ON c.programa_id = p.programa_id  
JOIN \"Institucion\" i ON p.institucion_id = i.institucion_id
ORDER BY i.nombre, c.nombre;"