-- =====================================================
-- Tabla: ArchivoChat
-- =====================================================

CREATE TABLE IF NOT EXISTS ArchivoChat (
    archivo_id uuid NOT NULL DEFAULT gen_random_uuid(),
    chat_grupo_id uuid NOT NULL,
    usuario_id uuid,
    nombre_archivo text NOT NULL,
    url_archivo text NOT NULL,
    fecha_envio timestamp with time zone NOT NULL DEFAULT now(),
    tipo_archivo text
,
    PRIMARY KEY (archivo_id)
);

-- Foreign Keys de ArchivoChat
ALTER TABLE ArchivoChat ADD CONSTRAINT ArchivoChat_chat_grupo_id_fkey FOREIGN KEY (chat_grupo_id) REFERENCES ChatGrupo(chat_grupo_id);
ALTER TABLE ArchivoChat ADD CONSTRAINT ArchivoChat_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de ArchivoChat
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_1_not_null CHECK (archivo_id IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_2_not_null CHECK (chat_grupo_id IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_4_not_null CHECK (nombre_archivo IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_5_not_null CHECK (url_archivo IS NOT NULL);
ALTER TABLE ArchivoChat ADD CONSTRAINT 39558_40252_6_not_null CHECK (fecha_envio IS NOT NULL);
