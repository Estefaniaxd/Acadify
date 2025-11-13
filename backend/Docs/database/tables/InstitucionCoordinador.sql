-- =====================================================
-- Tabla: InstitucionCoordinador
-- =====================================================

CREATE TABLE IF NOT EXISTS InstitucionCoordinador (
    institucion_id uuid NOT NULL,
    coordinador_id uuid NOT NULL,
    fecha_asignacion date NOT NULL,
    estado USER-DEFINED NOT NULL DEFAULT 'activo'::estado_coordinador
,
    PRIMARY KEY (institucion_id, coordinador_id)
);

-- Foreign Keys de InstitucionCoordinador
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT InstitucionCoordinador_coordinador_id_fkey FOREIGN KEY (coordinador_id) REFERENCES Coordinador(coordinador_id);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT InstitucionCoordinador_institucion_id_fkey FOREIGN KEY (institucion_id) REFERENCES Institucion(institucion_id);

-- Check Constraints de InstitucionCoordinador
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_1_not_null CHECK (institucion_id IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_2_not_null CHECK (coordinador_id IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_3_not_null CHECK (fecha_asignacion IS NOT NULL);
ALTER TABLE InstitucionCoordinador ADD CONSTRAINT 39558_39967_4_not_null CHECK (estado IS NOT NULL);
