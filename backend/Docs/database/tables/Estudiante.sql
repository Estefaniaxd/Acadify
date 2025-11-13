-- =====================================================
-- Tabla: Estudiante
-- =====================================================

CREATE TABLE IF NOT EXISTS Estudiante (
    estudiante_id uuid NOT NULL,
    programa_id uuid,
    fecha_ingreso date NOT NULL,
    creditos_aprobados smallint,
    etapa_formativa USER-DEFINED NOT NULL DEFAULT 'i'::etapa_formativa_estudiante,
    promedio_acumulado numeric
,
    PRIMARY KEY (estudiante_id)
);

-- Foreign Keys de Estudiante
ALTER TABLE Estudiante ADD CONSTRAINT Estudiante_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Usuario(usuario_id);
ALTER TABLE Estudiante ADD CONSTRAINT Estudiante_programa_id_fkey FOREIGN KEY (programa_id) REFERENCES Programa(programa_id);

-- Check Constraints de Estudiante
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_1_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_3_not_null CHECK (fecha_ingreso IS NOT NULL);
ALTER TABLE Estudiante ADD CONSTRAINT 39558_40105_5_not_null CHECK (etapa_formativa IS NOT NULL);
