-- NUCLEUS OS - FULL DATABASE SETUP
-- Educational console-project demo data only.
-- All readings, dates, quantities, and names below are fictional.
-- They are NOT real nuclear plant data, safety limits, or operating instructions.

CREATE DATABASE IF NOT EXISTS nucleus_os
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nucleus_os;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS safety_task_messages;
DROP TABLE IF EXISTS safety_tasks;
DROP TABLE IF EXISTS alert_notifications;
DROP TABLE IF EXISTS intelligent_recommendations;
DROP TABLE IF EXISTS maintenance;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS safety_records;
DROP TABLE IF EXISTS waste_storage;
DROP TABLE IF EXISTS radioactive_waste;
DROP TABLE IF EXISTS radiation_monitoring;
DROP TABLE IF EXISTS fuel_rod_tracking;
DROP TABLE IF EXISTS fuel_management;
DROP TABLE IF EXISTS power_generation;
DROP TABLE IF EXISTS reactors;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL,
    role VARCHAR(30) NOT NULL
);

CREATE TABLE reactors (
    reactor_id INT AUTO_INCREMENT PRIMARY KEY,
    reactor_type VARCHAR(100),
    capacity DECIMAL(12,2),
    operating_status VARCHAR(50)
);

CREATE TABLE power_generation (
    generation_id INT AUTO_INCREMENT PRIMARY KEY,
    reactor_id INT,
    generation_date DATE,
    electricity_generated DECIMAL(15,2)
);

CREATE TABLE fuel_management (
    fuel_id INT AUTO_INCREMENT PRIMARY KEY,
    reactor_id INT,
    fuel_type VARCHAR(100),
    quantity DECIMAL(12,2),
    usage_status VARCHAR(50)
);

CREATE TABLE fuel_rod_tracking (
    rod_id INT AUTO_INCREMENT PRIMARY KEY,
    reactor_id INT,
    installation_date DATE,
    remaining_life DECIMAL(10,2)
);

CREATE TABLE radiation_monitoring (
    sensor_record_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_name VARCHAR(100) NOT NULL,
    radiation_reading DECIMAL(12,4),
    alert_generation VARCHAR(50),
    area_monitoring VARCHAR(150),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE radioactive_waste (
    waste_id INT AUTO_INCREMENT PRIMARY KEY,
    waste_category VARCHAR(100),
    radiation_level DECIMAL(12,4),
    storage_assignment VARCHAR(150)
);

CREATE TABLE waste_storage (
    storage_id INT AUTO_INCREMENT PRIMARY KEY,
    storage_building VARCHAR(100),
    capacity DECIMAL(12,2),
    available_space DECIMAL(12,2),
    inspection_records VARCHAR(500)
);

CREATE TABLE safety_records (
    safety_id INT AUTO_INCREMENT PRIMARY KEY,
    safety_title VARCHAR(150),
    safety_description VARCHAR(500),
    risk_level VARCHAR(50),
    action_required VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100),
    equipment_type VARCHAR(100),
    equipment_status VARCHAR(50)
);

CREATE TABLE maintenance (
    maintenance_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100),
    maintenance_date DATE,
    maintenance_status VARCHAR(100)
);

CREATE TABLE intelligent_recommendations (
    recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_by VARCHAR(100),
    role VARCHAR(50),
    severity VARCHAR(30),
    condition_detected VARCHAR(255),
    recommendation VARCHAR(500),
    priority INT,
    status VARCHAR(30) DEFAULT 'Pending'
);

CREATE TABLE alert_notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recipient_role VARCHAR(50) NOT NULL,
    severity VARCHAR(30),
    condition_detected VARCHAR(255),
    message VARCHAR(500),
    status VARCHAR(20) DEFAULT 'Unread'
);

CREATE TABLE safety_tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    condition_detected VARCHAR(255) NOT NULL,
    recommendation VARCHAR(500) NOT NULL,
    priority VARCHAR(30),
    assigned_by VARCHAR(100),
    assigned_to VARCHAR(100),
    assigned_role VARCHAR(50),
    task_status VARCHAR(30) DEFAULT 'Pending',
    admin_review VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL
);

CREATE TABLE safety_task_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id INT NOT NULL,
    sender_username VARCHAR(100),
    sender_role VARCHAR(50),
    message_type VARCHAR(40),
    message_text VARCHAR(1000),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Four fictional demo accounts. example.com addresses are placeholders.
