#!/bin/bash
# Script para corregir TODAS las inconsistencias en vistas

cd /run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/database

echo "🔧 Aplicando correcciones a 03_vistas.sql..."

# 1. Tabla EstudianteGrupo (no estudiantes_grupos)
sed -i 's/estudiantes_grupos/EstudianteGrupo/g' 03_vistas.sql

# 2. CAST de estudiante_id VARCHAR a UUID en intentos_evaluacion
sed -i 's/ie\.estudiante_id = e\.estudiante_id/ie.estudiante_id::uuid = e.estudiante_id/g' 03_vistas.sql

# 3. tareas.curso_id no existe, pero sí grupo_id que tiene FK a Grupo que tiene curso_id
# Esta corrección es más compleja, necesitamos cambiar las queries que usan t.curso_id

# 4. evaluaciones.fecha_disponible → fecha_apertura
sed -i 's/ev\.fecha_disponible/ev.fecha_apertura/g' 03_vistas.sql

# 5. Curso no tiene nombre_curso, tiene nombre (ya corregido antes)

# 6. Código curso no existe, es codigo_curso
sed -i 's/c\.codigo_curso/c.codigo_curso/g' 03_vistas.sql

echo "✅ Correcciones aplicadas"
echo ""
echo "⚠️  NOTA: Las queries que usan t.curso_id necesitan corrección manual"
echo "   porque tareas tiene grupo_id, no curso_id directamente"
