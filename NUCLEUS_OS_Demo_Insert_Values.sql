-- ==============================================================
-- NUCLEUS OS - DEMO INSERT VALUES
-- Designed against the supplied NUCLEUS_OS Python project schema.
-- All records are fictional educational simulation data.
-- Run the FULL DATABASE SETUP first, then run this file.
--
-- INSERT IGNORE + fixed IDs help avoid duplicate-key errors if
-- this seed file is run more than once. Existing rows are not replaced.
-- The IDs below assume a fresh schema or matching parent IDs.
-- ==============================================================

USE nucleus_os;

-- USERS (demo login accounts; change passwords after demonstration)
INSERT IGNORE INTO users
(user_id, full_name, username, password, email, role) VALUES
(1,'NUCLEUS Administrator','admin','admin123','admin@example.com','Admin'),
(2,'Plant Manager Demo','manager','manager123','manager@example.com','Plant Manager'),
(3,'Project Engineer Demo','engineer','engineer123','engineer@example.com','Engineer'),
(4,'Safety Officer Demo','safety','safety123','safety@example.com','Safety Officer');

-- NUCLEAR POWER PLANTS
INSERT IGNORE INTO nuclear_power_plants (plant_id, plant_name, location) VALUES
(1,'Demo Nuclear Plant Alpha','Tamil Nadu - Demo'),
(2,'Demo Nuclear Plant Beta','Gujarat - Demo'),
(3,'Demo Nuclear Plant Gamma','Maharashtra - Demo'),
(4,'Demo Nuclear Plant Delta','Rajasthan - Demo'),
(5,'Demo Nuclear Plant Epsilon','Uttar Pradesh - Demo'),
(6,'Demo Nuclear Plant Zeta','Karnataka - Demo'),
(7,'Demo Nuclear Plant Eta','Andhra Pradesh - Demo'),
(8,'Demo Nuclear Plant Theta','Telangana - Demo'),
(9,'Demo Nuclear Plant Iota','Kerala - Demo'),
(10,'Demo Nuclear Plant Kappa','Odisha - Demo'),
(11,'Demo Nuclear Plant Lambda','West Bengal - Demo'),
(12,'Demo Nuclear Plant Mu','Punjab - Demo'),
(13,'Demo Nuclear Plant Nu','Haryana - Demo'),
(14,'Demo Nuclear Plant Xi','Madhya Pradesh - Demo'),
(15,'Demo Nuclear Plant Omicron','Chhattisgarh - Demo'),
(16,'Demo Nuclear Plant Pi','Goa - Demo'),
(17,'Demo Nuclear Plant Rho','Assam - Demo'),
(18,'Demo Nuclear Plant Sigma','Bihar - Demo'),
(19,'Demo Nuclear Plant Tau','Jharkhand - Demo'),
(20,'Demo Nuclear Plant Upsilon','Delhi - Demo');

-- REACTORS
INSERT IGNORE INTO reactors (reactor_id, plant_id, reactor_type, capacity, operating_status) VALUES
(1,1,'Demo Pressurised Water Reactor',1000,'Operational'),
(2,2,'Demo Pressurised Heavy Water Reactor',700,'Operational'),
(3,3,'Demo Boiling Water Reactor',800,'Operational'),
(4,4,'Demo Pressurised Water Reactor',900,'Maintenance'),
(5,5,'Demo Pressurised Heavy Water Reactor',650,'Operational'),
(6,6,'Demo Pressurised Water Reactor',750,'Operational'),
(7,7,'Demo Boiling Water Reactor',600,'Standby'),
(8,8,'Demo Pressurised Heavy Water Reactor',500,'Operational'),
(9,9,'Demo Pressurised Water Reactor',850,'Operational'),
(10,10,'Demo Boiling Water Reactor',700,'Maintenance'),
(11,11,'Demo Pressurised Heavy Water Reactor',550,'Operational'),
(12,12,'Demo Pressurised Water Reactor',950,'Operational'),
(13,13,'Demo Boiling Water Reactor',650,'Standby'),
(14,14,'Demo Pressurised Heavy Water Reactor',750,'Operational'),
(15,15,'Demo Pressurised Water Reactor',800,'Operational'),
(16,16,'Demo Boiling Water Reactor',600,'Maintenance'),
(17,17,'Demo Pressurised Heavy Water Reactor',700,'Operational'),
(18,18,'Demo Pressurised Water Reactor',900,'Operational'),
(19,19,'Demo Boiling Water Reactor',500,'Standby'),
(20,20,'Demo Pressurised Heavy Water Reactor',650,'Operational');

