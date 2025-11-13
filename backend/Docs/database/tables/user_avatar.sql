-- =====================================================
-- Tabla: user_avatar
-- =====================================================

CREATE TABLE IF NOT EXISTS user_avatar (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL,
    name character varying(100) NOT NULL,
    layers json NOT NULL,
    image_url character varying(500) NOT NULL,
    layers_hash character varying(64) NOT NULL,
    is_active boolean NOT NULL DEFAULT false,
    is_public boolean NOT NULL DEFAULT true,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now(),
    base_gender character varying(20) NOT NULL DEFAULT 'male'::character varying
,
    PRIMARY KEY (id)
);

-- Foreign Keys de user_avatar
ALTER TABLE user_avatar ADD CONSTRAINT user_avatar_user_id_fkey FOREIGN KEY (user_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de user_avatar
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_10_not_null CHECK (updated_at IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_11_not_null CHECK (base_gender IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_2_not_null CHECK (user_id IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_3_not_null CHECK (name IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_4_not_null CHECK (layers IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_5_not_null CHECK (image_url IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_6_not_null CHECK (layers_hash IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_7_not_null CHECK (is_active IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_8_not_null CHECK (is_public IS NOT NULL);
ALTER TABLE user_avatar ADD CONSTRAINT 39558_40457_9_not_null CHECK (created_at IS NOT NULL);

-- Índices de user_avatar
CREATE INDEX ix_user_avatar_id ON public.user_avatar USING btree (id);
CREATE INDEX ix_user_avatar_user_id ON public.user_avatar USING btree (user_id);
CREATE INDEX ix_user_avatar_layers_hash ON public.user_avatar USING btree (layers_hash);
