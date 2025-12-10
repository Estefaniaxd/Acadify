-- Tabla para archivos de curso (materiales, tareas, recursos, etc.)
CREATE TABLE IF NOT EXISTS archivos_curso (
    archivo_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    curso_id UUID NOT NULL REFERENCES "Curso"(curso_id) ON DELETE CASCADE,
    nombre_original TEXT NOT NULL,
    url TEXT NOT NULL,
    tipo TEXT NOT NULL,
    descripcion TEXT,
    tamaño BIGINT,
    subido_por UUID NOT NULL REFERENCES "Usuario"(usuario_id) ON DELETE SET NULL,
    fecha_subida TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_archivos_curso_curso_id ON archivos_curso(curso_id);
CREATE INDEX IF NOT EXISTS idx_archivos_curso_tipo ON archivos_curso(tipo);
CREATE INDEX IF NOT EXISTS idx_archivos_curso_subido_por ON archivos_curso(subido_por);
