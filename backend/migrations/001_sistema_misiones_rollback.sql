-- ============================================================================
-- Rollback: Sistema de Misiones para Acadify
-- Fecha: 2025-11-09
-- Descripción: Elimina todas las tablas y ENUMs del sistema de misiones
-- ============================================================================

-- ADVERTENCIA: Este script eliminará TODOS los datos de misiones
-- Ejecutar solo si estás seguro de querer revertir la migración

BEGIN;

-- ============================================================================
-- PASO 1: Eliminar vistas
-- ============================================================================

DROP VIEW IF EXISTS vista_estadisticas_misiones_usuario CASCADE;

RAISE NOTICE 'Vistas eliminadas...';

-- ============================================================================
-- PASO 2: Eliminar funciones
-- ============================================================================

DROP FUNCTION IF EXISTS asignar_misiones_diarias_usuario(UUID) CASCADE;
DROP FUNCTION IF EXISTS expirar_misiones_vencidas() CASCADE;
DROP FUNCTION IF EXISTS actualizar_fecha_modificacion() CASCADE;

RAISE NOTICE 'Funciones eliminadas...';

-- ============================================================================
-- PASO 3: Eliminar triggers
-- ============================================================================

DROP TRIGGER IF EXISTS trigger_actualizar_misiones ON misiones;

RAISE NOTICE 'Triggers eliminados...';

-- ============================================================================
-- PASO 4: Eliminar tablas
-- ============================================================================

DROP TABLE IF EXISTS misiones_usuario CASCADE;
DROP TABLE IF EXISTS misiones CASCADE;

RAISE NOTICE 'Tablas eliminadas...';

-- ============================================================================
-- PASO 5: Eliminar ENUMs
-- ============================================================================

DROP TYPE IF EXISTS dificultad_mision CASCADE;
DROP TYPE IF EXISTS frecuencia_mision CASCADE;
DROP TYPE IF EXISTS estado_mision CASCADE;
DROP TYPE IF EXISTS tipo_mision CASCADE;

RAISE NOTICE 'ENUMs eliminados...';

-- ============================================================================
-- FINALIZACIÓN
-- ============================================================================

RAISE NOTICE '============================================';
RAISE NOTICE 'ROLLBACK COMPLETADO EXITOSAMENTE';
RAISE NOTICE '============================================';
RAISE NOTICE 'Todas las estructuras del sistema de misiones han sido eliminadas';
RAISE NOTICE '============================================';

COMMIT;
