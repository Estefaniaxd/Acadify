-- =====================================================
-- Tabla: UsuarioInsignia
-- =====================================================

CREATE TABLE IF NOT EXISTS UsuarioInsignia (
    usuario_id uuid NOT NULL,
    insignia_id uuid NOT NULL,
    otorgada_por uuid,
    fecha_otorgada timestamp with time zone NOT NULL DEFAULT now()
,
    PRIMARY KEY (usuario_id, insignia_id)
);

-- Foreign Keys de UsuarioInsignia
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_insignia_id_fkey FOREIGN KEY (insignia_id) REFERENCES Insignia(insignia_id);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_otorgada_por_fkey FOREIGN KEY (otorgada_por) REFERENCES Usuario(usuario_id);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT UsuarioInsignia_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de UsuarioInsignia
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_1_not_null CHECK (usuario_id IS NOT NULL);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_2_not_null CHECK (insignia_id IS NOT NULL);
ALTER TABLE UsuarioInsignia ADD CONSTRAINT 39558_39830_4_not_null CHECK (fecha_otorgada IS NOT NULL);

-- Índices de UsuarioInsignia
CREATE INDEX idx_insignias_usuario_usuario_id ON public."UsuarioInsignia" USING btree (usuario_id);
