-- Script de creación de índices para mejorar rendimiento
-- Generado automáticamente para Acadify
-- Total de índices: 16

BEGIN;

-- Índice 1/16
CREATE INDEX IF NOT EXISTS idx_Usuario_email ON "Usuario" ("email");

-- Índice 2/16
CREATE INDEX IF NOT EXISTS idx_Usuario_estado ON "Usuario" ("estado");

-- Índice 3/16
CREATE INDEX IF NOT EXISTS idx_Curso_estado ON "Curso" ("estado");

-- Índice 4/16
CREATE INDEX IF NOT EXISTS idx_Curso_codigo ON "Curso" ("codigo");

-- Índice 5/16
CREATE INDEX IF NOT EXISTS idx_Examen_estado ON "Examen" ("estado");

-- Índice 6/16
CREATE INDEX IF NOT EXISTS idx_Tarea_estado ON "Tarea" ("estado");

-- Índice 7/16
CREATE INDEX IF NOT EXISTS idx_Mensaje_fecha_envio ON "Mensaje" ("fecha_envio");

-- Índice 8/16
CREATE INDEX IF NOT EXISTS idx_Estudiante_estado ON "Estudiante" ("estado");

-- Índice 9/16
CREATE INDEX IF NOT EXISTS idx_Docente_estado ON "Docente" ("estado");

-- Índice 10/16
CREATE INDEX IF NOT EXISTS idx_Mensaje_chat_id_fecha_envio ON "Mensaje" ("chat_id", "fecha_envio");

-- Índice 11/16
CREATE INDEX IF NOT EXISTS idx_Examen_curso_id_estado ON "Examen" ("curso_id", "estado");

-- Índice 12/16
CREATE INDEX IF NOT EXISTS idx_Tarea_curso_id_estado ON "Tarea" ("curso_id", "estado");

-- Índice 13/16
CREATE INDEX IF NOT EXISTS idx_Tarea_curso_id_fecha_limite ON "Tarea" ("curso_id", "fecha_limite");

-- Índice 14/16
CREATE INDEX IF NOT EXISTS idx_Clase_curso_id_fecha_inicio ON "Clase" ("curso_id", "fecha_inicio");

-- Índice 15/16
CREATE INDEX IF NOT EXISTS idx_Material_Educativo_curso_id_tipo ON "Material_Educativo" ("curso_id", "tipo");

-- Índice 16/16
CREATE INDEX IF NOT EXISTS idx_Chat_tipo_estado ON "Chat" ("tipo", "estado");

COMMIT;

-- Verificar índices creados:
-- SELECT schemaname, tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename;
