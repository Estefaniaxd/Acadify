-- =====================================================
-- Tabla: EntregarTarea
-- =====================================================

CREATE TABLE IF NOT EXISTS EntregarTarea (
    entrega_id uuid NOT NULL DEFAULT gen_random_uuid(),
    tarea_id uuid NOT NULL,
    estudiante_id uuid NOT NULL,
    archivo text NOT NULL,
    fecha_envio timestamp with time zone NOT NULL DEFAULT now(),
    calificacion numeric,
    fecha_revision timestamp with time zone
,
    PRIMARY KEY (entrega_id)
);

-- Foreign Keys de EntregarTarea
ALTER TABLE EntregarTarea ADD CONSTRAINT EntregarTarea_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Estudiante(estudiante_id);
ALTER TABLE EntregarTarea ADD CONSTRAINT EntregarTarea_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES Tarea(tarea_id);

-- Unique Constraints de EntregarTarea
ALTER TABLE EntregarTarea ADD CONSTRAINT uq_entrega UNIQUE (tarea_id, estudiante_id);

-- Check Constraints de EntregarTarea
ALTER TABLE EntregarTarea ADD CONSTRAINT 39558_40375_1_not_null CHECK (entrega_id IS NOT NULL);
ALTER TABLE EntregarTarea ADD CONSTRAINT 39558_40375_2_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE EntregarTarea ADD CONSTRAINT 39558_40375_3_not_null CHECK (estudiante_id IS NOT NULL);
ALTER TABLE EntregarTarea ADD CONSTRAINT 39558_40375_4_not_null CHECK (archivo IS NOT NULL);
ALTER TABLE EntregarTarea ADD CONSTRAINT 39558_40375_5_not_null CHECK (fecha_envio IS NOT NULL);
ALTER TABLE EntregarTarea ADD CONSTRAINT chk_calificacion CHECK (((calificacion >= (0)::numeric) AND (calificacion <= (5)::numeric)));

-- Índices de EntregarTarea
CREATE INDEX idx_entregas_tarea_estudiante ON public."EntregarTarea" USING btree (tarea_id, estudiante_id);
CREATE UNIQUE INDEX uq_entrega ON public."EntregarTarea" USING btree (tarea_id, estudiante_id);
