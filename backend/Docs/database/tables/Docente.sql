-- =====================================================
-- Tabla: Docente
-- =====================================================

CREATE TABLE IF NOT EXISTS Docente (
    docente_id uuid NOT NULL,
    area_conocimiento character varying(50) NOT NULL,
    fecha_vinculacion date NOT NULL,
    tipo_vinculacion USER-DEFINED NOT NULL DEFAULT 'planta'::tipo_vinculacion_institucion,
    titulo_academico character varying(50),
    horas_semanales smallint
,
    PRIMARY KEY (docente_id)
);

-- Foreign Keys de Docente
ALTER TABLE Docente ADD CONSTRAINT Docente_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de Docente
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_1_not_null CHECK (docente_id IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_2_not_null CHECK (area_conocimiento IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_3_not_null CHECK (fecha_vinculacion IS NOT NULL);
ALTER TABLE Docente ADD CONSTRAINT 39558_39761_4_not_null CHECK (tipo_vinculacion IS NOT NULL);
