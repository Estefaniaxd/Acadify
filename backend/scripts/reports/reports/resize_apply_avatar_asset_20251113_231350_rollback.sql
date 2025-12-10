-- Rollback SQL generated template. This requires that you run the psql \copy snapshot first to '/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/scripts/reports/reports/preapply_resize_avatar_asset_snapshot_20251113_231350.csv'.
-- After running the copy, run the following to revert values (this file assumes the snapshot CSV exists at the path above).
-- The snapshot contains columns: id,filename,width,height,file_size,sha256


-- Example Python snippet to generate rollback from the CSV:
-- import csv
-- with open('/run/media/arch/Storage/SENA/Proyecto-Formativo/Acadify/backend/scripts/reports/reports/preapply_resize_avatar_asset_snapshot_20251113_231350.csv', encoding='utf-8') as fh:
--     r = csv.DictReader(fh)
--     for row in r:
--         print(f"UPDATE avatar_asset SET width = {row['width']}, height = {row['height']}, file_size = {row['file_size']}, sha256 = '{row['sha256']}' WHERE id = {row['id']};")