INSERT INTO users (full_name, username, password, email, role) VALUES
('Arun Kumar', 'arun.kumar', 'demo_admin_01', 'arun.kumar@example.com', 'Admin'),
('Rahul Daniel', 'rahul.daniel', 'demo_manager_01', 'rahul.daniel@example.com', 'Plant Manager'),
('Vijay Raj', 'vijay.raj', 'demo_engineer_01', 'vijay.raj@example.com', 'Engineer'),
('Kavin Joseph', 'kavin.joseph', 'demo_safety_01', 'kavin.joseph@example.com', 'Safety Officer');

-- Exactly 20 fictional demo records in each operational module table.
INSERT INTO reactors (reactor_type, capacity, operating_status) VALUES
('PHWR Demo', 525, 'Standby'),
('BWR Demo', 550, 'Maintenance'),
('PWR Demo', 575, 'Simulation'),
('PHWR Demo', 600, 'Standby'),
('BWR Demo', 625, 'Maintenance'),
('PWR Demo', 650, 'Simulation'),
('PHWR Demo', 675, 'Standby'),
('BWR Demo', 700, 'Maintenance'),
('PWR Demo', 725, 'Simulation'),
('PHWR Demo', 750, 'Standby'),
('BWR Demo', 775, 'Maintenance'),
('PWR Demo', 800, 'Simulation'),
('PHWR Demo', 825, 'Standby'),
('BWR Demo', 850, 'Maintenance'),
('PWR Demo', 875, 'Simulation'),
('PHWR Demo', 900, 'Standby'),
('BWR Demo', 925, 'Maintenance'),
('PWR Demo', 950, 'Simulation'),
('PHWR Demo', 975, 'Standby'),
('BWR Demo', 1000, 'Maintenance');

INSERT INTO power_generation (reactor_id, generation_date, electricity_generated) VALUES
(1, 2, '2026-01-02', 127.35),
(2, 3, '2026-01-03', 134.7),
(3, 4, '2026-01-04', 142.05),
(4, 5, '2026-01-05', 149.4),
(5, 6, '2026-01-06', 156.75),
(6, 7, '2026-01-07', 164.1),
(7, 8, '2026-01-08', 171.45),
(8, 9, '2026-01-09', 178.8),
(9, 10, '2026-01-10', 186.15),
(10, 11, '2026-01-11', 193.5),
(11, 12, '2026-01-12', 200.85),
(12, 13, '2026-01-13', 208.2),
(13, 14, '2026-01-14', 215.55),
(14, 15, '2026-01-15', 222.9),
(15, 16, '2026-01-16', 230.25),
(16, 17, '2026-01-17', 237.6),
(17, 18, '2026-01-18', 244.95),
(18, 19, '2026-01-19', 252.3),
(19, 20, '2026-01-20', 259.65),
(20, 1, '2026-01-21', 267.0);

INSERT INTO fuel_management (reactor_id, fuel_type, quantity, usage_status) VALUES
(2, 'Demo Fuel B', 23.1, 'In Use'),
(3, 'Demo Fuel A', 26.2, 'Low'),
(4, 'Demo Fuel B', 29.3, 'Available'),
(5, 'Demo Fuel A', 32.4, 'In Use'),
(6, 'Demo Fuel B', 35.5, 'Low'),
(7, 'Demo Fuel A', 38.6, 'Available'),
(8, 'Demo Fuel B', 41.7, 'In Use'),
(9, 'Demo Fuel A', 44.8, 'Low'),
(10, 'Demo Fuel B', 47.9, 'Available'),
(11, 'Demo Fuel A', 51.0, 'In Use'),
(12, 'Demo Fuel B', 54.1, 'Low'),
(13, 'Demo Fuel A', 57.2, 'Available'),
(14, 'Demo Fuel B', 60.3, 'In Use'),
(15, 'Demo Fuel A', 63.4, 'Low'),
(16, 'Demo Fuel B', 66.5, 'Available'),
(17, 'Demo Fuel A', 69.6, 'In Use'),
(18, 'Demo Fuel B', 72.7, 'Low'),
(19, 'Demo Fuel A', 75.8, 'Available'),
(20, 'Demo Fuel B', 78.9, 'In Use'),
(1, 'Demo Fuel A', 82.0, 'Low');

