-- =====================================================
-- Tabla: entregas_tareas
-- =====================================================

CREATE TABLE IF NOT EXISTS entregas_tareas (
    entrega_id character varying NOT NULL,
    tarea_id character varying NOT NULL,
    estudiante_id uuid NOT NULL,
    titulo_entrega character varying(200),
    descripcion_entrega text,
    comentarios_estudiante text,
    archivo_url character varying(500),
    archivos_adicionales json,
    contenido_texto text,
    enlaces_externos json,
    fecha_entrega timestamp with time zone,
    fecha_limite_original timestamp with time zone,
    numero_intento integer,
    es_entrega_tardia boolean,
    calificacion double precision,
    calificacion_letras character varying(5),
    comentarios_docente text,
    rubrica_calificacion json,
    estado character varying(50),
    es_final boolean,
    requiere_revision boolean,
    tiempo_empleado integer,
    dificultad_percibida integer,
    satisfaccion_estudiante integer,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    calificado_por uuid,
    fecha_calificacion timestamp with time zone
,
    PRIMARY KEY (entrega_id)
);

-- Foreign Keys de entregas_tareas
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_calificado_por_fkey FOREIGN KEY (calificado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_estudiante_id_fkey FOREIGN KEY (estudiante_id) REFERENCES Usuario(usuario_id);
ALTER TABLE entregas_tareas ADD CONSTRAINT entregas_tareas_tarea_id_fkey FOREIGN KEY (tarea_id) REFERENCES tareas(tarea_id);

-- Check Constraints de entregas_tareas
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_1_not_null CHECK (entrega_id IS NOT NULL);
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_2_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE entregas_tareas ADD CONSTRAINT 39558_40582_3_not_null CHECK (estudiante_id IS NOT NULL);

-- Índices de entregas_tareas
CREATE INDEX idx_entregas_tarea_id ON public.entregas_tareas USING btree (tarea_id);
CREATE INDEX idx_entregas_estudiante_id ON public.entregas_tareas USING btree (estudiante_id);
CREATE INDEX idx_entregas_estado ON public.entregas_tareas USING btree (estado);