-- POWER GENERATION
INSERT IGNORE INTO power_generation
(generation_id, reactor_id, generation_date, electricity_generated) VALUES
(1,1,'2026-10-01',21500),(2,2,'2026-10-02',18400),
(3,3,'2026-10-03',19250),(4,4,'2026-10-04',17600),
(5,5,'2026-10-05',16800),(6,6,'2026-10-06',17900),
(7,7,'2026-10-07',15400),(8,8,'2026-10-08',14900),
(9,9,'2026-10-09',20100),(10,10,'2026-10-10',16200),
(11,11,'2026-10-11',15100),(12,12,'2026-10-12',20800),
(13,13,'2026-10-13',15800),(14,14,'2026-10-14',17100),
(15,15,'2026-10-15',18700),(16,16,'2026-10-16',14600),
(17,17,'2026-10-17',16500),(18,18,'2026-10-18',19900),
(19,19,'2026-10-19',14200),(20,20,'2026-10-20',15700);

-- FUEL MANAGEMENT (quantity is a simulated percentage)
INSERT IGNORE INTO fuel_management
(fuel_id, reactor_id, fuel_type, quantity, usage_status) VALUES
(1,1,'Demo Uranium Fuel',75,'Available'),
(2,2,'Demo Uranium Fuel',68,'Available'),
(3,3,'Demo Uranium Fuel',12,'Low'),
(4,4,'Demo Uranium Fuel',82,'Available'),
(5,5,'Demo Uranium Fuel',55,'Available'),
(6,6,'Demo Uranium Fuel',14,'Low'),
(7,7,'Demo Uranium Fuel',91,'Available'),
(8,8,'Demo Uranium Fuel',63,'Available'),
(9,9,'Demo Uranium Fuel',47,'Available'),
(10,10,'Demo Uranium Fuel',11,'Low'),
(11,11,'Demo Uranium Fuel',72,'Available'),
(12,12,'Demo Uranium Fuel',38,'Available'),
(13,13,'Demo Uranium Fuel',86,'Available'),
(14,14,'Demo Uranium Fuel',59,'Available'),
(15,15,'Demo Uranium Fuel',7,'Low'),
(16,16,'Demo Uranium Fuel',44,'Available'),
(17,17,'Demo Uranium Fuel',77,'Available'),
(18,18,'Demo Uranium Fuel',29,'Available'),
(19,19,'Demo Uranium Fuel',66,'Available'),
(20,20,'Demo Uranium Fuel',52,'Available');

-- FUEL ROD TRACKING
INSERT IGNORE INTO fuel_rod_tracking
(rod_id, reactor_id, installation_date, remaining_life) VALUES
(1,1,'2024-01-15',72),(2,2,'2024-02-10',68),
(3,3,'2024-03-05',64),(4,4,'2024-04-12',60),
(5,5,'2024-05-18',58),(6,6,'2024-06-20',55),
(7,7,'2024-07-11',52),(8,8,'2024-08-09',49),
(9,9,'2024-09-14',46),(10,10,'2024-10-22',43),
(11,11,'2024-11-16',40),(12,12,'2024-12-08',38),
(13,13,'2025-01-19',35),(14,14,'2025-02-13',32),
(15,15,'2025-03-21',30),(16,16,'2025-04-17',27),
(17,17,'2025-05-12',24),(18,18,'2025-06-25',22),
(19,19,'2025-07-14',19),(20,20,'2025-08-30',16);

