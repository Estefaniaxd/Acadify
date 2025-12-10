-- Rollback for 20251113_create_asset_category_and_gender_enum.sql
-- WARNING: revisar antes de ejecutar. Ejecutar en staging primero.

BEGIN;

-- 1) Quitar columnas añadidas (si existen)
ALTER TABLE IF EXISTS avatar_asset
    DROP COLUMN IF EXISTS normalized_at,
    DROP COLUMN IF EXISTS is_normalized,
    DROP COLUMN IF EXISTS sha256,
    DROP COLUMN IF EXISTS canonical_path,
    DROP COLUMN IF EXISTS gender,
    DROP COLUMN IF EXISTS category_id;

-- 2) Eliminar índices creados (si existen)
DROP INDEX IF EXISTS ix_avatar_asset_sha256;
DROP INDEX IF EXISTS ix_avatar_asset_canonical_path;
DROP INDEX IF EXISTS ix_avatar_asset_category_id;

-- 3) Eliminar tabla asset_category
DROP TABLE IF EXISTS asset_category;

-- 4) Eliminar tipo ENUM gender_type (si no está en uso)
DO $$ BEGIN
    IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type') THEN
        -- Sólo borramos si no hay columnas que la usen
        PERFORM 1 FROM pg_attribute a
            JOIN pg_class c ON a.attrelid = c.oid
            WHERE a.atttypid = (SELECT oid FROM pg_type WHERE typname = 'gender_type')
            LIMIT 1;
        IF NOT FOUND THEN
            DROP TYPE gender_type;
        ELSE
            RAISE NOTICE 'gender_type no puede borrarse: todavía está en uso por alguna columna';
        END IF;
    END IF;
END $$;

COMMIT;
