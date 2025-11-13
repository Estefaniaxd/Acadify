-- =====================================================
-- Tabla: ChatBot
-- =====================================================

CREATE TABLE IF NOT EXISTS ChatBot (
    chat_bot_id uuid NOT NULL DEFAULT gen_random_uuid(),
    nombre character varying(100) NOT NULL,
    descripcion text NOT NULL,
    foto_perfil_url text NOT NULL,
    activo boolean,
    fecha_registro date DEFAULT now()
,
    PRIMARY KEY (chat_bot_id)
);

-- Unique Constraints de ChatBot
ALTER TABLE ChatBot ADD CONSTRAINT ChatBot_nombre_key UNIQUE (nombre);

-- Check Constraints de ChatBot
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_1_not_null CHECK (chat_bot_id IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_2_not_null CHECK (nombre IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_3_not_null CHECK (descripcion IS NOT NULL);
ALTER TABLE ChatBot ADD CONSTRAINT 39558_39564_4_not_null CHECK (foto_perfil_url IS NOT NULL);

-- Índices de ChatBot
CREATE UNIQUE INDEX "ChatBot_nombre_key" ON public."ChatBot" USING btree (nombre);
