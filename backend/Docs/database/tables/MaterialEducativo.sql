-- =====================================================
-- Tabla: MaterialEducativo
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialEducativo (
    material_id uuid NOT NULL DEFAULT gen_random_uuid(),
    titulo character varying(100) NOT NULL,
    descripcion text,
    tipo_material USER-DEFINED NOT NULL,
    url_archivo character varying(255) NOT NULL,
    formato_archivo character varying(10) NOT NULL
,
    PRIMARY KEY (material_id)
);

-- Check Constraints de MaterialEducativo
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_1_not_null CHECK (material_id IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_2_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_4_not_null CHECK (tipo_material IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_5_not_null CHECK (url_archivo IS NOT NULL);
ALTER TABLE MaterialEducativo ADD CONSTRAINT 39558_39627_6_not_null CHECK (formato_archivo IS NOT NULL);
