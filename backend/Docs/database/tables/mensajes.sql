-- =====================================================
-- Tabla: mensajes
-- =====================================================

CREATE TABLE IF NOT EXISTS mensajes (
    id uuid NOT NULL,
    sala_id uuid NOT NULL,
    usuario_id uuid NOT NULL,
    contenido text,
    contenido_html text,
    tipo_mensaje character varying(50),
    archivos_urls json,
    metadatos_archivos json,
    mensaje_padre_id uuid,
    tiene_respuestas boolean,
    numero_respuestas integer,
    menciones_usuarios json,
    menciones_ia boolean,
    menciones_todos boolean,
    estado character varying(50),
    fecha_creacion timestamp without time zone DEFAULT now(),
    fecha_actualizacion timestamp without time zone,
    fecha_eliminacion timestamp without time zone,
    reacciones json,
    es_importante boolean,
    es_anuncio boolean
,
    PRIMARY KEY (id)
);

-- Foreign Keys de mensajes
ALTER TABLE mensajes ADD CONSTRAINT mensajes_sala_id_fkey FOREIGN KEY (sala_id) REFERENCES salas_chat(id);
ALTER TABLE mensajes ADD CONSTRAINT mensajes_mensaje_padre_id_fkey FOREIGN KEY (mensaje_padre_id) REFERENCES mensajes(id);

-- Check Constraints de mensajes
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_1_not_null CHECK (id IS NOT NULL);
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_2_not_null CHECK (sala_id IS NOT NULL);
ALTER TABLE mensajes ADD CONSTRAINT 39558_40661_3_not_null CHECK (usuario_id IS NOT NULL);
