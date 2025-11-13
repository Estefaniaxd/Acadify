-- =====================================================
-- Tabla: Institucion
-- =====================================================

CREATE TABLE IF NOT EXISTS Institucion (
    institucion_id uuid NOT NULL DEFAULT gen_random_uuid(),
    administrador_id_creador uuid,
    nombre character varying(150) NOT NULL,
    sigla character varying(20),
    lema character varying(255),
    tipo_institucion USER-DEFINED NOT NULL,
    usa_programas boolean NOT NULL,
    nivel_educativo USER-DEFINED NOT NULL,
    sector USER-DEFINED NOT NULL,
    direccion character varying(255),
    ciudad character varying(100),
    pais character varying(100) NOT NULL,
    correo_institucional character varying(100) NOT NULL,
    telefono character varying(30) NOT NULL,
    nit character varying(20),
    estado USER-DEFINED NOT NULL DEFAULT 'pendiente'::estado_institucion,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_activacion timestamp with time zone,
    dominio character varying(255)
,
    PRIMARY KEY (institucion_id)
);

-- Foreign Keys de Institucion
ALTER TABLE Institucion ADD CONSTRAINT Institucion_administrador_id_creador_fkey FOREIGN KEY (administrador_id_creador) REFERENCES Usuario(usuario_id);

-- Unique Constraints de Institucion
ALTER TABLE Institucion ADD CONSTRAINT Institucion_correo_institucional_key UNIQUE (correo_institucional);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_nit_key UNIQUE (nit);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_nombre_key UNIQUE (nombre);
ALTER TABLE Institucion ADD CONSTRAINT Institucion_sigla_key UNIQUE (sigla);

-- Check Constraints de Institucion
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_12_not_null CHECK (pais IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_13_not_null CHECK (correo_institucional IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_14_not_null CHECK (telefono IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_16_not_null CHECK (estado IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_1_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_3_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_6_not_null CHECK (tipo_institucion IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_7_not_null CHECK (usa_programas IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_8_not_null CHECK (nivel_educativo IS NOT NULL);
ALTER TABLE Institucion ADD CONSTRAINT 39558_39919_9_not_null CHECK (sector IS NOT NULL);

-- Índices de Institucion
CREATE INDEX idx_institucion_dominio ON public."Institucion" USING btree (dominio);
CREATE UNIQUE INDEX "Institucion_correo_institucional_key" ON public."Institucion" USING btree (correo_institucional);
CREATE UNIQUE INDEX "Institucion_nit_key" ON public."Institucion" USING btree (nit);
CREATE UNIQUE INDEX "Institucion_nombre_key" ON public."Institucion" USING btree (nombre);
CREATE UNIQUE INDEX "Institucion_sigla_key" ON public."Institucion" USING btree (sigla);
