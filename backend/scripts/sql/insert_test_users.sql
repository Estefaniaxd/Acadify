-- Insertar usuarios de prueba para load testing

-- Admin (sin correo, con username)
INSERT INTO "Usuario" (usuario_id, username, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, email_verified)
VALUES (gen_random_uuid(), 'adminacadify', 'Admin', 'Acadify', 'cc', '1000000001', 'administrador', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyKgwLwO7tia', 'activo', true)
ON CONFLICT (username) DO NOTHING;

-- Docente (con correo, sin username)
INSERT INTO "Usuario" (usuario_id, correo_institucional, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, email_verified)
VALUES (gen_random_uuid(), 'docente@acadify.com', 'Docente', 'Test', 'cc', '1000000002', 'docente', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyKgwLwO7tia', 'activo', true)
ON CONFLICT (correo_institucional) DO NOTHING;

-- Estudiante (con correo, sin username)
INSERT INTO "Usuario" (usuario_id, correo_institucional, nombres, apellidos, tipo_documento, numero_documento, rol, password_hash, estado_cuenta, email_verified)
VALUES (gen_random_uuid(), 'estudiante@acadify.com', 'Estudiante', 'Test', 'cc', '1000000003', 'estudiante', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyKgwLwO7tia', 'activo', true)
ON CONFLICT (correo_institucional) DO NOTHING;

SELECT 'Usuarios de prueba insertados correctamente' as status;