INSERT INTO fuel_rod_tracking (reactor_id, installation_date, remaining_life) VALUES
(2, '2023-01-12', 14.7),
(3, '2023-01-23', 17.4),
(4, '2023-02-03', 20.1),
(5, '2023-02-14', 22.8),
(6, '2023-02-25', 25.5),
(7, '2023-03-08', 28.2),
(8, '2023-03-19', 30.9),
(9, '2023-03-30', 33.6),
(10, '2023-04-10', 36.3),
(11, '2023-04-21', 39.0),
(12, '2023-05-02', 41.7),
(13, '2023-05-13', 44.4),
(14, '2023-05-24', 47.1),
(15, '2023-06-04', 49.8),
(16, '2023-06-15', 52.5),
(17, '2023-06-26', 55.2),
(18, '2023-07-07', 57.9),
(19, '2023-07-18', 60.6),
(20, '2023-07-29', 63.3),
(1, '2023-08-09', 66.0);

INSERT INTO radiation_monitoring (sensor_name, radiation_reading, alert_generation, area_monitoring) VALUES
('RAD-001', 0.28, 'No', 'Reactor Building'),
('RAD-002', 0.46, 'No', 'Turbine Building'),
('RAD-003', 0.64, 'No', 'Control Room'),
('RAD-004', 0.82, 'No', 'Fuel Handling Area'),
('RAD-005', 1.0, 'Yes', 'Waste Storage Area'),
('RAD-006', 1.18, 'Yes', 'Reactor Area'),
('RAD-007', 0.1, 'No', 'Monitoring Room'),
('RAD-008', 0.28, 'No', 'Equipment Area'),
('RAD-009', 0.46, 'No', 'Reactor Building'),
('RAD-010', 0.64, 'No', 'Turbine Building'),
('RAD-011', 0.82, 'No', 'Control Room'),
('RAD-012', 1.0, 'Yes', 'Fuel Handling Area'),
('RAD-013', 1.18, 'Yes', 'Waste Storage Area'),
('RAD-014', 0.1, 'No', 'Reactor Area'),
('RAD-015', 0.28, 'No', 'Monitoring Room'),
('RAD-016', 0.46, 'No', 'Equipment Area'),
('RAD-017', 0.64, 'No', 'Reactor Building'),
('RAD-018', 0.82, 'No', 'Turbine Building'),
('RAD-019', 1.0, 'Yes', 'Control Room'),
('RAD-020', 1.18, 'Yes', 'Fuel Handling Area');

INSERT INTO radioactive_waste (waste_category, radiation_level, storage_assignment) VALUES
('Demo liquid waste', 0.25, 'Storage Zone 2'),
('Demo protective material', 0.4, 'Storage Zone 3'),
('Demo solid waste', 0.55, 'Storage Zone 4'),
('Demo liquid waste', 0.7, 'Storage Zone 5'),
('Demo protective material', 0.85, 'Storage Zone 1'),
('Demo solid waste', 1.0, 'Storage Zone 2'),
('Demo liquid waste', 1.15, 'Storage Zone 3'),
('Demo protective material', 0.1, 'Storage Zone 4'),
('Demo solid waste', 0.25, 'Storage Zone 5'),
('Demo liquid waste', 0.4, 'Storage Zone 1'),
('Demo protective material', 0.55, 'Storage Zone 2'),
('Demo solid waste', 0.7, 'Storage Zone 3'),
('Demo liquid waste', 0.85, 'Storage Zone 4'),
('Demo protective material', 1.0, 'Storage Zone 5'),
('Demo solid waste', 1.15, 'Storage Zone 1'),
('Demo liquid waste', 0.1, 'Storage Zone 2'),
('Demo protective material', 0.25, 'Storage Zone 3'),
('Demo solid waste', 0.4, 'Storage Zone 4'),
('Demo liquid waste', 0.55, 'Storage Zone 5'),
('Demo protective material', 0.7, 'Storage Zone 1');

