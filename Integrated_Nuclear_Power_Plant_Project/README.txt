INTEGRATED NUCLEAR POWER PLANT MANAGEMENT SYSTEM
===================================================

Technology:
- Python 3
- MySQL
- mysql-connector-python
- Tkinter
- Matplotlib

IMPORTANT:
This is a Class XII educational project and a management-system simulation.
It does NOT control real reactors, radiation equipment, emergency systems,
or nuclear plant hardware. Reactor/radiation/emergency values are simulated
database records.

SETUP
-----

1. Install packages in Command Prompt:

   py -m pip install mysql-connector-python matplotlib

2. Open MySQL Workbench or MySQL Command Line Client.

3. Run database.sql.

4. Open database.py settings inside main.py and setup.py.
   Replace:

       "YOUR_MYSQL_PASSWORD"

   with your MySQL root password.

5. Run:

       py setup.py

   This creates the five demo login accounts.

6. Run:

       py main.py

DEMO LOGINS
-----------
admin      / admin123
manager    / manager123
engineer   / engineer123
safety     / safety123
security   / security123

25-MODULE COVERAGE
------------------
1. Login System
2. Nuclear Power Plant Management
3. Reactor Management
4. Power Generation
5. Nuclear Fuel Management
6. Fuel Rod Tracking
7. Radioactive Waste Management
8. Waste Storage Facility
9. Radiation Monitoring
10. Employee Management
11. Employee Radiation Exposure
12. Equipment Management
13. Maintenance Management
14. Safety Inspection
15. Environmental Monitoring
16. Visitor & Security
17. Emergency Response
18. Inventory & Purchase
19. Analytics & Reports
20. Intelligent Decision Support System
21. Human Resources Management
22. Career Portal
23. Payroll Management
24. Employee Awards
25. Leave Management

NOTE ON MODULES 21-25
---------------------
They are represented by connected database tables:
departments, job_vacancies, candidates, job_applications, payroll,
promotions, attendance, performance, training, retirement,
employee_awards and leave_records.

The GUI uses reusable CRUD forms so the same add/edit/delete/search/view
logic can operate across many related tables. This keeps the project
maintainable while still demonstrating functions, loops, conditions,
SQL, MySQL, exception handling and modular organization.

FOR THE PRESENTATION
--------------------
Show:
1. Login screen
2. Dashboard
3. Plant records
4. Reactor records
5. Waste and radiation records (simulated)
6. Employee/HR records
7. Payroll and leave records
8. Matplotlib reports
9. Rule-based Decision Support screen
10. MySQL database tables

DO NOT present the application as real nuclear safety/control software.
