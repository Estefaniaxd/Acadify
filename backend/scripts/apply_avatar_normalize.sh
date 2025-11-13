#!/usr/bin/env fish
# Script seguro para aplicar los SQL generados por avatar_normalize
# Uso:
#   1) Haz un backup: sudo -u postgres pg_dump -Fc -f /tmp/backup.dump acadify_db
#   2) Revisa los SQL en backend/scripts/avatar_normalize_output/
#   3) Ejecuta este script: sudo -u postgres ./backend/scripts/apply_avatar_normalize.sh

set -l out_dir backend/scripts/avatar_normalize_output
set -l avatar_asset_sql $out_dir/avatar_normalize_apply_avatar_asset.sql
set -l user_avatar_sql $out_dir/avatar_normalize_apply_user_avatar.sql

if not test -f $avatar_asset_sql -o -f $user_avatar_sql
    echo "No se encontraron los SQL esperados en $out_dir"
    exit 1
end

echo "IMPORTANTE: Asegúrate de tener un backup reciente. Este script ejecutará los SQL en orden."
read -P "¿Continuar? (y/n): " ans
if test "$ans" != "y"
    echo "Abortando"
    exit 0
end

echo "Ejecutando avatar_asset updates..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -f $avatar_asset_sql
if test $status -ne 0
    echo "Error al ejecutar avatar_asset SQL. Revisar logs."
    exit 2
end

echo "Ejecutando user_avatar updates..."
sudo -u postgres psql -v ON_ERROR_STOP=1 -f $user_avatar_sql
if test $status -ne 0
    echo "Error al ejecutar user_avatar SQL. Revisar logs."
    exit 3
end

echo "Aplicación completada. Verifica el sistema y los previews. Si hay problemas, restaura el backup."