INSERT INTO waste_storage (storage_building, capacity, available_space, inspection_records) VALUES
('Demo Storage 01', 1100, 781.0, 'Fictional inspection record 1'),
('Demo Storage 02', 1200, 804.0, 'Fictional inspection record 2'),
('Demo Storage 03', 1300, 819.0, 'Fictional inspection record 3'),
('Demo Storage 04', 1400, 826.0, 'Fictional inspection record 4'),
('Demo Storage 05', 1500, 1125.0, 'Fictional inspection record 5'),
('Demo Storage 06', 1600, 1136.0, 'Fictional inspection record 6'),
('Demo Storage 07', 1700, 1139.0, 'Fictional inspection record 7'),
('Demo Storage 08', 1800, 1134.0, 'Fictional inspection record 8'),
('Demo Storage 09', 1900, 1121.0, 'Fictional inspection record 9'),
('Demo Storage 10', 2000, 1500.0, 'Fictional inspection record 10'),
('Demo Storage 11', 2100, 1491.0, 'Fictional inspection record 11'),
('Demo Storage 12', 2200, 1474.0, 'Fictional inspection record 12'),
('Demo Storage 13', 2300, 1449.0, 'Fictional inspection record 13'),
('Demo Storage 14', 2400, 1416.0, 'Fictional inspection record 14'),
('Demo Storage 15', 2500, 1875.0, 'Fictional inspection record 15'),
('Demo Storage 16', 2600, 1846.0, 'Fictional inspection record 16'),
('Demo Storage 17', 2700, 1809.0, 'Fictional inspection record 17'),
('Demo Storage 18', 2800, 1764.0, 'Fictional inspection record 18'),
('Demo Storage 19', 2900, 1711.0, 'Fictional inspection record 19'),
('Demo Storage 20', 3000, 2250.0, 'Fictional inspection record 20');

INSERT INTO safety_records (safety_title, safety_description, risk_level, action_required) VALUES
('Demo Inspection 01', 'Fictional safety inspection description 1.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 02', 'Fictional safety inspection description 2.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 03', 'Fictional safety inspection description 3.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 04', 'Fictional safety inspection description 4.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 05', 'Fictional safety inspection description 5.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 06', 'Fictional safety inspection description 6.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 07', 'Fictional safety inspection description 7.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 08', 'Fictional safety inspection description 8.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 09', 'Fictional safety inspection description 9.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 10', 'Fictional safety inspection description 10.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 11', 'Fictional safety inspection description 11.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 12', 'Fictional safety inspection description 12.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 13', 'Fictional safety inspection description 13.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 14', 'Fictional safety inspection description 14.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 15', 'Fictional safety inspection description 15.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 16', 'Fictional safety inspection description 16.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 17', 'Fictional safety inspection description 17.', 'High', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 18', 'Fictional safety inspection description 18.', 'Low', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 19', 'Fictional safety inspection description 19.', 'Medium', 'Review through the project''s simulated reporting workflow.'),
('Demo Inspection 20', 'Fictional safety inspection description 20.', 'High', 'Review through the project''s simulated reporting workflow.');

INSERT INTO equipment (equipment_name, equipment_type, equipment_status) VALUES
('Demo Equipment 01', 'Pump model', 'Fair'),
('Demo Equipment 02', 'Monitoring unit', 'Poor'),
('Demo Equipment 03', 'Display unit', 'Good'),
('Demo Equipment 04', 'Sensor', 'Fair'),
('Demo Equipment 05', 'Pump model', 'Poor'),
('Demo Equipment 06', 'Monitoring unit', 'Good'),
('Demo Equipment 07', 'Display unit', 'Fair'),
('Demo Equipment 08', 'Sensor', 'Poor'),
('Demo Equipment 09', 'Pump model', 'Good'),
('Demo Equipment 10', 'Monitoring unit', 'Fair'),
('Demo Equipment 11', 'Display unit', 'Poor'),
('Demo Equipment 12', 'Sensor', 'Good'),
('Demo Equipment 13', 'Pump model', 'Fair'),
('Demo Equipment 14', 'Monitoring unit', 'Poor'),
('Demo Equipment 15', 'Display unit', 'Good'),
('Demo Equipment 16', 'Sensor', 'Fair'),
('Demo Equipment 17', 'Pump model', 'Poor'),
('Demo Equipment 18', 'Monitoring unit', 'Good'),
('Demo Equipment 19', 'Display unit', 'Fair'),
('Demo Equipment 20', 'Sensor', 'Poor');

