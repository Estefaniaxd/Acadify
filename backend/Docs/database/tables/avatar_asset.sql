-- =====================================================
-- Tabla: avatar_asset
-- =====================================================

CREATE TABLE IF NOT EXISTS avatar_asset (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    category character varying(50) NOT NULL,
    filename character varying(255) NOT NULL,
    display_name character varying(100),
    file_size integer NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    meta_info json,
    is_active character varying(1) NOT NULL DEFAULT 'Y'::character varying,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    target_gender character varying(20) NOT NULL DEFAULT 'unisex'::character varying
,
    PRIMARY KEY (id)
);

-- Unique Constraints de avatar_asset
ALTER TABLE avatar_asset ADD CONSTRAINT avatar_asset_filename_key UNIQUE (filename);

-- Check Constraints de avatar_asset
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_10_not_null CHECK (created_at IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_11_not_null CHECK (updated_at IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_12_not_null CHECK (target_gender IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_2_not_null CHECK (category IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_3_not_null CHECK (filename IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_5_not_null CHECK (file_size IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_6_not_null CHECK (width IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_7_not_null CHECK (height IS NOT NULL);
ALTER TABLE avatar_asset ADD CONSTRAINT 39558_40442_9_not_null CHECK (is_active IS NOT NULL);

-- Índices de avatar_asset
CREATE UNIQUE INDEX avatar_asset_filename_key ON public.avatar_asset USING btree (filename);
CREATE INDEX ix_avatar_asset_id ON public.avatar_asset USING btree (id);
CREATE INDEX ix_avatar_asset_category ON public.avatar_asset USING btree (category);
CREATE INDEX ix_avatar_asset_target_gender ON public.avatar_asset USING btree (target_gender);
