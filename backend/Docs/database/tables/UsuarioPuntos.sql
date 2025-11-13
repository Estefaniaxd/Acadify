-- =====================================================
-- Tabla: UsuarioPuntos
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioPuntos (
    usuario_id uuid NOT NULL,
    puntos_acumulados integer NOT NULL DEFAULT 0,
    cambio integer NOT NULL,
    motivo text,
    fecha timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (usuario_id)
);

-- Foreign Keys de UsuarioPuntos
ALTER TABLE UsuarioPuntos ADD CONSTRAINT UsuarioPuntos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioPuntos
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_2_not_null CHECK (puntos_acumulados IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_3_not_null CHECK (cambio IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT 39558_39851_5_not_null CHECK (fecha IS NOT NULL);
ALTER TABLE UsuarioPuntos ADD CONSTRAINT UsuarioPuntos_cambio_check CHECK ((cambio <> 0));

-- Índices de UsuarioPuntos
CREATE INDEX idx_usuario_puntos_usuario_id ON public."UsuarioPuntos" USING btree (usuario_id);