-- RADIATION MONITORING (all values are simulated demo readings)
INSERT IGNORE INTO radiation_monitoring
(sensor_record_id, sensor_name, radiation_reading, alert_generation, area_monitoring, recorded_at) VALUES
(1,'RAD-001',0.18,'No','Reactor Building','2026-10-01 09:00:00'),
(2,'RAD-002',0.12,'No','Turbine Building','2026-10-01 09:05:00'),
(3,'RAD-003',0.09,'No','Control Room','2026-10-01 09:10:00'),
(4,'RAD-004',0.65,'No','Fuel Handling Area','2026-10-01 09:15:00'),
(5,'RAD-005',0.80,'No','Waste Storage Area','2026-10-01 09:20:00'),
(6,'RAD-006',0.35,'No','Reactor Area','2026-10-01 09:25:00'),
(7,'RAD-007',0.15,'No','Radiation Monitoring Room','2026-10-01 09:30:00'),
(8,'RAD-008',0.35,'No','Equipment Area','2026-10-01 09:35:00'),
(9,'RAD-009',1.25,'Yes','Service Corridor','2026-10-01 09:40:00'),
(10,'RAD-010',0.22,'No','Control Room','2026-10-01 09:45:00'),
(11,'RAD-011',0.31,'No','Reactor Building','2026-10-02 09:00:00'),
(12,'RAD-012',0.44,'No','Turbine Building','2026-10-02 09:05:00'),
(13,'RAD-013',0.56,'No','Fuel Handling Area','2026-10-02 09:10:00'),
(14,'RAD-014',0.28,'No','Waste Storage Area','2026-10-02 09:15:00'),
(15,'RAD-015',0.19,'No','Equipment Area','2026-10-02 09:20:00'),
(16,'RAD-016',0.72,'No','Service Corridor','2026-10-02 09:25:00'),
(17,'RAD-017',0.38,'No','Reactor Area','2026-10-02 09:30:00'),
(18,'RAD-018',0.48,'No','Control Room','2026-10-02 09:35:00'),
(19,'RAD-019',2.20,'Yes','Demo Alert Area','2026-10-02 09:40:00'),
(20,'RAD-020',0.25,'No','Turbine Building','2026-10-02 09:45:00');

-- RADIOACTIVE WASTE
INSERT IGNORE INTO radioactive_waste
(waste_id, waste_category, radiation_level, storage_assignment) VALUES
(1,'Low-level demo waste',0.12,'Storage Block A'),
(2,'Low-level demo waste',0.18,'Storage Block A'),
(3,'Intermediate-level demo waste',0.75,'Storage Block B'),
(4,'Low-level demo waste',0.09,'Storage Block A'),
(5,'Intermediate-level demo waste',0.92,'Storage Block B'),
(6,'Low-level demo waste',0.15,'Storage Block C'),
(7,'Low-level demo waste',0.22,'Storage Block A'),
(8,'Intermediate-level demo waste',0.68,'Storage Block B'),
(9,'Low-level demo waste',0.11,'Storage Block C'),
(10,'Low-level demo waste',0.25,'Storage Block A'),
(11,'Intermediate-level demo waste',0.81,'Storage Block B'),
(12,'Low-level demo waste',0.14,'Storage Block C'),
(13,'Low-level demo waste',0.19,'Storage Block A'),
(14,'Intermediate-level demo waste',0.73,'Storage Block B'),
(15,'Low-level demo waste',0.16,'Storage Block C'),
(16,'Low-level demo waste',0.21,'Storage Block A'),
(17,'Intermediate-level demo waste',0.88,'Storage Block B'),
(18,'Low-level demo waste',0.13,'Storage Block C'),
(19,'Low-level demo waste',0.17,'Storage Block A'),
(20,'Intermediate-level demo waste',0.79,'Storage Block B');

