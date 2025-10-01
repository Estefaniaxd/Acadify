#!/bin/bash

# Script para insertar datos de prueba en PostgreSQL
echo "🔄 Insertando datos de prueba en la base de datos..."

# Variables de conexión (ajustar según tu configuración)
DB_NAME="acadify_db"
DB_USER="acadify_user"
DB_HOST="localhost"
DB_PORT="5432"

# Leer contraseña de variables de entorno o usar default
export PGPASSWORD="acadify_password"

# Función para ejecutar SQL
execute_sql() {
    echo "Ejecutando: $1"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "$1"
}

# Crear usuario de prueba
echo "📝 Creando usuario de prueba..."
execute_sql "INSERT INTO \"Usuario\" (
    nombres, apellidos, nombre_completo, email, 
    correo_institucional, username, password_hash, 
    tipo_documento, numero_documento, telefono, 
    fecha_nacimiento, genero, rol, estado, fecha_creacion
) VALUES (
    'Usuario', 'Test', 'Usuario Test', 'test@acadify.com',
    'test@acadify.com', 'test_user', encode(digest('test123', 'sha256'), 'hex'),
    'cedula', '12345678', '1234567890',
    '1990-01-01', 'masculino', 'estudiante', 'activo', CURRENT_TIMESTAMP
) ON CONFLICT (email) DO NOTHING;"

# Obtener ID del usuario
USER_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT usuario_id FROM \"Usuario\" WHERE email = 'test@acadify.com';" | xargs)
echo "Usuario creado/encontrado con ID: $USER_ID"

# Crear cursos de prueba
echo "📚 Creando cursos de prueba..."

# Matemáticas Avanzadas (activo)
execute_sql "INSERT INTO \"Curso\" (
    nombre, descripcion, codigo_acceso, modalidad,
    fecha_inicio, fecha_fin, estado, creditos,
    fecha_creacion, horas_academicas
) VALUES (
    'Matemáticas Avanzadas', 
    'Curso avanzado de cálculo diferencial e integral',
    'MAT001', 'Presencial',
    CURRENT_DATE - INTERVAL '30 days',
    CURRENT_DATE + INTERVAL '60 days',
    'activo', 4, CURRENT_TIMESTAMP, 48
) ON CONFLICT (codigo_acceso) DO NOTHING;"

# Programación Orientada a Objetos (próximo)
execute_sql "INSERT INTO \"Curso\" (
    nombre, descripcion, codigo_acceso, modalidad,
    fecha_inicio, fecha_fin, estado, creditos,
    fecha_creacion, horas_academicas
) VALUES (
    'Programación Orientada a Objetos',
    'Fundamentos de POO con Java y Python',
    'POO002', 'Virtual',
    CURRENT_DATE + INTERVAL '15 days',
    CURRENT_DATE + INTERVAL '120 days',
    'próximo', 3, CURRENT_TIMESTAMP, 48
) ON CONFLICT (codigo_acceso) DO NOTHING;"

# Base de Datos I (completado)
execute_sql "INSERT INTO \"Curso\" (
    nombre, descripcion, codigo_acceso, modalidad,
    fecha_inicio, fecha_fin, estado, creditos,
    fecha_creacion, horas_academicas
) VALUES (
    'Base de Datos I',
    'Diseño y administración de bases de datos relacionales',
    'BD003', 'Híbrida',
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE - INTERVAL '10 days',
    'completado', 3, CURRENT_TIMESTAMP, 48
) ON CONFLICT (codigo_acceso) DO NOTHING;"

# Obtener IDs de los cursos
MAT_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT curso_id FROM \"Curso\" WHERE codigo_acceso = 'MAT001';" | xargs)
POO_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT curso_id FROM \"Curso\" WHERE codigo_acceso = 'POO002';" | xargs)
BD_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT curso_id FROM \"Curso\" WHERE codigo_acceso = 'BD003';" | xargs)

echo "Cursos creados:"
echo "- Matemáticas Avanzadas ID: $MAT_ID"
echo "- POO ID: $POO_ID"
echo "- Base de Datos I ID: $BD_ID"

# Crear grupos para cada curso
echo "👥 Creando grupos..."

