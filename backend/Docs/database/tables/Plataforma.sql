-- =====================================================
-- Tabla: Plataforma
-- =====================================================

CREATE TABLE IF NOT EXISTS Plataforma (
    plataforma_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(50) NOT NULL,
    url_base text NOT NULL,
    tipo_integracion USER-DEFINED NOT NULL,
    requiere_cuenta boolean NOT NULL,
    es_gratuita boolean
,
    PRIMARY KEY (plataforma_id)
);

-- Unique Constraints de Plataforma
ALTER TABLE Plataforma ADD CONSTRAINT Plataforma_nombre_key UNIQUE (nombre);

-- Check Constraints de Plataforma
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_1_not_null CHECK (plataforma_id IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_3_not_null CHECK (url_base IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_4_not_null CHECK (tipo_integracion IS NOT NULL);
ALTER TABLE Plataforma ADD CONSTRAINT 39558_39645_5_not_null CHECK (requiere_cuenta IS NOT NULL);

-- Índices de Plataforma
CREATE UNIQUE INDEX "Plataforma_nombre_key" ON public."Plataforma" USING btree (nombre);
