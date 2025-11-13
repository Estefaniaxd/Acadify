-- =====================================================
-- Tabla: notificaciones
-- =====================================================

CREATE TABLE IF NOT EXISTS notificaciones (
    id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    titulo character varying(255) NOT NULL,
    mensaje text,
    tipo_notificacion character varying(50),
    sala_id uuid,
    mensaje_id uuid,
    tarea_id uuid,
    curso_id uuid,
    leida boolean,
    enviada_email boolean,
    enviada_push boolean,
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_lectura timestamp without time zone,
    fecha_envio_email timestamp without time zone,
    datos_adicionales json,
    url_accion character varying(500),
    icono character varying(100),
    color character varying(7)
,
    PRIMARY KEY (id)
);

-- Foreign Keys de notificaciones
ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_sala_id_fkey FOREIGN KEY (sala_id) REFERENCES salas_chat(id);
ALTER TABLE notificaciones ADD CONSTRAINT notificaciones_mensaje_id_fkey FOREIGN KEY (mensaje_id) REFERENCES mensajes(id);

-- Check Constraints de notificaciones
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_2_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE notificaciones ADD CONSTRAINT 39558_40679_3_not_null CHECK (titulo IS NOT NULL);

-- Índices de notificaciones
CREATE INDEX idx_notificaciones_usuario_id ON public.notificaciones USING btree (usuario_id);
CREATE INDEX idx_notificaciones_leida ON public.notificaciones USING btree (leida);
CREATE INDEX idx_notificaciones_usuario_leida_fecha ON public.notificaciones USING btree (usuario_id, leida, fecha_creacion DESC);
CREATE INDEX idx_notificaciones_tipo ON public.notificaciones USING btree (tipo_notificacion) WHERE (tipo_notificacion IS NOT NULL);
