-- =====================================================
-- Tabla: Clase
-- =====================================================

CREATE TABLE IF NOT EXISTS Clase (
    clase_id uuid NOT NULL DEFAULT gen_random_uuid(),
    grupo_curso_id uuid NOT NULL,
    plataforma_id uuid,
    titulo text NOT NULL,
    descripcion text,
    hora_inicio timestamp with time zone NOT NULL DEFAULT now(),
    duracion interval NOT NULL,
    link_videollamada text NOT NULL
,
    PRIMARY KEY (clase_id)
);

-- Foreign Keys de Clase
ALTER TABLE Clase ADD CONSTRAINT Clase_grupo_curso_id_fkey FOREIGN KEY (grupo_curso_id) REFERENCES GrupoCurso(grupo_curso_id);
ALTER TABLE Clase ADD CONSTRAINT Clase_plataforma_id_fkey FOREIGN KEY (plataforma_id) REFERENCES Plataforma(plataforma_id);

-- Check Constraints de Clase
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_1_not_null CHECK (clase_id IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_2_not_null CHECK (grupo_curso_id IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_4_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_6_not_null CHECK (hora_inicio IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_7_not_null CHECK (duracion IS NOT NULL);
ALTER TABLE Clase ADD CONSTRAINT 39558_40271_8_not_null CHECK (link_videollamada IS NOT NULL);
