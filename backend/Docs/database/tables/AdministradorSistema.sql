-- =====================================================
-- Tabla: AdministradorSistema
-- =====================================================

CREATE TABLE IF NOT EXISTS AdministradorSistema (
    administrador_id uuid NOT NULL
,
    PRIMARY KEY (administrador_id)
);

-- Foreign Keys de AdministradorSistema
ALTER TABLE AdministradorSistema ADD CONSTRAINT AdministradorSistema_administrador_id_fkey FOREIGN KEY (administrador_id) REFERENCES Usuario(usuario_id);

-- Check Constraints de AdministradorSistema
ALTER TABLE AdministradorSistema ADD CONSTRAINT 39558_39730_1_not_null CHECK (administrador_id IS NOT NULL);