-- WASTE STORAGE (capacity and available_space use the same unit)
-- One row is intentionally near-full so the demo recommendation rule can be shown.
INSERT IGNORE INTO waste_storage
(storage_id, storage_building, capacity, available_space, inspection_records) VALUES
(1,'Storage Block A',1000,80,'Demo inspection: routine review recorded'),
(2,'Storage Block B',1200,360,'Demo inspection: satisfactory'),
(3,'Storage Block C',900,540,'Demo inspection: satisfactory'),
(4,'Storage Block D',1100,700,'Demo inspection: satisfactory'),
(5,'Storage Block E',950,500,'Demo inspection: satisfactory'),
(6,'Storage Block F',1050,620,'Demo inspection: satisfactory'),
(7,'Storage Block G',800,400,'Demo inspection: satisfactory'),
(8,'Storage Block H',1250,750,'Demo inspection: satisfactory'),
(9,'Storage Block I',1000,650,'Demo inspection: satisfactory'),
(10,'Storage Block J',1150,800,'Demo inspection: satisfactory'),
(11,'Storage Block K',900,600,'Demo inspection: satisfactory'),
(12,'Storage Block L',1300,900,'Demo inspection: satisfactory'),
(13,'Storage Block M',850,550,'Demo inspection: satisfactory'),
(14,'Storage Block N',1000,700,'Demo inspection: satisfactory'),
(15,'Storage Block O',1200,850,'Demo inspection: satisfactory'),
(16,'Storage Block P',950,650,'Demo inspection: satisfactory'),
(17,'Storage Block Q',1050,750,'Demo inspection: satisfactory'),
(18,'Storage Block R',900,650,'Demo inspection: satisfactory'),
(19,'Storage Block S',1150,850,'Demo inspection: satisfactory'),
(20,'Storage Block T',1000,750,'Demo inspection: satisfactory');

-- SAFETY INSPECTION RECORDS
INSERT IGNORE INTO safety_records
(safety_id, safety_title, safety_description, risk_level, action_required) VALUES
(1,'Demo access-control review','Routine simulated access-control inspection','Low','Record inspection completion'),
(2,'Demo monitoring review','Check that demo monitoring records are present','Low','Continue routine review'),
(3,'Demo equipment review','One equipment record requires follow-up','Medium','Schedule an inspection'),
(4,'Demo storage review','Review storage-block sample records','Medium','Update inspection note'),
(5,'Demo training review','Training record review for project demonstration','Low','Record attendance'),
(6,'Demo signage review','Check sample safety-signage records','Low','Record inspection completion'),
(7,'Demo maintenance review','Review pending maintenance sample','Medium','Assign maintenance review'),
(8,'Demo emergency-plan review','Review the demonstration emergency-plan entry','Medium','Update the sample record'),
(9,'Demo housekeeping review','Routine simulated housekeeping review','Low','Continue routine review'),
(10,'Demo sensor review','Review sensor record availability','Low','Record inspection completion'),
(11,'Demo storage-label review','Review sample storage labels','Medium','Update sample labels'),
(12,'Demo equipment-area review','Routine equipment-area sample inspection','Low','Record inspection completion'),
(13,'Demo procedure review','Review project procedure record','Low','Continue routine review'),
(14,'Demo training follow-up','Follow-up item in fictional training data','Medium','Schedule a training review'),
(15,'Demo maintenance follow-up','Fictional maintenance follow-up item','Medium','Review maintenance status'),
(16,'Demo monitoring follow-up','Fictional monitoring follow-up item','Low','Record inspection completion'),
(17,'Demo waste-record review','Review fictional waste records','Low','Update sample record'),
(18,'Demo audit entry','Routine fictional audit entry','Low','Retain the demo record'),
(19,'Demo inspection follow-up','Fictional inspection follow-up item','Medium','Assign a review'),
(20,'Demo final review','Final sample safety-record review','Low','Record completion');

