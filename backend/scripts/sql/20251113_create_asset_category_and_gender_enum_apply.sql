BEGIN;

DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type') THEN
        CREATE TYPE gender_type AS ENUM ('male','female','unisex','other');
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS asset_category (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE IF EXISTS avatar_asset
    ADD COLUMN IF NOT EXISTS category_id INTEGER REFERENCES asset_category(id),
    ADD COLUMN IF NOT EXISTS gender gender_type,
    ADD COLUMN IF NOT EXISTS canonical_path VARCHAR(1024),
    ADD COLUMN IF NOT EXISTS sha256 TEXT,
    ADD COLUMN IF NOT EXISTS is_normalized BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS normalized_at TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS ix_avatar_asset_sha256 ON avatar_asset (sha256);
CREATE INDEX IF NOT EXISTS ix_avatar_asset_canonical_path ON avatar_asset (canonical_path);
CREATE INDEX IF NOT EXISTS ix_avatar_asset_category_id ON avatar_asset (category_id);

COMMIT;
