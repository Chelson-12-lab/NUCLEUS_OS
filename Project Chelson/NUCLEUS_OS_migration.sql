-- ============================================================
-- NUCLEUS OS - Database Migration
-- CBSE Class 12 Computer Science Project (fictional simulation)
--
-- Run this ONCE against the existing nucleus_os database:
--     mysql -u root -p nucleus_os < NUCLEUS_OS_migration.sql
--
-- What it does:
--   1. Cleans and rebuilds employee_exposure so there is exactly ONE
--      row per registered user, linked to users.user_id by a foreign key
--      and protected by a unique constraint.
--   2. Adds the extended task columns to safety_tasks.
--   3. Creates task_review_log, safety_task_messages and
--      equipment_generation_log.
--   4. Creates alert_notifications if it does not already exist.
--
-- It does NOT touch the employees table, does NOT delete users, and does
-- NOT delete equipment / maintenance / waste / reactor records.
-- ============================================================

USE nucleus_os;

-- MySQL Workbench enables "Safe Updates" by default, which blocks
-- DELETE/UPDATE statements that have no WHERE clause. This migration
-- intentionally clears the whole employee_exposure table, so safe
-- updates are switched off for this script only and restored at the end.
SET SQL_SAFE_UPDATES = 0;

-- ------------------------------------------------------------
-- 1. USERS - full_name column
--    Older databases were created without full_name, which breaks
--    sign-up and the Employee Exposure module.
-- ------------------------------------------------------------

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='users' AND COLUMN_NAME='full_name');
SET @sql := IF(@c=0,
    'ALTER TABLE users ADD COLUMN full_name VARCHAR(100) AFTER user_id',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Give existing accounts a readable default so no name is blank.
UPDATE users
SET full_name = username
WHERE full_name IS NULL OR TRIM(full_name) = '';

-- ------------------------------------------------------------
-- 2. EMPLOYEE EXPOSURE
-- ------------------------------------------------------------

-- Create the table if this older database never had it, so the script
-- works on any existing nucleus_os database.
CREATE TABLE IF NOT EXISTS employee_exposure (
    exposure_id      INT AUTO_INCREMENT PRIMARY KEY,
    employee_id      INT NOT NULL,
    daily_exposure   DECIMAL(10,4) DEFAULT 0,
    monthly_exposure DECIMAL(10,4) DEFAULT 0,
    safe_limit       DECIMAL(10,4) DEFAULT 1.0000,
    limit_status     VARCHAR(30)   DEFAULT 'Normal',
    recorded_date    DATETIME      DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Make sure every column the program uses is present, even on very old
-- copies of the table.
SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='employee_exposure' AND COLUMN_NAME='daily_exposure');
SET @sql := IF(@c=0, 'ALTER TABLE employee_exposure ADD COLUMN daily_exposure DECIMAL(10,4) DEFAULT 0', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='employee_exposure' AND COLUMN_NAME='monthly_exposure');
SET @sql := IF(@c=0, 'ALTER TABLE employee_exposure ADD COLUMN monthly_exposure DECIMAL(10,4) DEFAULT 0', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='employee_exposure' AND COLUMN_NAME='safe_limit');
SET @sql := IF(@c=0, 'ALTER TABLE employee_exposure ADD COLUMN safe_limit DECIMAL(10,4) DEFAULT 1.0000', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='employee_exposure' AND COLUMN_NAME='limit_status');
SET @sql := IF(@c=0, "ALTER TABLE employee_exposure ADD COLUMN limit_status VARCHAR(30) DEFAULT 'Normal'", 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='employee_exposure' AND COLUMN_NAME='recorded_date');
SET @sql := IF(@c=0, 'ALTER TABLE employee_exposure ADD COLUMN recorded_date DATETIME DEFAULT CURRENT_TIMESTAMP', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Remove any foreign key / unique constraint left from an earlier attempt
-- so the script can be re-run safely.
SET @fk := (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'employee_exposure'
              AND CONSTRAINT_NAME = 'fk_employee_exposure_user');
SET @sql := IF(@fk > 0,
    'ALTER TABLE employee_exposure DROP FOREIGN KEY fk_employee_exposure_user',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Drop ANY other foreign key on employee_exposure (for example an old one
-- pointing at the unused employees table). Such a key would reject the new
-- user-linked rows, so it must go before the rebuild.
SET @oldfk := (SELECT GROUP_CONCAT(DISTINCT CONSTRAINT_NAME)
               FROM information_schema.KEY_COLUMN_USAGE
               WHERE TABLE_SCHEMA = DATABASE()
                 AND TABLE_NAME = 'employee_exposure'
                 AND COLUMN_NAME = 'employee_id'
                 AND REFERENCED_TABLE_NAME IS NOT NULL);
SET @sql := IF(@oldfk IS NULL, 'SELECT 1',
    CONCAT('ALTER TABLE employee_exposure DROP FOREIGN KEY ', SUBSTRING_INDEX(@oldfk, ',', 1)));
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @uk := (SELECT COUNT(*) FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'employee_exposure'
              AND INDEX_NAME = 'uk_employee_exposure_employee');
SET @sql := IF(@uk > 0,
    'ALTER TABLE employee_exposure DROP INDEX uk_employee_exposure_employee',
    'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Delete ALL existing exposure records (no archiving), then rebuild one
-- record per registered user with zeroed exposure values.
DELETE FROM employee_exposure;

INSERT INTO employee_exposure
    (employee_id, daily_exposure, monthly_exposure,
     safe_limit, limit_status, recorded_date)
SELECT user_id, 0, 0, 1.0000, 'Normal', NOW()
FROM users;

-- One exposure record per user.
ALTER TABLE employee_exposure
    ADD CONSTRAINT uk_employee_exposure_employee UNIQUE (employee_id);

-- Link exposure to the real user account. Deleting a user removes the
-- matching exposure row automatically.
ALTER TABLE employee_exposure
    ADD CONSTRAINT fk_employee_exposure_user
    FOREIGN KEY (employee_id) REFERENCES users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- ------------------------------------------------------------
-- 3. SAFETY TASKS - extended columns
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS safety_tasks (
    task_id            INT AUTO_INCREMENT PRIMARY KEY,
    task_title         VARCHAR(200),
    task_description   VARCHAR(1000),
    condition_detected VARCHAR(255) NOT NULL,
    recommendation     VARCHAR(500) NOT NULL,
    priority           VARCHAR(30)  DEFAULT 'HIGH',
    task_source        VARCHAR(30)  DEFAULT 'Automatic',
    assigned_by        VARCHAR(100),
    assigned_to        VARCHAR(100),
    assigned_role      VARCHAR(50),
    assigned_date      DATETIME,
    due_date           DATE,
    task_status        VARCHAR(40)  DEFAULT 'Pending Assignment',
    admin_review       VARCHAR(60)  DEFAULT 'Pending',
    created_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at          DATETIME
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add the new columns only if they are missing (safe on older installs).
SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='safety_tasks' AND COLUMN_NAME='task_title');
SET @sql := IF(@c=0, 'ALTER TABLE safety_tasks ADD COLUMN task_title VARCHAR(200)', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='safety_tasks' AND COLUMN_NAME='task_description');
SET @sql := IF(@c=0, 'ALTER TABLE safety_tasks ADD COLUMN task_description VARCHAR(1000)', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='safety_tasks' AND COLUMN_NAME='task_source');
SET @sql := IF(@c=0, "ALTER TABLE safety_tasks ADD COLUMN task_source VARCHAR(30) DEFAULT 'Automatic'", 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='safety_tasks' AND COLUMN_NAME='assigned_date');
SET @sql := IF(@c=0, 'ALTER TABLE safety_tasks ADD COLUMN assigned_date DATETIME', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @c := (SELECT COUNT(*) FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='safety_tasks' AND COLUMN_NAME='due_date');
SET @sql := IF(@c=0, 'ALTER TABLE safety_tasks ADD COLUMN due_date DATE', 'SELECT 1');
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ------------------------------------------------------------
-- 4. TASK MESSAGES AND ADMIN REVIEW AUDIT LOG
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS safety_task_messages (
    message_id      INT AUTO_INCREMENT PRIMARY KEY,
    task_id         INT NOT NULL,
    sender_username VARCHAR(100) NOT NULL,
    sender_role     VARCHAR(50)  NOT NULL,
    message_type    VARCHAR(40)  NOT NULL,
    message_text    VARCHAR(1000) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_safety_task_messages_task (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS task_review_log (
    review_id     INT AUTO_INCREMENT PRIMARY KEY,
    task_id       INT NOT NULL,
    reviewed_by   VARCHAR(100) NOT NULL,
    review_action VARCHAR(60)  NOT NULL,
    feedback      VARCHAR(1000),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY idx_task_review_log_task (task_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 5. EQUIPMENT GENERATION MILESTONE LOG
--    Guarantees each 20-completion milestone creates equipment once.
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS equipment_generation_log (
    generation_id       INT AUTO_INCREMENT PRIMARY KEY,
    completed_milestone INT NOT NULL,
    equipment_created   INT NOT NULL DEFAULT 10,
    generated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY completed_milestone (completed_milestone)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 6. NOTIFICATION CENTRE
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS alert_notifications (
    notification_id    INT AUTO_INCREMENT PRIMARY KEY,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipient_role     VARCHAR(50) NOT NULL,
    severity           VARCHAR(30),
    condition_detected VARCHAR(255),
    message            VARCHAR(500),
    status             VARCHAR(20) DEFAULT 'Unread'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ------------------------------------------------------------
-- 7. VERIFICATION QUERIES (optional - run manually)
-- ------------------------------------------------------------
-- SELECT COUNT(*) AS users FROM users;
-- SELECT COUNT(*) AS exposure_rows FROM employee_exposure;
-- SELECT u.user_id, u.username, e.daily_exposure, e.monthly_exposure
--   FROM users u LEFT JOIN employee_exposure e ON e.employee_id = u.user_id;

-- Restore Workbench's safety setting.
SET SQL_SAFE_UPDATES = 1;
