-- DDL: crea enum gender_type y tabla asset_category
-- Añade columnas seguras (nullable) a avatar_asset para backfill
-- Ejecutar en PostgreSQL. Recomendado: hacer snapshot antes y ejecutar en staging primero.

BEGIN;

-- 1) Tipo ENUM para gender (valores iniciales; se pueden ampliar manualmente si se necesita)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type') THEN
        CREATE TYPE gender_type AS ENUM ('male', 'female', 'unisex', 'other');
    END IF;
END $$;

-- 2) Tabla de categorías de assets (extensible)
CREATE TABLE IF NOT EXISTS asset_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3) Columnas añadidas a avatar_asset (todas NULLABLE para backfill seguro)
ALTER TABLE IF EXISTS avatar_asset
    ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES asset_category(id),
    ADD COLUMN IF NOT EXISTS gender gender_type,
    ADD COLUMN IF NOT EXISTS canonical_path VARCHAR(1024),
    ADD COLUMN IF NOT EXISTS sha256 TEXT,
    ADD COLUMN IF NOT EXISTS is_normalized BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS normalized_at TIMESTAMPTZ;

-- 4) Índices útiles para búsquedas y dedupe (no únicos para evitar romper datos durante backfill)
CREATE INDEX IF NOT EXISTS ix_avatar_asset_sha256 ON avatar_asset (sha256);
CREATE INDEX IF NOT EXISTS ix_avatar_asset_canonical_path ON avatar_asset (canonical_path);
CREATE INDEX IF NOT EXISTS ix_avatar_asset_category_id ON avatar_asset (category_id);

COMMIT;

-- Instrucciones:
-- 1) Hacer snapshot/export (ya generado por scripts anteriores).
-- 2) Ejecutar este archivo en staging y verificar que las columnas se añadieron y que no hay errores.
-- 3) Rellenar `asset_category` y backfill de `avatar_asset` usando mapping CSV y scripts (batch small).
-- 4) Cuando el backfill y verificaciones estén OK, considerar agregar constraints/unique index en `canonical_path`.
