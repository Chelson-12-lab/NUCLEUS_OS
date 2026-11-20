-- NUCLEUS OS cleanup migration for an already-created database.
-- Run this while connected to the nucleus_os database.

DROP TABLE IF EXISTS `career_records`;
DROP TABLE IF EXISTS `payroll`;
DROP TABLE IF EXISTS `nuclear_power_plants`;

-- Remove the legacy plant_id column from reactors only if it exists.
SET @has_plant_id = (
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'reactors'
      AND COLUMN_NAME = 'plant_id'
);
SET @drop_plant_id_sql = IF(
    @has_plant_id > 0,
    'ALTER TABLE `reactors` DROP COLUMN `plant_id`',
    'SELECT ''reactors.plant_id is already absent'' AS migration_status'
);
PREPARE nucleus_stmt FROM @drop_plant_id_sql;
EXECUTE nucleus_stmt;
DEALLOCATE PREPARE nucleus_stmt;
