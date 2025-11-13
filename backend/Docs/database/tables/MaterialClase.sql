-- =====================================================
-- Tabla: MaterialClase
-- =====================================================

CREATE TABLE IF NOT EXISTS MaterialClase (
    material_clase_id uuid NOT NULL,
    clase_id uuid
,
    PRIMARY KEY (material_clase_id)
);

-- Foreign Keys de MaterialClase
ALTER TABLE MaterialClase ADD CONSTRAINT MaterialClase_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES Clase(clase_id);
ALTER TABLE MaterialClase ADD CONSTRAINT MaterialClase_material_clase_id_fkey FOREIGN KEY (material_clase_id) REFERENCES MaterialEducativo(material_id);

-- Check Constraints de MaterialClase
ALTER TABLE MaterialClase ADD CONSTRAINT 39558_40341_1_not_null CHECK (material_clase_id IS NOT NULL);

-- Índices de MaterialClase
CREATE INDEX idx_material_clase_clase_id ON public."MaterialClase" USING btree (clase_id);