-- EQUIPMENT
INSERT IGNORE INTO equipment
(equipment_id, equipment_name, equipment_type, equipment_status) VALUES
(1,'Demo Radiation Monitor 1','Monitoring Device','Good'),
(2,'Demo Cooling Pump 1','Pump','Good'),
(3,'Demo Ventilation Unit 1','Ventilation','Fair'),
(4,'Demo Pressure Sensor 1','Sensor','Good'),
(5,'Demo Control Panel 1','Control Equipment','Good'),
(6,'Demo Backup Pump 1','Pump','Fair'),
(7,'Demo Temperature Sensor 1','Sensor','Good'),
(8,'Demo Filtration Unit 1','Filtration','Poor'),
(9,'Demo Alarm Panel 1','Alarm System','Good'),
(10,'Demo Valve Assembly 1','Valve','Good'),
(11,'Demo Radiation Monitor 2','Monitoring Device','Fair'),
(12,'Demo Cooling Pump 2','Pump','Good'),
(13,'Demo Ventilation Unit 2','Ventilation','Good'),
(14,'Demo Pressure Sensor 2','Sensor','Good'),
(15,'Demo Control Panel 2','Control Equipment','Fair'),
(16,'Demo Backup Pump 2','Pump','Good'),
(17,'Demo Temperature Sensor 2','Sensor','Good'),
(18,'Demo Filtration Unit 2','Filtration','Good'),
(19,'Demo Alarm Panel 2','Alarm System','Good'),
(20,'Demo Valve Assembly 2','Valve','Good');

-- MAINTENANCE (past dates + Pending status intentionally demonstrate overdue-rule detection)
INSERT IGNORE INTO maintenance
(maintenance_id, equipment_name, maintenance_date, maintenance_status) VALUES
(1,'Demo Radiation Monitor 1','2026-08-01','Pending'),
(2,'Demo Cooling Pump 1','2026-08-05','Completed'),
(3,'Demo Ventilation Unit 1','2026-08-10','In Progress'),
(4,'Demo Pressure Sensor 1','2026-08-15','Completed'),
(5,'Demo Control Panel 1','2026-08-20','Pending'),
(6,'Demo Backup Pump 1','2026-08-25','Completed'),
(7,'Demo Temperature Sensor 1','2026-09-01','In Progress'),
(8,'Demo Filtration Unit 1','2026-09-05','Pending'),
(9,'Demo Alarm Panel 1','2026-09-10','Completed'),
(10,'Demo Valve Assembly 1','2026-09-12','Pending'),
(11,'Demo Radiation Monitor 2','2026-09-15','Completed'),
(12,'Demo Cooling Pump 2','2026-09-18','In Progress'),
(13,'Demo Ventilation Unit 2','2026-09-20','Pending'),
(14,'Demo Pressure Sensor 2','2026-09-22','Completed'),
(15,'Demo Control Panel 2','2026-09-25','Pending'),
(16,'Demo Backup Pump 2','2026-09-28','Completed'),
(17,'Demo Temperature Sensor 2','2026-10-01','Pending'),
(18,'Demo Filtration Unit 2','2026-10-03','In Progress'),
(19,'Demo Alarm Panel 2','2026-10-05','Completed'),
(20,'Demo Valve Assembly 2','2026-10-07','Pending');

