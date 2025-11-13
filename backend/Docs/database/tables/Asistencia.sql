-- =====================================================
-- Tabla: Asistencia
-- =====================================================

CREATE TABLE IF NOT EXISTS Asistencia (
    asistencia_id uuid NOT NULL DEFAULT gen_random_uuid(),
    clase_id uuid NOT NULL,
    estudiante_id uuid NOT NULL,
    estado USER-DEFINED NOT NULL
,
    PRIMARY KEY (asistencia_id)
);

-- Foreign Keys de Asistencia
ALTER TABLE Asistencia ADD CONSTRAINT Asistencia_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES Clase(clase_id);
ALTER TABLE Asistencia ADD CONSTRAINT Asistencia_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Estudiante(estudiante_id);

-- Check Constraints de Asistencia
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_1_not_null CHECK (asistencia_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_2_not_null CHECK (clase_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_3_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE Asistencia ADD CONSTRAINT 39558_40325_4_not_null CHECK (estado IS NOT NULL);
