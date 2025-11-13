-- =====================================================
-- Tabla: UsuarioRecompensa
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioRecompensa (
    usuario_recompensa_id uuid NOT NULL,
    usuario_id uuid,
    recompensa_id uuid,
    fecha_canje timestamp with time zone DEFAULT now()
,
    PRIMARY KEY (usuario_recompensa_id)
);

-- Foreign Keys de UsuarioRecompensa
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT UsuarioRecompensa_recompensa_id_fkey FOREIGN KEY (recompensa_id) REFERENCES Recompensa(recompensa_id);
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT UsuarioRecompensa_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioRecompensa
ALTER TABLE UsuarioRecompensa ADD CONSTRAINT 39558_39866_1_not_null CHECK (usuario_recompensa_id IS NOT NULL);