-- EMPLOYEE EXPOSURE (illustrative demo values only, not medical/safety limits)
INSERT IGNORE INTO employee_exposure
(exposure_id, employee_id, daily_exposure, monthly_exposure, safe_limit, limit_status, recorded_date) VALUES
(1,101,0.02,0.35,1.00,'Within Limit','2026-10-01'),
(2,102,0.03,0.42,1.00,'Within Limit','2026-10-01'),
(3,103,0.04,1.15,1.00,'Above Limit','2026-10-01'),
(4,104,0.01,0.28,1.00,'Within Limit','2026-10-01'),
(5,105,0.02,0.51,1.00,'Within Limit','2026-10-01'),
(6,106,0.03,0.76,1.00,'Within Limit','2026-10-01'),
(7,107,0.02,0.63,1.00,'Within Limit','2026-10-01'),
(8,108,0.04,1.20,1.00,'Above Limit','2026-10-01'),
(9,109,0.01,0.31,1.00,'Within Limit','2026-10-01'),
(10,110,0.02,0.48,1.00,'Within Limit','2026-10-01'),
(11,111,0.03,0.58,1.00,'Within Limit','2026-10-01'),
(12,112,0.02,0.82,1.00,'Within Limit','2026-10-01'),
(13,113,0.04,1.08,1.00,'Above Limit','2026-10-01'),
(14,114,0.01,0.24,1.00,'Within Limit','2026-10-01'),
(15,115,0.02,0.45,1.00,'Within Limit','2026-10-01'),
(16,116,0.03,0.69,1.00,'Within Limit','2026-10-01'),
(17,117,0.02,0.55,1.00,'Within Limit','2026-10-01'),
(18,118,0.03,0.91,1.00,'Within Limit','2026-10-01'),
(19,119,0.01,0.33,1.00,'Within Limit','2026-10-01'),
(20,120,0.02,0.47,1.00,'Within Limit','2026-10-01');

-- Seed one example recommendation and role notifications for the dashboard.
INSERT IGNORE INTO intelligent_recommendations
(recommendation_id, generated_by, role, severity, condition_detected, recommendation, priority, status) VALUES
(1,'Demo System','System','HIGH','Demo fuel level below 15%: Reactor 3','Project simulation: schedule a review of the demo fuel inventory.',2,'Pending');

INSERT IGNORE INTO alert_notifications
(notification_id, recipient_role, severity, condition_detected, message, status) VALUES
(1,'Admin','HIGH','Demo fuel level below 15%: Reactor 3','Demo alert: review the simulated fuel record.','Unread'),
(2,'Plant Manager','HIGH','Demo fuel level below 15%: Reactor 3','Demo alert: review the simulated fuel record.','Unread'),
(3,'Engineer','HIGH','Demo maintenance item pending','Demo alert: review the simulated maintenance record.','Unread'),
(4,'Safety Officer','HIGH','Demo equipment health requires review','Demo alert: review the simulated equipment record.','Unread');

-- safety_tasks and safety_task_messages are intentionally left empty.
-- NUCLEUS OS creates these workflow records when findings are generated
-- and Admin assigns tasks / staff submit responses through the application.

-- QUICK VERIFICATION: expected sample row counts on a fresh database.
SELECT 'users' AS table_name, COUNT(*) AS total_records FROM users
UNION ALL SELECT 'nuclear_power_plants', COUNT(*) FROM nuclear_power_plants
UNION ALL SELECT 'reactors', COUNT(*) FROM reactors
UNION ALL SELECT 'power_generation', COUNT(*) FROM power_generation
UNION ALL SELECT 'fuel_management', COUNT(*) FROM fuel_management
UNION ALL SELECT 'fuel_rod_tracking', COUNT(*) FROM fuel_rod_tracking
UNION ALL SELECT 'radiation_monitoring', COUNT(*) FROM radiation_monitoring
UNION ALL SELECT 'radioactive_waste', COUNT(*) FROM radioactive_waste
UNION ALL SELECT 'waste_storage', COUNT(*) FROM waste_storage
UNION ALL SELECT 'safety_records', COUNT(*) FROM safety_records
UNION ALL SELECT 'equipment', COUNT(*) FROM equipment
UNION ALL SELECT 'maintenance', COUNT(*) FROM maintenance
UNION ALL SELECT 'employee_exposure', COUNT(*) FROM employee_exposure
UNION ALL SELECT 'intelligent_recommendations', COUNT(*) FROM intelligent_recommendations
UNION ALL SELECT 'alert_notifications', COUNT(*) FROM alert_notifications;
