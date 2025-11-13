-- =====================================================
-- Tabla: tareas
-- =====================================================

CREATE TABLE IF NOT EXISTS tareas (
    tarea_id character varying NOT NULL,
    docente_id uuid NOT NULL,
    titulo character varying(200) NOT NULL,
    descripcion text,
    instrucciones text,
    objetivos text,
    tipo_tarea USER-DEFINED NOT NULL DEFAULT 'ensayo'::tipo_tarea,
    prioridad USER-DEFINED NOT NULL DEFAULT 'media'::prioridad_tarea,
    grupo_id uuid NOT NULL,
    tags character varying(500),
    fecha_asignacion timestamp with time zone DEFAULT now(),
    fecha_limite timestamp with time zone NOT NULL,
    fecha_inicio_disponible timestamp with time zone,
    tiempo_estimado integer,
    permite_entrega_tardia boolean,
    penalizacion_tardia double precision,
    intentos_maximos integer,
    formato_entrega character varying(200),
    tamano_maximo_mb double precision,
    puntuacion_maxima double precision NOT NULL,
    peso_evaluacion double precision,
    rubrica_id character varying,
    estado USER-DEFINED NOT NULL DEFAULT 'asignada'::estado_tarea,
    es_grupal boolean,
    es_publica boolean,
    requiere_aprobacion boolean,
    configuracion_json json,
    recursos_necesarios text,
    criterios_evaluacion text,
    activa boolean,
    fecha_creacion timestamp with time zone DEFAULT now(),
    fecha_actualizacion timestamp with time zone,
    creado_por uuid,
    actualizado_por uuid
,
    PRIMARY KEY (tarea_id)
);

-- Foreign Keys de tareas
ALTER TABLE tareas ADD CONSTRAINT tareas_creado_por_fkey FOREIGN KEY (creado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_actualizado_por_fkey FOREIGN KEY (actualizado_por) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_docente_id_fkey FOREIGN KEY (docente_id) REFERENCES Usuario(usuario_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_grupo_id_fkey FOREIGN KEY (grupo_id) REFERENCES Grupo(grupo_id);
ALTER TABLE tareas ADD CONSTRAINT tareas_rubrica_id_fkey FOREIGN KEY (rubrica_id) REFERENCES rubricas(rubrica_id);

-- Check Constraints de tareas
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_12_not_null CHECK (fecha_limite IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_1_not_null CHECK (tarea_id IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_20_not_null CHECK (puntuacion_maxima IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_23_not_null CHECK (estado IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_2_not_null CHECK (docente_id IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_3_not_null CHECK (titulo IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_7_not_null CHECK (tipo_tarea IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_8_not_null CHECK (prioridad IS NOT NULL);
ALTER TABLE tareas ADD CONSTRAINT 39558_40545_9_not_null CHECK (grupo_id IS NOT NULL);

-- Índices de tareas
CREATE INDEX idx_tareas_grupo_id ON public.tareas USING btree (grupo_id);
CREATE INDEX idx_tareas_docente_id ON public.tareas USING btree (docente_id);
CREATE INDEX idx_tareas_fecha_limite ON public.tareas USING btree (fecha_limite);
CREATE INDEX idx_tareas_estado ON public.tareas USING btree (estado);
