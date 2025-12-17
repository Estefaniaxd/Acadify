-- =====================================================
-- TABLA DE AUDITORÍA PARA ACADIFY
-- Base de datos: PostgreSQL
-- =====================================================

-- Crear tabla de auditoría si no existe
CREATE TABLE IF NOT EXISTS "AuditoriaAcciones" (
    auditoria_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES "Usuario"(usuario_id) ON DELETE SET NULL,
    accion VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100) NOT NULL,
    registro_id UUID,
    detalles TEXT,
    ip_address VARCHAR(45),
    fecha_hora TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    
    -- Índices para consultas rápidas
    CONSTRAINT chk_accion CHECK (accion IN (
        'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 
        'CAMBIO_PASSWORD', 'CAMBIO_ROL', 'ACTIVAR_2FA', 
        'DESACTIVAR_2FA', 'EXPORTAR_DATOS', 'IMPORTAR_DATOS',
        'CALIFICAR_TAREA', 'ELIMINAR_USUARIO', 'CREAR_INSTITUCION'
    ))
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON "AuditoriaAcciones"(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON "AuditoriaAcciones"(fecha_hora DESC);
CREATE INDEX IF NOT EXISTS idx_auditoria_accion ON "AuditoriaAcciones"(accion);
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON "AuditoriaAcciones"(tabla_afectada);

-- Comentario de la tabla
COMMENT ON TABLE "AuditoriaAcciones" IS 'Tabla para registrar acciones críticas del sistema con fines de auditoría';
COMMENT ON COLUMN "AuditoriaAcciones".accion IS 'Tipo de acción realizada (CREATE, UPDATE, DELETE, LOGIN, etc.)';
COMMENT ON COLUMN "AuditoriaAcciones".tabla_afectada IS 'Nombre de la tabla o módulo afectado';
COMMENT ON COLUMN "AuditoriaAcciones".registro_id IS 'ID del registro afectado si aplica';
COMMENT ON COLUMN "AuditoriaAcciones".ip_address IS 'Dirección IP desde donde se realizó la acción';
