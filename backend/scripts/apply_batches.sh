#!/usr/bin/env fish
# Aplica archivos batch_*.sql en orden usando psql.
# Uso:
#   sudo -u postgres ./backend/scripts/apply_batches.sh backend/scripts/avatar_normalize_output/batches

if test (count $argv) -ne 1
    echo "Uso: sudo -u postgres ./backend/scripts/apply_batches.sh <batches_dir>"
    exit 1
end

set -l batches_dir $argv[1]
if not test -d $batches_dir
    echo "Directorio no encontrado: $batches_dir"
    exit 1
end

for f in (ls $batches_dir/batch_*.sql | sort)
    echo "Ejecutando: $f"
    psql -v ON_ERROR_STOP=1 -f $f
    if test $status -ne 0
        echo "Error al ejecutar $f. Abortando."
        exit 2
    end
end

echo "Todos los batches aplicados correctamente."
