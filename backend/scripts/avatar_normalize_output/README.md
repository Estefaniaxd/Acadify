Avatar normalization - outputs and how to apply

Contenido generado por los scripts de normalización de avatar (hair):

- `avatar_normalize_mapping.csv` - mapping fuente -> candidato relativo (para SQL generator).
- `avatar_normalize_apply_avatar_asset.sql` - SQL con UPDATEs para `avatar_asset` (dry-run style, transaccional).
- `avatar_normalize_apply_user_avatar.sql` - SQL con UPDATEs para `user_avatar` (JSON replace in `layers`).
- `batches/` - lotes SQL listos para aplicar (avatar_asset updates).
- `batches_user_avatar/` - lotes SQL listos para aplicar (user_avatar updates).

INSTRUCCIONES (NO EJECUTAR EN PRODUCCIÓN SIN BACKUP):

1) Crear backup de la BD (ejecutar en el host con acceso a la DB):

```fish
# Reemplaza los valores con tu conexión
set -l DBURL "postgresql://user:pass@host:5432/dbname"
pg_dump -Fc -f backup_before_avatar_normalize_"(date +%Y%m%d_%H%M)".dump $DBURL
```

2) Revisar manualmente los SQL generados en:

```fish
ls -la backend/scripts/avatar_normalize_output/*.sql
ls -la backend/scripts/avatar_normalize_output/batches
ls -la backend/scripts/avatar_normalize_output/batches_user_avatar
```

3) Aplicar batches (recomendado: staging primero). Hay un helper `apply_batches.sh` (fish) que ejecuta psql con ON_ERROR_STOP:

```fish
# Ejecutar como el usuario que tenga permisos para aplicar cambios (p. ej. postgres)
# Aplica los batches de avatar_asset
sudo -u postgres ./backend/scripts/apply_batches.sh backend/scripts/avatar_normalize_output/batches
# Aplica los batches que actualizan user_avatar JSON
sudo -u postgres ./backend/scripts/apply_batches.sh backend/scripts/avatar_normalize_output/batches_user_avatar
```

4) Verificación rápida después de cada batch:

```fish
# Comprobar que el filename canónico existe
psql $DBURL -c "SELECT count(*) FROM avatar_asset WHERE filename LIKE 'hair/female/%';"
# Comprobar user_avatar afectados
psql $DBURL -c "SELECT count(*) FROM user_avatar WHERE EXISTS (SELECT 1 FROM jsonb_array_elements(layers::jsonb) elem WHERE elem->>'file' = 'hair_4.png');"
```

5) Limpieza de disco (opcional, realizar solo tras confirmar que la BD fue actualizada y validada):

- Mover duplicados a `backend/static/assets/_archive/` o reemplazarlos por symlinks apuntando al canonical.
- Validar previews UI en staging.

6) Rollback (si necesario): restaurar el dump creado en el paso 1.

---

Si quieres, puedo:
- Generar un script de rollback SQL (no siempre trivial para JSON updates). O
- Crear PR con estos artefactos y una descripción para QA.
