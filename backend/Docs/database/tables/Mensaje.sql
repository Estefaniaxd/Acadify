-- =====================================================
-- Tabla: Mensaje
-- =====================================================

CREATE TABLE IF NOT EXISTS Mensaje (
    mensaje_id uuid NOT NULL,
    chat_grupo_id uuid NOT NULL,
    emisor_id uuid,
    fecha_hora timestamp with time zone NOT NULL DEFAULT now(),
    tipo USER-DEFINED NOT NULL,
    contenido text NOT NULL
,
    PRIMARY KEY (mensaje_id)
);

-- Foreign Keys de Mensaje
ALTER TABLE Mensaje ADD CONSTRAINT Mensaje_chat_grupo_id_fkey FOREIGN KEY (chat_grupo_id) REFERENCES ChatGrupo(chat_grupo_id);
ALTER TABLE Mensaje ADD CONSTRAINT Mensaje_emisor_id_fkey FOREIGN KEY (emisor_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de Mensaje
ALTER TABLE Mensaje ADD CONSTRAINT 39558_40299_1_not_null CHECK (mensaje_id IS NOT NULL);
ALTER TABLE Mensaje ADD CONSTRAINT 39558_40299_2_not_null CHECK (chat_grupo_id IS NOT NULL);
ALTER TABLE Mensaje ADD CONSTRAINT 39558_40299_4_not_null CHECK (fecha_hora IS NOT NULL);
ALTER TABLE Mensaje ADD CONSTRAINT 39558_40299_5_not_null CHECK (tipo IS NOT NULL);
ALTER TABLE Mensaje ADD CONSTRAINT 39558_40299_6_not_null CHECK (contenido IS NOT NULL);
