-- =====================================================
-- Tabla: OAuthProvider
-- =====================================================

CREATE TABLE IF NOT EXISTS OAuthProvider (
    oauth_provider_id uuid NOT NULL DEFAULT gen_random_uuid(),
    usuario_id uuid NOT NULL,
    provider character varying(50) NOT NULL,
    provider_user_id character varying(255) NOT NULL,
    provider_email character varying(255) NOT NULL,
    fecha_vinculacion timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (oauth_provider_id)
);

-- Foreign Keys de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT OAuthProvider_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Unique Constraints de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT uq_provider_user UNIQUE (provider, provider_user_id);

-- Check Constraints de OAuthProvider
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_1_not_null CHECK (oauth_provider_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_2_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_3_not_null CHECK (provider IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_4_not_null CHECK (provider_user_id IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_5_not_null CHECK (provider_email IS NOT NULL);
ALTER TABLE OAuthProvider ADD CONSTRAINT 39558_39787_6_not_null CHECK (fecha_vinculacion IS NOT NULL);

-- Índices de OAuthProvider
CREATE UNIQUE INDEX uq_provider_user ON public."OAuthProvider" USING btree (provider, provider_user_id);
