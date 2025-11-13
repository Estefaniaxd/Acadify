-- Actualizar usuarios que solo tienen correo, asignándoles username único
UPDATE "Usuario" 
SET username = SUBSTRING(correo_institucional FROM '^([^@]+)') || '_' || SUBSTRING(usuario_id::text FROM 1 FOR 8)
WHERE username IS NULL AND correo_institucional IS NOT NULL;

-- Actualizar admin que solo tiene username, asignándole un correo
UPDATE "Usuario" 
SET correo_institucional = username || '@acadify.local'
WHERE correo_institucional IS NULL AND username IS NOT NULL;

-- Ahora crear el constraint
ALTER TABLE "Usuario" ADD CONSTRAINT chk_login 
CHECK (
  (username IS NOT NULL) AND 
  (correo_institucional IS NOT NULL)
);

SELECT 'Usuarios actualizados y constraint creado' as status;
SELECT COUNT(*) as total_usuarios, 
       COUNT(username) as con_username, 
       COUNT(correo_institucional) as con_correo 
FROM "Usuario";
