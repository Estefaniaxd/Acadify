#!/usr/bin/env fish
# Helper script to run full safe pipeline for avatar normalization:
# 1) dry-run (against DB)
# 2) snapshot CSVs (preapply)
# 3) generate rollback.sql
# 4) optionally apply batches (avatar_asset then user_avatar)

# SECURITY: This script prompts for DB connection string securely. Do NOT paste secrets into chat.

function prompt_dburl
    echo "Enter PostgreSQL connection string in the form: postgresql://USER:PASS@HOST:5432/DBNAME"
    echo -n "DBURL: "
    read -s DBURL
    echo
    # Accept either a raw URI or a "DATABASE_URL=..." style paste and normalize
    if test (string match -r '^DATABASE_URL=' $DBURL) != ""
        set DBURL (string replace -r '^DATABASE_URL=' '' $DBURL)
    end

    set -g DBURL $DBURL
end

if not test -n "$DBURL"
    prompt_dburl
end

# Ensure psql is available
if not type -q psql
    echo "Error: 'psql' not found in PATH. Install the PostgreSQL client (package 'postgresql' or 'postgresql-client') and retry."; exit 1
end

set -l OUT_DIR backend/scripts/avatar_normalize_output
mkdir -p $OUT_DIR

echo "1) Running dry-run against DB (non-destructive)"
python3 backend/scripts/avatar_normalize_dryrun.py --assets-dir backend/static/assets --out $OUT_DIR --psql-cmd "psql '$DBURL'"

echo "\n2) Creating snapshots (this runs psql \copy and writes CSVs to $OUT_DIR)"
python3 backend/scripts/create_snapshots_for_mapping.py --mapping $OUT_DIR/avatar_normalize_mapping.csv --db-url $DBURL --exec

echo "\n3) Generating rollback SQL from snapshots"
python3 backend/scripts/generate_rollback_from_snapshots.py

echo "\n4) Review outputs in: $OUT_DIR"
ls -la $OUT_DIR

echo "\nIf everything looks good, you can apply batches. Apply now? (y/N)"
read APPLY
if test "$APPLY" = "y" -o "$APPLY" = "Y"
    echo "Applying avatar_asset batches..."
    if test -e $OUT_DIR/batches/batch_001.sql
        for f in $OUT_DIR/batches/batch_*.sql
            echo "Applying: $f"
            psql "$DBURL" -v ON_ERROR_STOP=1 -f "$f"
            if test $status -ne 0
                echo "Error applying $f; aborting. Check logs and rollback if needed."
                exit 1
            end
        end
    else
        echo "No avatar_asset batch files found in $OUT_DIR/batches; skipping."
    end

    echo "Applying user_avatar batches..."
    if test -e $OUT_DIR/batches_user_avatar/batch_001.sql
        for f in $OUT_DIR/batches_user_avatar/batch_*.sql
            echo "Applying: $f"
            psql "$DBURL" -v ON_ERROR_STOP=1 -f "$f"
            if test $status -ne 0
                echo "Error applying $f; aborting. Check logs and rollback if needed."
                exit 1
            end
        end
    else
        echo "No user_avatar batch files found in $OUT_DIR/batches_user_avatar; skipping."
    end

    echo "Batches applied. Run verification queries and smoke tests."
else
    echo "Apply aborted by user. Inspect mapping and ambiguous list before applying."
end

echo "Done."
