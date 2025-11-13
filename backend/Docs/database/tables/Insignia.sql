-- =====================================================
-- Tabla: Insignia
-- =====================================================

CREATE TABLE IF NOT EXISTS Insignia (
    insignia_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text,
    imagen_url text,
    tipo USER-DEFINED NOT NULL DEFAULT 'manual'::tipo_insignia,
    es_unica boolean NOT NULL
,
    PRIMARY KEY (insignia_id)
);

-- Unique Constraints de Insignia
ALTER TABLE Insignia ADD CONSTRAINT Insignia_nombre_key UNIQUE (nombre);

-- Check Constraints de Insignia
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_1_not_null CHECK (insignia_id IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Insignia ADD CONSTRAINT 39558_39593_6_not_null CHECK (es_unica IS NOT NULL);

-- Índices de Insignia
CREATE UNIQUE INDEX "Insignia_nombre_key" ON public."Insignia" USING btree (nombre);
