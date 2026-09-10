-- ============================================================
-- INTEGRATED NUCLEAR POWER PLANT MANAGEMENT SYSTEM
-- MySQL Database
-- Educational / simulated project
-- ============================================================

CREATE DATABASE IF NOT EXISTS nuclear_project;
USE nuclear_project;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS plants (
    plant_id INT PRIMARY KEY AUTO_INCREMENT,
    plant_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    manager VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS reactors (
    reactor_id INT PRIMARY KEY AUTO_INCREMENT,
    plant_id INT,
    reactor_type VARCHAR(80),
    capacity DECIMAL(12,2),
    operating_status VARCHAR(80),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
);

CREATE TABLE IF NOT EXISTS power_generation (
    generation_id INT PRIMARY KEY AUTO_INCREMENT,
    reactor_id INT,
    generation_date DATE,
    electricity_generated DECIMAL(14,2),
    efficiency DECIMAL(6,2),
    FOREIGN KEY (reactor_id) REFERENCES reactors(reactor_id)
);

CREATE TABLE IF NOT EXISTS fuel (
    fuel_id INT PRIMARY KEY AUTO_INCREMENT,
    reactor_id INT,
    fuel_type VARCHAR(80),
    stock_percentage DECIMAL(6,2),
    usage_date DATE,
    replacement_date DATE,
    FOREIGN KEY (reactor_id) REFERENCES reactors(reactor_id)
);

CREATE TABLE IF NOT EXISTS fuel_rods (
    rod_id INT PRIMARY KEY AUTO_INCREMENT,
    reactor_id INT,
    installation_date DATE,
    remaining_life_months INT,
    status VARCHAR(50),
    FOREIGN KEY (reactor_id) REFERENCES reactors(reactor_id)
);

CREATE TABLE IF NOT EXISTS waste_storage (
    storage_id INT PRIMARY KEY AUTO_INCREMENT,
    building_name VARCHAR(100),
    capacity DECIMAL(12,2),
    used_capacity DECIMAL(12,2),
    last_inspection DATE,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS radioactive_waste (
    waste_id INT PRIMARY KEY AUTO_INCREMENT,
    waste_category VARCHAR(80),
    radiation_level DECIMAL(10,2),
    storage_id INT,
    registration_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (storage_id) REFERENCES waste_storage(storage_id)
);

CREATE TABLE IF NOT EXISTS radiation_monitoring (
    reading_id INT PRIMARY KEY AUTO_INCREMENT,
    sensor_id VARCHAR(50),
    area_name VARCHAR(100),
    reading_date DATETIME,
    radiation_reading DECIMAL(10,3),
    alert_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    designation VARCHAR(100),
    date_of_joining DATE,
    contact VARCHAR(30),
    shift VARCHAR(30),
    qualification VARCHAR(150),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS employee_exposure (
    exposure_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    exposure_date DATE,
    daily_exposure DECIMAL(10,3),
    monthly_exposure DECIMAL(10,3),
    safe_limit_status VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INT PRIMARY KEY AUTO_INCREMENT,
    equipment_name VARCHAR(100),
    equipment_type VARCHAR(80),
    status VARCHAR(60),
    health_score DECIMAL(6,2),
    spare_parts VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS maintenance (
    maintenance_id INT PRIMARY KEY AUTO_INCREMENT,
    equipment_id INT,
    engineer_id INT,
    scheduled_date DATE,
    cost DECIMAL(12,2),
    completion_status VARCHAR(50),
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id),
    FOREIGN KEY (engineer_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS safety_inspections (
    inspection_id INT PRIMARY KEY AUTO_INCREMENT,
    inspection_date DATE,
    area_name VARCHAR(100),
    compliance_status VARCHAR(50),
    safety_score DECIMAL(6,2),
    recommendations VARCHAR(500)
);

CREATE TABLE IF NOT EXISTS environment_monitoring (
    environment_id INT PRIMARY KEY AUTO_INCREMENT,
    reading_date DATE,
    water_quality VARCHAR(100),
    air_quality VARCHAR(100),
    soil_monitoring VARCHAR(100),
    outside_radiation DECIMAL(10,3)
);

CREATE TABLE IF NOT EXISTS security_visitors (
    visitor_id INT PRIMARY KEY AUTO_INCREMENT,
    visitor_name VARCHAR(100),
    visit_date DATE,
    entry_time TIME,
    exit_time TIME,
    security_clearance VARCHAR(50),
    restricted_access VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS emergency_incidents (
    incident_id INT PRIMARY KEY AUTO_INCREMENT,
    incident_date DATETIME,
    incident_type VARCHAR(100),
    emergency_level VARCHAR(50),
    evacuation_status VARCHAR(50),
    rescue_team VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS inventory (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100),
    category VARCHAR(80),
    quantity INT,
    reorder_level INT,
    supplier VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS job_vacancies (
    job_id INT PRIMARY KEY AUTO_INCREMENT,
    job_title VARCHAR(100),
    department_id INT,
    qualification VARCHAR(200),
    experience_years DECIMAL(5,2),
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    vacancies INT,
    closing_date DATE,
    status VARCHAR(40),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    qualification VARCHAR(200),
    experience_years DECIMAL(5,2),
    contact VARCHAR(30),
    email VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS job_applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    candidate_id INT,
    job_id INT,
    application_date DATE,
    application_status VARCHAR(50),
    interview_date DATE,
    final_selection VARCHAR(30),
    FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY (job_id) REFERENCES job_vacancies(job_id)
);

CREATE TABLE IF NOT EXISTS payroll (
    payroll_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    pay_month VARCHAR(20),
    basic_salary DECIMAL(12,2),
    allowances DECIMAL(12,2),
    risk_allowance DECIMAL(12,2),
    overtime DECIMAL(12,2),
    bonus DECIMAL(12,2),
    income_tax DECIMAL(12,2),
    provident_fund DECIMAL(12,2),
    medical_insurance DECIMAL(12,2),
    deductions DECIMAL(12,2),
    net_salary DECIMAL(12,2),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS promotions (
    promotion_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    promotion_date DATE,
    years_of_service DECIMAL(5,2),
    performance_rating DECIMAL(5,2),
    training_completed VARCHAR(100),
    old_designation VARCHAR(100),
    new_designation VARCHAR(100),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    attendance_date DATE,
    status VARCHAR(30),
    shift VARCHAR(30),
    night_shift VARCHAR(30),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS performance (
    performance_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    evaluation_month VARCHAR(20),
    rating DECIMAL(5,2),
    supervisor_comments VARCHAR(500),
    awards VARCHAR(200),
    improvement_areas VARCHAR(300),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS training (
    training_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    training_type VARCHAR(100),
    training_date DATE,
    certificate_no VARCHAR(100),
    status VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS retirement (
    retirement_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    retirement_date DATE,
    pension_details VARCHAR(300),
    service_years DECIMAL(5,2),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS employee_awards (
    award_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    award_name VARCHAR(120),
    award_date DATE,
    certificate_no VARCHAR(100),
    reward VARCHAR(200),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS leave_records (
    leave_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    leave_type VARCHAR(50),
    start_date DATE,
    end_date DATE,
    reason VARCHAR(300),
    approval_status VARCHAR(50),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- ============================================================
-- DEFAULT USERS
-- Passwords for all demo accounts are shown below.
-- They are hashed by the Python application using SHA-256.
-- admin123, manager123, engineer123, safety123, security123
-- ============================================================

-- Demo users are created by setup.py so their password hashes are correct.

INSERT IGNORE INTO departments (department_name, manager) VALUES
('Reactor Operations', 'Plant Manager'),
('Safety Department', 'Safety Officer'),
('Radiation Monitoring', 'Radiation Officer'),
('Security', 'Security Officer'),
('Human Resources', 'HR Manager'),
('Maintenance', 'Maintenance Manager'),
('Environmental Monitoring', 'Environment Officer'),
('Finance', 'Finance Manager'),
('Research & Development', 'R&D Manager');
