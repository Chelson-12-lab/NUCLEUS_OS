
import mysql.connector
from mysql.connector import Error


# ==========================================================
# NUCLEUS OS
# Nuclear Waste & Radiation Monitoring System
# Python + MySQL Console Application
# ==========================================================

DB_CONFIG = {
    "host": "127.0.0.1",
    "port":3306,
    "user": "root",
    "password": "dani",
    "database": "nucleus_os"
}


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def connect_database():
        try:
            conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            use_pure=True,
            connection_timeout=5
            )


            if conn.is_connected():
               print("Database connection successful!")
               return conn
            else:
               print("Database connection failed!")
               return None

        except Error as e:
            print("\nDatabase connection failed!")
            print("Error:", e)
            return None


# ==========================================================
# DISPLAY TABLE
# ==========================================================

def display_table(conn, table, columns):
    try:
        cursor = conn.cursor()

        query = f"SELECT {', '.join(columns)} FROM {table}"
        cursor.execute(query)

        rows = cursor.fetchall()

        print("\n" + "=" * 90)
        print(table.upper())
        print("=" * 90)

        if not rows:
            print("No records found.")
            cursor.close()
            return

        print(" | ".join(columns))
        print("-" * 90)

        for row in rows:
            print(" | ".join(str(value) for value in row))

        cursor.close()

    except Error as e:
        print("Database Error:", e)


# ==========================================================
# ADD RECORD
# ==========================================================

def add_record(conn, table, columns):
    values = []

    print("\nEnter the following details:")

    for column in columns:
        value = input(
            column.replace("_", " ").title() + ": "
        )

        if value == "":
            print("All fields are compulsory.")
            return

        values.append(value)

    try:
        cursor = conn.cursor()

        placeholders = ",".join(["%s"] * len(values))

        query = (
            f"INSERT INTO {table} "
            f"({','.join(columns)}) "
            f"VALUES ({placeholders})"
        )

        cursor.execute(query, values)
        conn.commit()

        cursor.close()

        print("\nRecord added successfully!")

    except Error as e:
        conn.rollback()
        print("\nDatabase Error:", e)


# ==========================================================
# DELETE RECORD
# ==========================================================

def delete_record(conn, table, primary_key):
    record_id = input(
        f"\nEnter {primary_key.replace('_', ' ')} to delete: "
    )

    try:
        cursor = conn.cursor()

        query = (
            f"DELETE FROM {table} "
            f"WHERE {primary_key}=%s"
        )

        cursor.execute(query, (record_id,))
        conn.commit()

        if cursor.rowcount > 0:
            print("\nRecord deleted successfully!")
        else:
            print("\nRecord not found.")

        cursor.close()

    except Error as e:
        conn.rollback()
        print("\nDatabase Error:", e)


# ==========================================================
# GENERIC MODULE
# ==========================================================

def database_module(
    conn,
    title,
    table,
    columns,
    input_columns,
    primary_key
):

    while True:

        print("\n")
        print("=" * 60)
        print(title.upper())
        print("=" * 60)

        print("1. View Records")
        print("2. Add Record")
        print("3. Delete Record")
        print("4. Back")

        choice = input("\nEnter your choice: ")

        if choice == "1":

            display_table(
                conn,
                table,
                columns
            )

        elif choice == "2":

            add_record(
                conn,
                table,
                input_columns
            )

        elif choice == "3":

            delete_record(
                conn,
                table,
                primary_key
            )

        elif choice == "4":
            break

        else:
            print("\nInvalid choice!")


# ==========================================================
# DASHBOARD
# ==========================================================
# ==========================================================
# ROLE-BASED DASHBOARD
# ==========================================================