for CURSO_ID in $MAT_ID $POO_ID $BD_ID; do
    echo "Procesando curso ID: $CURSO_ID"
    
    # Crear grupo
    execute_sql "INSERT INTO \"Grupo\" (nombre, descripcion, estado, fecha_creacion)
    VALUES ('Grupo A - Curso $CURSO_ID', 'Grupo principal para el curso $CURSO_ID', 'activo', CURRENT_TIMESTAMP);"
    
    # Obtener ID del grupo recién creado
    GRUPO_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT grupo_id FROM \"Grupo\" WHERE nombre = 'Grupo A - Curso $CURSO_ID';" | xargs)
    
    # Vincular grupo con curso
    execute_sql "INSERT INTO \"GrupoCurso\" (grupo_id, curso_id, fecha_asignacion)
    VALUES ($GRUPO_ID, $CURSO_ID, CURRENT_DATE) ON CONFLICT DO NOTHING;"
    
    echo "Grupo $GRUPO_ID creado y vinculado al curso $CURSO_ID"
done

# Inscribir al usuario de prueba en MAT001 y POO002
echo "✏️ Inscribiendo usuario en cursos..."

# Obtener IDs de grupos
MAT_GRUPO=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT grupo_id FROM \"Grupo\" WHERE nombre = 'Grupo A - Curso $MAT_ID';" | xargs)
POO_GRUPO=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT grupo_id FROM \"Grupo\" WHERE nombre = 'Grupo A - Curso $POO_ID';" | xargs)

# Inscribir en Matemáticas
execute_sql "INSERT INTO \"EstudianteGrupo\" (grupo_id, estudiante_id, fecha_vinculacion)
VALUES ($MAT_GRUPO, $USER_ID, CURRENT_DATE) ON CONFLICT DO NOTHING;"

# Inscribir en POO
execute_sql "INSERT INTO \"EstudianteGrupo\" (grupo_id, estudiante_id, fecha_vinculacion)
VALUES ($POO_GRUPO, $USER_ID, CURRENT_DATE) ON CONFLICT DO NOTHING;"

echo "Usuario inscrito en Matemáticas y POO"

# Crear estudiantes adicionales para tener conteos realistas
echo "👨‍🎓 Creando estudiantes adicionales..."

for i in {1..3}; do
    execute_sql "INSERT INTO \"Usuario\" (
        nombres, apellidos, nombre_completo, email,
        correo_institucional, username, password_hash,
        tipo_documento, numero_documento, telefono,
        fecha_nacimiento, genero, rol, estado, fecha_creacion
    ) VALUES (
        'Estudiante$i', 'Test$i', 'Estudiante$i Test$i', 'estudiante$i@test.com',
        'estudiante$i@test.com', 'estudiante$i', 'dummy_hash',
        'cedula', '1234567$i', '0000000000',
        '1995-01-01', 'otro', 'estudiante', 'activo', CURRENT_TIMESTAMP
    ) ON CONFLICT (email) DO NOTHING;"
    
    # Obtener ID del estudiante
    EST_ID=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT usuario_id FROM \"Usuario\" WHERE email = 'estudiante$i@test.com';" | xargs)
    
    # Inscribir en todos los grupos
    execute_sql "INSERT INTO \"EstudianteGrupo\" (grupo_id, estudiante_id, fecha_vinculacion)
    VALUES ($MAT_GRUPO, $EST_ID, CURRENT_DATE) ON CONFLICT DO NOTHING;"
    
    execute_sql "INSERT INTO \"EstudianteGrupo\" (grupo_id, estudiante_id, fecha_vinculacion)
    VALUES ($POO_GRUPO, $EST_ID, CURRENT_DATE) ON CONFLICT DO NOTHING;"
done

echo "✅ Datos de prueba insertados exitosamente"
echo ""
echo "🔑 Credenciales de prueba:"
echo "Email: test@acadify.com"
echo "Password: test123"
echo ""
echo "📚 Códigos de cursos disponibles:"
echo "MAT001 - Matemáticas Avanzadas (activo) - 4 estudiantes"
echo "POO002 - Programación Orientada a Objetos (próximo) - 4 estudiantes" 
echo "BD003 - Base de Datos I (completado) - 3 estudiantes"
echo ""
echo "El usuario test@acadify.com está inscrito en MAT001 y POO002"