INSERT INTO maintenance (equipment_name, maintenance_date, maintenance_status) VALUES
('Demo Equipment 01', '2026-01-06', 'In Progress'),
('Demo Equipment 02', '2026-01-11', 'Completed'),
('Demo Equipment 03', '2026-01-16', 'Pending'),
('Demo Equipment 04', '2026-01-21', 'In Progress'),
('Demo Equipment 05', '2026-01-26', 'Completed'),
('Demo Equipment 06', '2026-01-31', 'Pending'),
('Demo Equipment 07', '2026-02-05', 'In Progress'),
('Demo Equipment 08', '2026-02-10', 'Completed'),
('Demo Equipment 09', '2026-02-15', 'Pending'),
('Demo Equipment 10', '2026-02-20', 'In Progress'),
('Demo Equipment 11', '2026-02-25', 'Completed'),
('Demo Equipment 12', '2026-03-02', 'Pending'),
('Demo Equipment 13', '2026-03-07', 'In Progress'),
('Demo Equipment 14', '2026-03-12', 'Completed'),
('Demo Equipment 15', '2026-03-17', 'Pending'),
('Demo Equipment 16', '2026-03-22', 'In Progress'),
('Demo Equipment 17', '2026-03-27', 'Completed'),
('Demo Equipment 18', '2026-04-01', 'Pending'),
('Demo Equipment 19', '2026-04-06', 'In Progress'),
('Demo Equipment 20', '2026-04-11', 'Completed');

-- Initial notification examples for all four roles.
INSERT INTO alert_notifications
(recipient_role, severity, condition_detected, message, status) VALUES
('Admin','INFO','Demo system initialised','The fictional NUCLEUS OS demonstration database is ready.','Unread'),
('Plant Manager','INFO','Demo system initialised','The fictional NUCLEUS OS demonstration database is ready.','Unread'),
('Engineer','INFO','Demo system initialised','The fictional NUCLEUS OS demonstration database is ready.','Unread'),
('Safety Officer','INFO','Demo system initialised','The fictional NUCLEUS OS demonstration database is ready.','Unread');

-- Initial recommendations: 20 history rows for this history module.
INSERT INTO intelligent_recommendations (generated_by, role, severity, condition_detected, recommendation, priority, status) VALUES
('Database Setup', 'Plant Manager', 'WARNING', 'Fictional demo condition 1', 'Review demo record 1 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Engineer', 'HIGH', 'Fictional demo condition 2', 'Review demo record 2 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Safety Officer', 'INFO', 'Fictional demo condition 3', 'Review demo record 3 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Admin', 'WARNING', 'Fictional demo condition 4', 'Review demo record 4 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Plant Manager', 'HIGH', 'Fictional demo condition 5', 'Review demo record 5 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Engineer', 'INFO', 'Fictional demo condition 6', 'Review demo record 6 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Safety Officer', 'WARNING', 'Fictional demo condition 7', 'Review demo record 7 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Admin', 'HIGH', 'Fictional demo condition 8', 'Review demo record 8 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Plant Manager', 'INFO', 'Fictional demo condition 9', 'Review demo record 9 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Engineer', 'WARNING', 'Fictional demo condition 10', 'Review demo record 10 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Safety Officer', 'HIGH', 'Fictional demo condition 11', 'Review demo record 11 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Admin', 'INFO', 'Fictional demo condition 12', 'Review demo record 12 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Plant Manager', 'WARNING', 'Fictional demo condition 13', 'Review demo record 13 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Engineer', 'HIGH', 'Fictional demo condition 14', 'Review demo record 14 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Safety Officer', 'INFO', 'Fictional demo condition 15', 'Review demo record 15 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Admin', 'WARNING', 'Fictional demo condition 16', 'Review demo record 16 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Plant Manager', 'HIGH', 'Fictional demo condition 17', 'Review demo record 17 in the relevant module.', 3, 'Pending'),
('Database Setup', 'Engineer', 'INFO', 'Fictional demo condition 18', 'Review demo record 18 in the relevant module.', 1, 'Pending'),
('Database Setup', 'Safety Officer', 'WARNING', 'Fictional demo condition 19', 'Review demo record 19 in the relevant module.', 2, 'Pending'),
('Database Setup', 'Admin', 'HIGH', 'Fictional demo condition 20', 'Review demo record 20 in the relevant module.', 3, 'Pending');

-- Task tables intentionally start empty; task rows are created by Admin workflow.
-- Employee and employee_exposure tables are intentionally excluded per project decision.
-- nuclear_power_plants table is intentionally excluded per project decision.

SHOW TABLES;
