-- ========================================
-- SCRIPT SQL DE DIAGNÓSTICO
-- Bug de Archivos en Entregas de Tareas
-- ========================================
-- Ejecutar en: psql -U acadify_user -d acadify -f diagnostico_archivos_entregas.sql
--
-- Objetivo: Verificar que archivos_adicionales se están guardando correctamente
--           con todos los archivos y sus nombres originales

-- ========================================
-- 1. VERIFICAR ENTREGAS RECIENTES
-- ========================================
\echo '🔍 1. VERIFICANDO ENTREGAS RECIENTES (últimas 10):'
\echo ''

SELECT 
    e.entrega_id,
    e.tarea_id,
    u.nombres || ' ' || u.apellidos AS estudiante,
    e.estado,
    e.fecha_entrega,
    e.archivo_url AS primer_archivo_legacy,
    CASE 
        WHEN e.archivos_adicionales IS NULL THEN 'NULL'
        WHEN e.archivos_adicionales::text = '' THEN 'EMPTY'
        ELSE 'EXISTS'
    END AS archivos_adicionales_status,
    LENGTH(e.archivos_adicionales::text) AS json_length_bytes
FROM entregas_tareas e
JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
ORDER BY e.fecha_entrega DESC NULLS LAST
LIMIT 10;

\echo ''
\echo '=========================================='
\echo ''

-- ========================================
-- 2. VERIFICAR ESTRUCTURA DE JSON archivos_adicionales
-- ========================================
\echo '🔍 2. VERIFICANDO ESTRUCTURA JSON DE archivos_adicionales:'
\echo ''

WITH json_analysis AS (
    SELECT 
        e.entrega_id,
        e.estado,
        e.archivos_adicionales,
        CASE 
            WHEN e.archivos_adicionales IS NULL THEN 0
            WHEN jsonb_typeof(e.archivos_adicionales::jsonb) = 'object' AND 
                 e.archivos_adicionales::jsonb ? 'archivos' THEN 
                jsonb_array_length((e.archivos_adicionales::jsonb->'archivos')::jsonb)
            ELSE 0
        END AS total_archivos_en_json
    FROM entregas_tareas e
    WHERE e.archivos_adicionales IS NOT NULL
    ORDER BY e.fecha_entrega DESC NULLS LAST
    LIMIT 10
)
SELECT 
    entrega_id,
    estado,
    total_archivos_en_json,
    CASE 
        WHEN total_archivos_en_json = 0 THEN '❌ JSON MAL FORMADO'
        WHEN total_archivos_en_json = 1 THEN '⚠️ Solo 1 archivo'
        ELSE '✅ ' || total_archivos_en_json || ' archivos'
    END AS diagnostico
FROM json_analysis;

\echo ''
\echo '=========================================='
\echo ''

-- ========================================
-- 3. VERIFICAR METADATA DE ARCHIVOS (nombre_original)
-- ========================================
\echo '🔍 3. VERIFICANDO METADATA DE ARCHIVOS (nombre_original presente):'
\echo ''

SELECT 
    e.entrega_id,
    e.estado,
    jsonb_pretty(e.archivos_adicionales::jsonb) AS archivos_metadata_formateado
FROM entregas_tareas e
WHERE e.archivos_adicionales IS NOT NULL
ORDER BY e.fecha_entrega DESC NULLS LAST
LIMIT 3;

\echo ''
\echo '=========================================='
\echo ''

-- ========================================
-- 4. BUSCAR ENTREGAS CON ARCHIVOS SIN nombre_original
-- ========================================
\echo '🔍 4. BUSCANDO ENTREGAS CON ARCHIVOS SIN nombre_original:'
\echo ''

WITH archivos_sin_nombre AS (
    SELECT 
        e.entrega_id,
        e.estado,
        e.fecha_entrega,
        archivo_item
    FROM entregas_tareas e,
    LATERAL jsonb_array_elements((e.archivos_adicionales::jsonb->'archivos')::jsonb) AS archivo_item
    WHERE e.archivos_adicionales IS NOT NULL
      AND NOT (archivo_item ? 'nombre_original')  -- No tiene key nombre_original
)
SELECT 
    entrega_id,
    estado,
    fecha_entrega,
    COUNT(*) AS archivos_sin_nombre_original,
    jsonb_pretty(jsonb_agg(archivo_item)) AS archivos_problematicos