def dashboard(conn, username, role):

    while True:

        print("\n")
        print("=" * 75)
        print("                         NUCLEUS OS")
        print("            Nuclear Waste & Radiation Monitoring System")
        print("=" * 75)

        print("\nWelcome,", username)
        print("Role    :", role)

        print("\n" + "-" * 75)
        print("                    YOUR DASHBOARD")
        print("-" * 75)

        # ==================================================
        # ADMIN DASHBOARD
        # ==================================================

        if role == "Admin":

            print("\n1. User Management")
            print("2. Nuclear Power Plant")
            print("3. Reactor Management")
            print("4. Power Generation")
            print("5. Fuel Management")
            print("6. Fuel Rod Tracking")
            print("7. Radiation Alert")
            print("8. Radiation Monitoring")
            print("9. Radioactive Waste")
            print("10. Waste Storage")
            print("11. HR & Employees")
            print("12. Radiation Exposure")
            print("13. Safety Inspection")
            print("14. Maintenance")
            print("15. Career Protocol")
            print("16. Payroll")
            print("17. Logout")

            choice = input("\nEnter your choice: ")

            # USER MANAGEMENT
            if choice == "1":

                database_module(
                    conn,
                    "User Management",
                    "users",
                    [
                        "user_id",
                        "username",
                        "password",
                        "email",
                        "role"
                    ],
                    [
                        "username",
                        "password",
                        "email",
                        "role"
                    ],
                    "user_id"
                )

            # NUCLEAR POWER PLANT
            elif choice == "2":

                database_module(
                    conn,
                    "Nuclear Power Plant",
                    "nuclear_power_plants",
                    [
                        "plant_id",
                        "plant_name",
                        "location"
                    ],
                    [
                        "plant_name",
                        "location"
                    ],
                    "plant_id"
                )

            # REACTORS
            elif choice == "3":

                database_module(
                    conn,
                    "Reactor Management",
                    "reactors",
                    [
                        "reactor_id",
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    [
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    "reactor_id"
                )

            # POWER GENERATION
            elif choice == "4":

                database_module(
                    conn,
                    "Power Generation",
                    "power_generation",
                    [
                        "generation_id",
                        "reactor_id",
                        "generation_date",
                        "electricity_generated"
                    ],
                    [
                        "reactor_id",
                        "generation_date",
                        "electricity_generated"
                    ],
                    "generation_id"
                )

            # FUEL
            elif choice == "5":

                database_module(
                    conn,
                    "Fuel Management",
                    "fuel_management",
                    [
                        "fuel_id",
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    [
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    "fuel_id"
                )

            # FUEL ROD
            elif choice == "6":

                database_module(
                    conn,
                    "Fuel Rod Tracking",
                    "fuel_rod_tracking",
                    [
                        "rod_id",
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    [
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    "rod_id"
                )

            # RADIATION ALERT
            elif choice == "7":

                radiation_alert(conn)

            # RADIATION MONITORING
            elif choice == "8":

                database_module(
                    conn,
                    "Radiation Monitoring",
                    "radiation_monitoring",
                    [
                        "sensor_record_id",
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring",
                        "recorded_at"
                    ],
                    [
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring"
                    ],
                    "sensor_record_id"
                )

            # RADIOACTIVE WASTE
            elif choice == "9":

                database_module(
                    conn,
                    "Radioactive Waste",
                    "radioactive_waste",
                    [
                        "waste_id",
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    [
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    "waste_id"
                )

            # WASTE STORAGE
            elif choice == "10":

                database_module(
                    conn,
                    "Waste Storage",
                    "waste_storage",
                    [
                        "storage_id",
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    [
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    "storage_id"
                )

            # HR
            elif choice == "11":

                database_module(
                    conn,
                    "HR & Employees",
                    "employees",
                    [
                        "employee_id",
                        "employee_name",
                        "department",
                        "salary",
                        "promotion_status",
                        "performance_record"
                    ],
                    [
                        "employee_name",
                        "department",
                        "salary",
                        "promotion_status",
                        "performance_record"
                    ],
                    "employee_id"
                )

            # EXPOSURE
            elif choice == "12":

                database_module(
                    conn,
                    "Radiation Exposure",
                    "employee_exposure",
                    [
                        "exposure_id",
                        "employee_id",
                        "daily_exposure",
                        "monthly_exposure",
                        "safe_limit",
                        "limit_status",
                        "recorded_date"
                    ],
                    [
                        "employee_id",
                        "daily_exposure",
                        "monthly_exposure",
                        "safe_limit",
                        "limit_status",
                        "recorded_date"
                    ],
                    "exposure_id"
                )

            # SAFETY
            elif choice == "13":

                database_module(
                    conn,
                    "Safety Inspection",
                    "safety_records",
                    [
                        "safety_id",
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required",
                        "created_at"
                    ],
                    [
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required"
                    ],
                    "safety_id"
                )

            # MAINTENANCE
            elif choice == "14":

                database_module(
                    conn,
                    "Maintenance",
                    "maintenance",
                    [
                        "maintenance_id",
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    [
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    "maintenance_id"
                )

            # CAREER
            elif choice == "15":

                database_module(
                    conn,
                    "Career Protocol",
                    "career_records",
                    [
                        "career_id",
                        "employee_id",
                        "position_name",
                        "candidate_name",
                        "career_status",
                        "notes"
                    ],
                    [
                        "employee_id",
                        "position_name",
                        "candidate_name",
                        "career_status",
                        "notes"
                    ],
                    "career_id"
                )

            # PAYROLL
            elif choice == "16":

                database_module(
                    conn,
                    "Payroll Management",
                    "payroll",
                    [
                        "payroll_id",
                        "employee_id",
                        "salary",
                        "payment_date",
                        "payment_status"
                    ],
                    [
                        "employee_id",
                        "salary",
                        "payment_date",
                        "payment_status"
                    ],
                    "payroll_id"
                )

            elif choice == "17":

                print("\nLogged out successfully.")
                break

            else:

                print("\nInvalid choice!")


        # ==================================================
        # PLANT MANAGER DASHBOARD
        # ==================================================

        elif role == "Plant Manager":

            print("\n1. Radiation Alert")
            print("2. Radiation Monitoring")
            print("3. Nuclear Power Plant")
            print("4. Reactor Management")
            print("5. Power Generation")
            print("6. Fuel Management")
            print("7. Fuel Rod Tracking")
            print("8. Radioactive Waste")
            print("9. Waste Storage")
            print("10. HR & Employees")
            print("11. Safety Inspection")
            print("12. Maintenance")
            print("13. Radiation Exposure")
            print("14. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":

                radiation_alert(conn)

            elif choice == "2":

                database_module(
                    conn,
                    "Radiation Monitoring",
                    "radiation_monitoring",
                    [
                        "sensor_record_id",
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring",
                        "recorded_at"
                    ],
                    [
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring"
                    ],
                    "sensor_record_id"
                )

            elif choice == "3":

                database_module(
                    conn,
                    "Nuclear Power Plant",
                    "nuclear_power_plants",
                    [
                        "plant_id",
                        "plant_name",
                        "location"
                    ],
                    [
                        "plant_name",
                        "location"
                    ],
                    "plant_id"
                )

            elif choice == "4":

                database_module(
                    conn,
                    "Reactor Management",
                    "reactors",
                    [
                        "reactor_id",
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    [
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    "reactor_id"
                )

            elif choice == "5":

                database_module(
                    conn,
                    "Power Generation",
                    "power_generation",
                    [
                        "generation_id",
                        "reactor_id",
                        "generation_date",
                        "electricity_generated"
                    ],
                    [
                        "reactor_id",
                        "generation_date",
                        "electricity_generated"
                    ],
                    "generation_id"
                )

            elif choice == "6":

                database_module(
                    conn,
                    "Fuel Management",
                    "fuel_management",
                    [
                        "fuel_id",
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    [
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    "fuel_id"
                )

            elif choice == "7":

                database_module(
                    conn,
                    "Fuel Rod Tracking",
                    "fuel_rod_tracking",
                    [
                        "rod_id",
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    [
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    "rod_id"
                )

            elif choice == "8":

                database_module(
                    conn,
                    "Radioactive Waste",
                    "radioactive_waste",
                    [
                        "waste_id",
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    [
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    "waste_id"
                )

            elif choice == "9":

                database_module(
                    conn,
                    "Waste Storage",
                    "waste_storage",
                    [
                        "storage_id",
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    [
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    "storage_id"
                )

            elif choice == "10":

                database_module(
                    conn,
                    "HR & Employees",
                    "employees",
                    [
                        "employee_id",
                        "employee_name",
                        "department",
                        "salary",
                        "promotion_status",
                        "performance_record"
                    ],
                    [
                        "employee_name",
                        "department",
                        "salary",
                        "promotion_status",
                        "performance_record"
                    ],
                    "employee_id"
                )

            elif choice == "11":

                database_module(
                    conn,
                    "Safety Inspection",
                    "safety_records",
                    [
                        "safety_id",
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required",
                        "created_at"
                    ],
                    [
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required"
                    ],
                    "safety_id"
                )

            elif choice == "12":

                database_module(
                    conn,
                    "Maintenance",
                    "maintenance",
                    [
                        "maintenance_id",
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    [
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    "maintenance_id"
                )

            elif choice == "13":

                database_module(
                    conn,
                    "Radiation Exposure",
                    "employee_exposure",
                    [
                        "exposure_id",
                        "employee_id",
                        "daily_exposure",
                        "monthly_exposure",
                        "safe_limit",
                        "limit_status",
                        "recorded_date"
                    ],
                    [
                        "employee_id",
                        "daily_exposure",
                        "monthly_exposure",
                        "safe_limit",
                        "limit_status",
                        "recorded_date"
                    ],
                    "exposure_id"
                )

            elif choice == "14":

                print("\nLogged out successfully.")
                break

            else:

                print("\nInvalid choice!")


        # ==================================================
        # ENGINEER DASHBOARD
        # ==================================================

        elif role == "Engineer":

            print("\n1. Radiation Alert")
            print("2. Radiation Monitoring")
            print("3. Reactor Management")
            print("4. Fuel Management")
            print("5. Fuel Rod Tracking Management")
            print("6. Equipment")
            print("7. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":

                radiation_alert(conn)

            elif choice == "2":

                database_module(
                    conn,
                    "Radiation Monitoring",
                    "radiation_monitoring",
                    [
                        "sensor_record_id",
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring",
                        "recorded_at"
                    ],
                    [
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring"
                    ],
                    "sensor_record_id"
                )

            elif choice == "3":

                database_module(
                    conn,
                    "Reactor Management",
                    "reactors",
                    [
                        "reactor_id",
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    [
                        "plant_id",
                        "reactor_type",
                        "capacity",
                        "operating_status"
                    ],
                    "reactor_id"
                )

            elif choice == "4":

                database_module(
                    conn,
                    "Fuel Management",
                    "fuel_management",
                    [
                        "fuel_id",
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    [
                        "reactor_id",
                        "fuel_type",
                        "quantity",
                        "usage_status"
                    ],
                    "fuel_id"
                )

            elif choice == "5":

                database_module(
                    conn,
                    "Fuel Rod Tracking Management",
                    "fuel_rod_tracking",
                    [
                        "rod_id",
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    [
                        "reactor_id",
                        "installation_date",
                        "remaining_life"
                    ],
                    "rod_id"
                )

            elif choice == "6":

                database_module(
                    conn,
                    "Equipment Management",
                    "equipment",
                    [
                        "equipment_id",
                        "equipment_name",
                        "equipment_type",
                        "equipment_status"
                    ],
                    [
                        "equipment_name",
                        "equipment_type",
                        "equipment_status"
                    ],
                    "equipment_id"
                )

            elif choice == "7":

                print("\nLogged out successfully.")
                break

            else:

                print("\nInvalid choice!")


        # ==================================================
        # SAFETY OFFICER DASHBOARD
        # ==================================================

        elif role == "Safety Officer":

            print("\n1. Radiation Alert")
            print("2. Radiation Monitoring")
            print("3. Radioactive Waste")
            print("4. Waste Storage")
            print("5. Safety Inspection")
            print("6. Maintenance")
            print("7. Logout")

            choice = input("\nEnter your choice: ")

            if choice == "1":

                radiation_alert(conn)

            elif choice == "2":

                database_module(
                    conn,
                    "Radiation Monitoring",
                    "radiation_monitoring",
                    [
                        "sensor_record_id",
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring",
                        "recorded_at"
                    ],
                    [
                        "sensor_name",
                        "radiation_reading",
                        "alert_generation",
                        "area_monitoring"
                    ],
                    "sensor_record_id"
                )

            elif choice == "3":

                database_module(
                    conn,
                    "Radioactive Waste",
                    "radioactive_waste",
                    [
                        "waste_id",
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    [
                        "waste_category",
                        "radiation_level",
                        "storage_assignment"
                    ],
                    "waste_id"
                )

            elif choice == "4":

                database_module(
                    conn,
                    "Waste Storage",
                    "waste_storage",
                    [
                        "storage_id",
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    [
                        "storage_building",
                        "capacity",
                        "available_space",
                        "inspection_records"
                    ],
                    "storage_id"
                )

            elif choice == "5":

                database_module(
                    conn,
                    "Safety Inspection",
                    "safety_records",
                    [
                        "safety_id",
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required",
                        "created_at"
                    ],
                    [
                        "safety_title",
                        "safety_description",
                        "risk_level",
                        "action_required"
                    ],
                    "safety_id"
                )

            elif choice == "6":

                database_module(
                    conn,
                    "Maintenance",
                    "maintenance",
                    [
                        "maintenance_id",
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    [
                        "equipment_name",
                        "maintenance_date",
                        "maintenance_status"
                    ],
                    "maintenance_id"
                )

            elif choice == "7":

                print("\nLogged out successfully.")
                break

            else:

                print("\nInvalid choice!")

        else:

            print("\nUnknown role.")
            break


# ==========================================================
# COUNT RECORDS
# ==========================================================

def count_records(conn, table):

    try:

        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM {table}"
        )

        result = cursor.fetchone()[0]

        cursor.close()

        return result

    except Error:
        return 0


# ==========================================================
# LOGIN
# ==========================================================

# ==========================================================
# SIGN UP
# ==========================================================

def signup(conn):

    print("\n")
    print("=" * 60)
    print("                    SIGN UP")
    print("=" * 60)

    username = input("\nCreate Username : ")
    password = input("Create Password : ")
    email = input("Email           : ")

    print("\nSelect your role:")
    print("1. Admin")
    print("2. Plant Manager")
    print("3. Engineer")
    print("4. Safety Officer")

    role_choice = input("\nEnter role choice: ")

    roles = {
        "1": "Admin",
        "2": "Plant Manager",
        "3": "Engineer",
        "4": "Safety Officer"
    }

    if role_choice not in roles:
        print("\nInvalid role!")
        return

    role = roles[role_choice]

    if username == "" or password == "" or email == "":
        print("\nAll fields are compulsory.")
        return

    try:

        cursor = conn.cursor()

        cursor.execute(
            "SELECT user_id FROM users WHERE username=%s",
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            print("\nUsername already exists!")
            cursor.close()
            return

        query = """
            INSERT INTO users
            (username, password, email, role)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (username, password, email, role)
        )

        conn.commit()
        cursor.close()

        print("\nAccount created successfully!")
        print("Username :", username)
        print("Role     :", role)
        print("\nYou can now login.")

    except Error as e:

        conn.rollback()
        print("\nDatabase Error:", e)


# ==========================================================
# LOGIN / START MENU
# ==========================================================

def login(conn):

    while True:

        print("\n")
        print("=" * 65)
        print("                         NUCLEUS OS")
        print("=" * 65)

        print("\nNuclear Waste & Radiation Monitoring System")

        print("\n------------------- START MENU -------------------")
        print("1. Sign Up")
        print("2. Login")
        print("3. Exit")

        choice = input("\nEnter your choice: ")

        # ==================================================
        # SIGN UP
        # ==================================================

        if choice == "1":

            signup(conn)

        # ==================================================
        # LOGIN
        # ==================================================

        elif choice == "2":

            print("\n")
            print("=" * 60)
            print("                       LOGIN")
            print("=" * 60)

            print("\nSelect your role:")
            print("1. Admin")
            print("2. Plant Manager")
            print("3. Engineer")
            print("4. Safety Officer")

            role_choice = input("\nEnter your role: ")

            roles = {
                "1": "Admin",
                "2": "Plant Manager",
                "3": "Engineer",
                "4": "Safety Officer"
            }

            if role_choice not in roles:
                print("\nInvalid role!")
                continue

            selected_role = roles[role_choice]

            username = input("\nUsername : ")
            password = input("Password : ")

            if username == "" or password == "":
                print("\nUsername and password are compulsory.")
                continue

            try:

                cursor = conn.cursor()

                query = """
                    SELECT user_id, username, email, role
                    FROM users
                    WHERE username=%s
                    AND password=%s
                    AND role=%s
                """

                cursor.execute(
                    query,
                    (username, password, selected_role)
                )

                user = cursor.fetchone()

                cursor.close()

                if user:

                    print("\nLogin successful!")
                    print("Welcome :", user[1])
                    print("Role    :", user[3])

                    dashboard(
                        conn,
                        user[1],
                        user[3]
                    )

                else:

                    print("\nInvalid username, password or role.")

            except Error as e:

                print("\nDatabase Error:", e)

        # ==================================================
        # EXIT
        # ==================================================

        elif choice == "3":

            print("\nThank you for using NUCLEUS OS.")
            break

        else:

            print("\nInvalid choice!")
# ==========================================================
# MAIN PROGRAM
# ==========================================================

def main():

    print("=" * 60)
    print("             NUCLEUS OS STARTING...")
    print("=" * 60)

    conn = connect_database()

    if conn is None:
        return

    login(conn)

    conn.close()

    print("\nNucleus OS closed.")
    print("Thank you.")


# ==========================================================
# RUN PROGRAM
# ==========================================================

if __name__ == "__main__":
    main()

