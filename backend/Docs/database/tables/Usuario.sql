-- =====================================================
-- Tabla: Usuario
-- =====================================================

CREATE TABLE IF NOT EXISTS Usuario (
    usuario_id uuid NOT NULL DEFAULT gen_random_uuid(),
    correo_institucional character varying(100),
    username character varying(50),
    nombres character varying(100) NOT NULL,
    apellidos character varying(100) NOT NULL,
    tipo_documento USER-DEFINED NOT NULL,
    numero_documento character varying(20) NOT NULL,
    rol USER-DEFINED NOT NULL,
    password_hash character varying(255) NOT NULL,
    estado_cuenta USER-DEFINED NOT NULL DEFAULT 'activo'::estado_cuenta_usuario,
    fecha_creacion timestamp with time zone DEFAULT now(),
    ultimo_acceso timestamp with time zone DEFAULT now(),
    perfil_url text,
    portada_url text,
    telefono character varying(20),
    descripcion text,
    email_verified boolean NOT NULL DEFAULT false,
    failed_login_attempts smallint NOT NULL DEFAULT 0,
    locked_until timestamp with time zone,
    twofa_enabled boolean NOT NULL DEFAULT false,
    twofa_secret character varying(32)
,
    PRIMARY KEY (usuario_id)
);

-- Check Constraints de Usuario
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_10_not_null CHECK (estado_cuenta IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_17_not_null CHECK (email_verified IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_18_not_null CHECK (failed_login_attempts IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_20_not_null CHECK (twofa_enabled IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_4_not_null CHECK (nombres IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_5_not_null CHECK (apellidos IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_6_not_null CHECK (tipo_documento IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_7_not_null CHECK (numero_documento IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_8_not_null CHECK (rol IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT 39558_39711_9_not_null CHECK (password_hash IS NOT NULL);
ALTER TABLE Usuario ADD CONSTRAINT chk_login CHECK ((((rol = 'administrador'::rol_usuario) AND (username IS NOT NULL) AND (correo_institucional IS NULL)) OR ((rol <> 'administrador'::rol_usuario) AND (correo_institucional IS NOT NULL) AND (username IS NULL))));

-- Índices de Usuario
CREATE INDEX idx_usuario_rol ON public."Usuario" USING btree (rol);
CREATE INDEX idx_usuario_estado_cuenta ON public."Usuario" USING btree (estado_cuenta);
CREATE INDEX idx_usuario_rol_estado ON public."Usuario" USING btree (rol, estado_cuenta);
CREATE INDEX idx_usuario_nombres_busqueda ON public."Usuario" USING gin (to_tsvector('spanish'::regconfig, (((nombres)::text || ' '::text) || (apellidos)::text)));
CREATE UNIQUE INDEX "ix_Usuario_correo_institucional" ON public."Usuario" USING btree (correo_institucional);
CREATE INDEX "ix_Usuario_numero_documento" ON public."Usuario" USING btree (numero_documento);
CREATE UNIQUE INDEX "ix_Usuario_username" ON public."Usuario" USING btree (username);
CREATE INDEX "ix_Usuario_usuario_id" ON public."Usuario" USING btree (usuario_id);