FROM archivos_sin_nombre
GROUP BY entrega_id, estado, fecha_entrega
ORDER BY fecha_entrega DESC NULLS LAST
LIMIT 5;

\echo ''
\echo '=========================================='
\echo ''

-- ========================================
-- 5. ESTADÍSTICAS GENERALES
-- ========================================
\echo '📊 5. ESTADÍSTICAS GENERALES:'
\echo ''

SELECT 
    COUNT(*) AS total_entregas,
    COUNT(CASE WHEN archivos_adicionales IS NOT NULL THEN 1 END) AS con_archivos_adicionales,
    COUNT(CASE WHEN archivos_adicionales IS NULL THEN 1 END) AS sin_archivos_adicionales,
    COUNT(CASE WHEN estado = 'entregada' THEN 1 END) AS estado_entregada,
    COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) AS estado_cancelada,
    ROUND(
        AVG(
            CASE 
                WHEN archivos_adicionales IS NOT NULL AND 
                     jsonb_typeof(archivos_adicionales::jsonb) = 'object' AND 
                     archivos_adicionales::jsonb ? 'archivos' 
                THEN jsonb_array_length((archivos_adicionales::jsonb->'archivos')::jsonb)
                ELSE 0
            END
        )::numeric, 
        2
    ) AS promedio_archivos_por_entrega
FROM entregas_tareas;

\echo ''
\echo '=========================================='
\echo ''

-- ========================================
-- 6. VERIFICAR ENTREGA ESPECÍFICA (Cambiar ID)
-- ========================================
\echo '🔍 6. PLANTILLA PARA VERIFICAR ENTREGA ESPECÍFICA:'
\echo '   (Reemplaza el entrega_id con el que quieras investigar)'
\echo ''

-- Descomenta y reemplaza el ID para usar:
/*
\set entrega_id '\'tu-entrega-id-aqui\''

SELECT 
    e.entrega_id,
    t.titulo AS tarea,
    u.nombres || ' ' || u.apellidos AS estudiante,
    e.estado,
    e.fecha_entrega,
    e.archivo_url AS primer_archivo_legacy,
    jsonb_pretty(e.archivos_adicionales::jsonb) AS archivos_metadata_completo,
    jsonb_array_length((e.archivos_adicionales::jsonb->'archivos')::jsonb) AS total_archivos,
    (
        SELECT string_agg(
            archivo->>'nombre_original' || ' (' || archivo->>'url' || ')', 
            ', '
        )
        FROM jsonb_array_elements((e.archivos_adicionales::jsonb->'archivos')::jsonb) AS archivo
    ) AS lista_archivos_con_nombres
FROM entregas_tareas e
JOIN tareas t ON e.tarea_id = t.tarea_id
JOIN "Usuario" u ON e.estudiante_id = u.usuario_id
WHERE e.entrega_id = :entrega_id;
*/

\echo ''
\echo '=========================================='
\echo '✅ DIAGNÓSTICO COMPLETADO'
\echo '=========================================='
\echo ''
\echo 'INTERPRETACIÓN DE RESULTADOS:'
\echo ''
\echo '1. Si "total_archivos_en_json" = 1 pero subiste 4:'
\echo '   ➜ Problema en el guardado inicial (INSERT)'
\echo '   ➜ Verificar logs del backend en entregarTarea()'
\echo ''
\echo '2. Si "total_archivos_en_json" = 4 pero frontend muestra 1:'
\echo '   ➜ Problema en el parsing (obtenerEntrega())'
\echo '   ➜ Verificar logs del backend con el logging agregado'
\echo ''
\echo '3. Si archivos no tienen "nombre_original":'
\echo '   ➜ Problema en la metadata del curso_tareas.py'
\echo '   ➜ Verificar que meta dict incluya nombre_original'
\echo ''
\echo '4. Si estado = "cancelada" y archivos desaparecen:'
\echo '   ➜ Problema resuelto con Fix #4 (reusa archivos)'
\echo ''
\echo 'PRÓXIMOS PASOS:'
\echo '1. Ejecutar este script: psql -U acadify_user -d acadify -f diagnostico_archivos_entregas.sql'
\echo '2. Revisar logs del backend después de subir 4 archivos'
\echo '3. Ejecutar test end-to-end completo'
\echo ''
