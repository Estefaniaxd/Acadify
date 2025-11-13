-- =====================================================
-- Tabla: Tarea
-- =====================================================

CREATE TABLE IF NOT EXISTS Tarea (
    tarea_id uuid NOT NULL DEFAULT gen_random_uuid(),
    docente_id uuid,
    clase_id uuid NOT NULL,
    titulo character varying(50) NOT NULL,
    descripcion text,
    fecha_asignacion timestamp with time zone NOT NULL DEFAULT now(),
    fecha_limite timestamp with time zone,
    archivo_adjunto text,
    permite_entregas_tardias boolean NOT NULL
,
    PRIMARY KEY (tarea_id)
);

-- Foreign Keys de Tarea
ALTER TABLE Tarea ADD CONSTRAINT Tarea_clase_id_fkey FOREIGN KEY (clase_id) REFERENCES Clase(clase_id);
ALTER TABLE Tarea ADD CONSTRAINT Tarea_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Docente(docente_id);

-- Check Constraints de Tarea
ALTER TABLE Tarea ADD CONSTRAINT 39558_40356_1_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE Tarea ADD CONSTRAINT 39558_40356_3_not_null CHECK (clase_id IS NOT NULL);
ALTER TABLE Tarea ADD CONSTRAINT 39558_40356_4_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE Tarea ADD CONSTRAINT 39558_40356_6_not_null CHECK (fecha_asignacion IS NOT NULL);
ALTER TABLE Tarea ADD CONSTRAINT 39558_40356_9_not_null CHECK (permite_entregas_tardias IS NOT NULL);

-- Índices de Tarea
CREATE INDEX idx_tareas_clase_id ON public."Tarea" USING btree (clase_id);
