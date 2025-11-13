-- Eliminar el constraint viejo que prohibía tener ambos campos
ALTER TABLE "Usuario" DROP CONSTRAINT IF EXISTS chk_login;

-- Crear nuevo constraint que requiere ambos campos
-- Todos los usuarios deben tener username Y correo_institucional
ALTER TABLE "Usuario" ADD CONSTRAINT chk_login 
CHECK (
  (username IS NOT NULL) AND 
  (correo_institucional IS NOT NULL)
);

SELECT 'Constraint actualizado correctamente - Ahora todos los usuarios deben tener username Y correo' as status;
