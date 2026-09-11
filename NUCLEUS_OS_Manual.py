
import mysql.connector
from mysql.connector import Error
from tabulate import tabulate


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

        print(tabulate(
            rows,
            headers=columns,
            tablefmt="grid",
            stralign="left"
        ))

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
# RADIATION MONITORING MODULE
# ==========================================================

# These are PROJECT-SIMULATION thresholds used only for NUCLEUS OS.
# They are not real nuclear safety limits.
RAD_NORMAL_LIMIT = 1.0
RAD_WARNING_LIMIT = 2.0
RAD_CRITICAL_ALERT_LIMIT = 2.5


def radiation_status(reading):
    """Return a simple project-simulation status for a radiation reading."""
    if reading >= RAD_WARNING_LIMIT:
        return "High"
    elif reading >= RAD_NORMAL_LIMIT:
        return "Warning"
    return "Normal"


def radiation_alert_value(reading):
    """Return the alert label shown in the Radiation Monitoring table."""
    if reading >= RAD_CRITICAL_ALERT_LIMIT:
        return "Critical"
    elif reading >= RAD_NORMAL_LIMIT:
        return "Yes"
    return "No"


def radiation_monitoring_module(conn):
    """Dedicated Radiation Monitoring module with a cleaner sensor table."""
    while True:
        print("\n")
        print("=" * 72)
        print("                    RADIATION MONITORING")
        print("=" * 72)
        print("1. View Records")
        print("2. Add Record")
        print("3. Delete Record")
        print("4. Back")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT sensor_name, area_monitoring, radiation_reading,
                           alert_generation, recorded_at
                    FROM radiation_monitoring
                    ORDER BY sensor_record_id ASC
                """)
                rows = cursor.fetchall()
                cursor.close()

                table_rows = []
                for row in rows:
                    try:
                        reading = float(row[2])
                    except (TypeError, ValueError):
                        reading = 0.0
                    table_rows.append([
                        row[0],
                        row[1],
                        f"{reading:.2f}",
                        radiation_status(reading),
                        row[3]
                    ])

                if table_rows:
                    print("\n" + tabulate(
                        table_rows,
                        headers=[
                            "Sensor ID",
                            "Location",
                            "Radiation Reading (µSv/h)",
                            "Status",
                            "Alert"
                        ],
                        tablefmt="grid",
                        stralign="left"
                    ))
                else:
                    print("\nNo radiation monitoring records found.")

            except Error as e:
                print("\nDatabase Error:", e)

        elif choice == "2":
            print("\nEnter the following details:")
            sensor_id = input("Sensor ID: ").strip()
            location = input("Location: ").strip()
            reading_text = input("Radiation Reading (µSv/h): ").strip()

            if not sensor_id or not location or not reading_text:
                print("All fields are compulsory.")
                continue

            try:
                reading = float(reading_text)
                if reading < 0:
                    print("Radiation reading cannot be negative.")
                    continue

                status = radiation_status(reading)
                alert = radiation_alert_value(reading)

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO radiation_monitoring
                    (sensor_name, radiation_reading, alert_generation, area_monitoring)
                    VALUES (%s, %s, %s, %s)
                """, (sensor_id, reading, alert, location))
                conn.commit()
                cursor.close()

                print("\nRecord added successfully!")
                print("Status:", status)
                print("Alert:", alert)

                if alert != "No":
                    severity = "CRITICAL" if alert == "Critical" else status.upper()
                    condition = f"Radiation reading {reading:.2f} µSv/h detected at {location}"
                    recommendation = (
                        "Project simulation: review the affected area and follow the "
                        "plant safety workflow."
                    )
                    create_role_notifications(
                        conn, severity, condition, recommendation
                    )
                    print("\n🔔 Notification created for:")
                    print("   Admin | Plant Manager | Engineer | Safety Officer")

            except ValueError:
                print("Please enter a valid numeric radiation reading.")
            except Error as e:
                conn.rollback()
                print("\nDatabase Error:", e)

        elif choice == "3":
            delete_record(conn, "radiation_monitoring", "sensor_record_id")

        elif choice == "4":
            break

        else:
            print("\nInvalid choice!")


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

    if table == "radiation_monitoring":
        radiation_monitoring_module(conn)
        return

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
# INTELLIGENT SAFETY & RECOMMENDATION ENGINE
# ==========================================================

# These limits are for the SIMULATED NUCLEUS OS project only.
RADIATION_HIGH_LIMIT = 100.0
RADIATION_CRITICAL_LIMIT = 200.0
FUEL_LOW_LIMIT = 15.0
STORAGE_HIGH_LIMIT = 90.0
REACTOR_TEMP_HIGH_LIMIT = 300.0


def ensure_recommendation_table(conn):
    """Create the recommendation history table if it does not exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligent_recommendations (
                recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                generated_by VARCHAR(100),
                role VARCHAR(50),
                severity VARCHAR(30),
                condition_detected VARCHAR(255),
                recommendation VARCHAR(500),
                priority INT,
                status VARCHAR(30) DEFAULT 'Pending'
            )
        """)
        conn.commit()
        cursor.close()
    except Error as e:
        conn.rollback()
        print("Database Error while creating recommendation table:", e)


# ==========================================================
# NOTIFICATION CENTRE
# ==========================================================

NOTIFICATION_ROLES = [
    "Admin",
    "Plant Manager",
    "Engineer",
    "Safety Officer"
]


def ensure_notification_table(conn):
    """Create the role-based notification table automatically."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alert_notifications (
                notification_id INT AUTO_INCREMENT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recipient_role VARCHAR(50) NOT NULL,
                severity VARCHAR(30),
                condition_detected VARCHAR(255),
                message VARCHAR(500),
                status VARCHAR(20) DEFAULT 'Unread'
            )
        """)
        conn.commit()
        cursor.close()
    except Error as e:
        conn.rollback()
        print("Database Error while creating notification table:", e)


def unread_notification_count(conn, role):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM alert_notifications
            WHERE recipient_role=%s AND status='Unread'
        """, (role,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    except Error:
        return 0


def notification_summary(conn):
    """Show a compact notification centre above the start menu."""
    ensure_notification_table(conn)
    rows = []
    for role in NOTIFICATION_ROLES:
        count = unread_notification_count(conn, role)
        if count:
            status = f"{count} new - Please login to see it"
        else:
            status = "No new notifications"
        rows.append([role, status])

    print("\n🔔 NOTIFICATION CENTRE")
    print(tabulate(rows, headers=["Role", "Status"],
                   tablefmt="simple", stralign="left"))


def create_role_notifications(conn, severity, condition, recommendation):
    """Create an unread notification for all four roles without duplicates."""
    ensure_notification_table(conn)
    message = f"{condition}. {recommendation}"
    try:
        cursor = conn.cursor()
        for recipient_role in NOTIFICATION_ROLES:
            cursor.execute("""
                SELECT notification_id FROM alert_notifications
                WHERE recipient_role=%s AND condition_detected=%s
                  AND status='Unread'
                LIMIT 1
            """, (recipient_role, condition))
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO alert_notifications
                    (recipient_role, severity, condition_detected, message, status)
                    VALUES (%s, %s, %s, %s, 'Unread')
                """, (recipient_role, severity, condition, message))
        conn.commit()
        cursor.close()
    except Error as e:
        conn.rollback()
        print("Could not create role notifications:", e)


def notification_center(conn, role):
    """Display notifications belonging to the logged-in role."""
    ensure_notification_table(conn)
    while True:
        print("\n" + "=" * 95)
        print(f"                 🔔 {role.upper()} NOTIFICATION CENTRE")
        print("=" * 95)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notification_id, created_at, severity,
                       condition_detected, message, status
                FROM alert_notifications
                WHERE recipient_role=%s
                ORDER BY notification_id DESC
            """, (role,))
            rows = cursor.fetchall()
            cursor.close()
            if rows:
                print(tabulate(
                    rows,
                    headers=["ID", "Created", "Severity", "Condition", "Message", "Status"],
                    tablefmt="grid", stralign="left"
                ))
            else:
                print("No notifications for this role.")
        except Error as e:
            print("Notification Error:", e)

        print("\n1. Mark all notifications as read")
        print("2. Back to Dashboard")
        choice = input("\nEnter your choice: ")
        if choice == "1":
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE alert_notifications SET status='Read'
                    WHERE recipient_role=%s AND status='Unread'
                """, (role,))
                conn.commit()
                print(f"\n{cursor.rowcount} notification(s) marked as read.")
                cursor.close()
            except Error as e:
                conn.rollback()
                print("Database Error:", e)
        elif choice == "2":
            break
        else:
            print("\nInvalid choice!")


def dashboard_notification_header(conn, role):
    count = unread_notification_count(conn, role)
    if count:
        text = f"🔔 {role.upper()} NOTIFICATIONS: {count} NEW"
    else:
        text = f"🔔 {role.upper()} NOTIFICATIONS: 0"
    print(text.rjust(75))


def save_recommendation(conn, username, role, severity, condition, recommendation, priority):
    """Save an intelligent recommendation for future review."""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO intelligent_recommendations
            (generated_by, role, severity, condition_detected, recommendation, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, role, severity, condition, recommendation, priority))
        conn.commit()
        cursor.close()
    except Error as e:
        conn.rollback()
        print("Could not save recommendation:", e)


def get_float_input(prompt, default=None):
    """Read a numeric simulated value without crashing on bad input."""
    while True:
        value = input(prompt).strip()
        if value == "" and default is not None:
            return default
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def intelligent_recommendation_engine(conn, username, role):
    """
    Rule-based decision-support engine.
    It analyses simulated/database conditions and produces
    recommendations. It is NOT real AI or machine learning.
    """

    ensure_recommendation_table(conn)

    print("\n" + "=" * 85)
    print("             NUCLEUS OS INTELLIGENT SAFETY ENGINE")
    print("=" * 85)
    print("Rule-based analysis of simulated plant conditions")

    findings = []

    # ------------------------------------------------------
    # 1. RADIATION ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT radiation_reading, sensor_name, area_monitoring, recorded_at
            FROM radiation_monitoring
            ORDER BY recorded_at DESC
            LIMIT 1
        """)
        latest = cursor.fetchone()

        cursor.execute("""
            SELECT radiation_reading
            FROM radiation_monitoring
            ORDER BY recorded_at DESC
            LIMIT 5
        """)
        radiation_history = [float(row[0]) for row in cursor.fetchall() if row[0] is not None]
        cursor.close()

        if latest and latest[0] is not None:
            radiation = float(latest[0])
            print(f"\nRadiation reading : {radiation:.2f}")
            print(f"Sensor            : {latest[1]}")
            print(f"Area              : {latest[2]}")

            if radiation >= RADIATION_CRITICAL_LIMIT:
                findings.append(("CRITICAL", "Very high radiation detected",
                                 "Immediate evacuation required and radiation source should be investigated.", 1))
            elif radiation >= RADIATION_HIGH_LIMIT:
                findings.append(("HIGH", "High radiation detected",
                                 "Restrict access and inspect the affected radiation zone immediately.", 2))

            # Trend detection: records are newest first.
            if len(radiation_history) >= 3:
                newest_three = radiation_history[:3]
                if newest_three[0] > newest_three[1] > newest_three[2]:
                    findings.append(("WARNING", "Radiation trend is continuously increasing",
                                     "Inspect the monitored area and continue close radiation monitoring.", 3))
        else:
            print("\nRadiation reading : No monitoring record available")
    except Error as e:
        print("Radiation analysis error:", e)

    # ------------------------------------------------------
    # 2. WASTE STORAGE ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT storage_building, capacity, available_space
            FROM waste_storage
        """)
        storage_rows = cursor.fetchall()
        cursor.close()

        for building, capacity, available in storage_rows:
            if capacity and float(capacity) > 0 and available is not None:
                occupancy = ((float(capacity) - float(available)) / float(capacity)) * 100
                if occupancy >= STORAGE_HIGH_LIMIT:
                    findings.append(("HIGH", f"Storage {building} is {occupancy:.1f}% full",
                                     "Transfer waste to long-term storage.", 2))
    except Error as e:
        print("Storage analysis error:", e)

    # ------------------------------------------------------
    # 3. FUEL ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT reactor_id, quantity, usage_status
            FROM fuel_management
            ORDER BY fuel_id DESC
        """)
        fuel_rows = cursor.fetchall()
        cursor.close()

        for reactor_id, quantity, usage_status in fuel_rows:
            if quantity is not None and float(quantity) <= FUEL_LOW_LIMIT:
                findings.append(("HIGH", f"Fuel level for reactor {reactor_id} is {float(quantity):.1f}%",
                                 "Schedule refueling.", 2))
            elif usage_status and str(usage_status).lower() in ("low", "critical", "refuel"):
                findings.append(("WARNING", f"Fuel status for reactor {reactor_id} is {usage_status}",
                                 "Review fuel inventory and plan refueling if required.", 3))
    except Error as e:
        print("Fuel analysis error:", e)

    # ------------------------------------------------------
    # 4. MAINTENANCE ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT equipment_name, maintenance_date, maintenance_status
            FROM maintenance
        """)
        maintenance_rows = cursor.fetchall()
        cursor.close()

        from datetime import date
        today = date.today()
        completed_statuses = {"completed", "complete", "done", "closed", "resolved"}

        for equipment_name, maintenance_date, status in maintenance_rows:
            if maintenance_date and maintenance_date < today and str(status).lower() not in completed_statuses:
                findings.append(("HIGH", f"Maintenance overdue for {equipment_name}",
                                 "Generate maintenance work order.", 2))
    except Error as e:
        print("Maintenance analysis error:", e)

    # ------------------------------------------------------
    # 5. EMPLOYEE EXPOSURE ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT employee_id, monthly_exposure, safe_limit
            FROM employee_exposure
        """)
        exposure_rows = cursor.fetchall()
        cursor.close()

        for employee_id, monthly, safe_limit in exposure_rows:
            if monthly is not None and safe_limit is not None and float(monthly) > float(safe_limit):
                findings.append(("CRITICAL", f"Employee {employee_id} has exceeded the exposure limit",
                                 "Remove employee from the radiation zone and initiate a safety review.", 1))
    except Error as e:
        print("Exposure analysis error:", e)

    # ------------------------------------------------------
    # 6. EQUIPMENT HEALTH ANALYSIS
    # ------------------------------------------------------
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT equipment_name, equipment_status
            FROM equipment
        """)
        equipment_rows = cursor.fetchall()
        cursor.close()

        poor_statuses = {"poor", "critical", "failed", "failure", "damaged", "replace", "unsafe"}
        for equipment_name, status in equipment_rows:
            if status and str(status).strip().lower() in poor_statuses:
                findings.append(("HIGH", f"Equipment health is poor: {equipment_name}",
                                 "Replace equipment after appropriate inspection and authorization.", 2))
    except Error as e:
        print("Equipment analysis error:", e)

    # ------------------------------------------------------
    # 7. SIMULATED REACTOR TEMPERATURE
    # ------------------------------------------------------
    print("\nSIMULATED REACTOR TEMPERATURE")
    temperature = get_float_input("Enter reactor temperature (simulated, °C): ")

    if temperature >= REACTOR_TEMP_HIGH_LIMIT:
        findings.append(("CRITICAL", f"Simulated reactor temperature is {temperature:.1f} °C",
                         "Initiate controlled shutdown and investigate the cause.", 1))
    elif temperature >= REACTOR_TEMP_HIGH_LIMIT * 0.90:
        findings.append(("WARNING", f"Simulated reactor temperature is approaching the high limit ({temperature:.1f} °C)",
                         "Increase monitoring and inspect reactor operating conditions.", 3))

    # ------------------------------------------------------
    # 8. OVERALL RISK SCORE
    # ------------------------------------------------------
    severity_points = {"CRITICAL": 5, "HIGH": 3, "WARNING": 2, "NORMAL": 0}
    risk_score = sum(severity_points.get(item[0], 0) for item in findings)

    if risk_score >= 10:
        overall_risk = "CRITICAL"
    elif risk_score >= 6:
        overall_risk = "HIGH"
    elif risk_score >= 2:
        overall_risk = "WARNING"
    else:
        overall_risk = "NORMAL"

    print("\n" + "-" * 85)
    print("INTELLIGENT ANALYSIS RESULT")
    print("-" * 85)
    print(f"Overall Risk Level : {overall_risk}")
    print(f"Risk Score         : {risk_score}")

    if not findings:
        print("✓ No abnormal conditions detected.")
        print("Recommendation    : Continue routine monitoring.")
        return

    # Highest priority first, then severity.
    severity_order = {"CRITICAL": 1, "HIGH": 2, "WARNING": 3}
    findings.sort(key=lambda x: (x[3], severity_order.get(x[0], 9)))

    table_rows = []
    for number, (severity, condition, recommendation, priority) in enumerate(findings, 1):
        table_rows.append([number, severity, condition, recommendation, priority])
        save_recommendation(conn, username, role, severity, condition, recommendation, priority)
        create_role_notifications(conn, severity, condition, recommendation)

    print(tabulate(
        table_rows,
        headers=["#", "Severity", "Condition Detected", "Recommended Action", "Priority"],
        tablefmt="grid",
        stralign="left"
    ))

    print("\nResponsible role :", role)
    print("Recommendation history has been saved to MySQL.")
    print("Note: This is a simulated rule-based decision-support system, not real AI.")


def recommendation_history(conn):
    """Display saved intelligent recommendations."""
    ensure_recommendation_table(conn)
    display_table(
        conn,
        "intelligent_recommendations",
        [
            "recommendation_id",
            "generated_at",
            "generated_by",
            "role",
            "severity",
            "condition_detected",
            "recommendation",
            "priority",
            "status"
        ]
    )

# ==========================================================
# DASHBOARD
# ==========================================================
# ==========================================================
# ROLE-BASED DASHBOARD
# ==========================================================

# ==========================================================
# RADIATION ALERT
# ==========================================================

def radiation_alert(conn):
    """Display the latest simulated radiation reading and generate a role notification."""
    print("\n" + "=" * 70)
    print("                    RADIATION ALERT")
    print("=" * 70)

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sensor_record_id, sensor_name, radiation_reading,
                   alert_generation, area_monitoring, recorded_at
            FROM radiation_monitoring
            ORDER BY recorded_at DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        cursor.close()

        if not rows:
            print("No radiation monitoring records found.")
            print("Add a reading through Radiation Monitoring first.")
            return

        print(tabulate(
            rows,
            headers=["ID", "Sensor", "Radiation", "Alert", "Area", "Recorded At"],
            tablefmt="grid",
            stralign="left"
        ))

        latest = rows[0]
        radiation = float(latest[2]) if latest[2] is not None else 0.0
        sensor_name = latest[1]
        area = latest[4]

        print("\nLatest simulated reading:", f"{radiation:.2f}")
        print("Sensor:", sensor_name)
        print("Area:", area)

        # Project-defined simulated thresholds only.
        if radiation >= RADIATION_CRITICAL_LIMIT:
            severity = "CRITICAL"
            condition = "Very high radiation detected"
            recommendation = (
                "Project simulation: flag the area for immediate safety response "
                "and investigate the source."
            )
        elif radiation >= RADIATION_HIGH_LIMIT:
            severity = "HIGH"
            condition = "High radiation detected"
            recommendation = (
                "Project simulation: restrict access to the affected area and "
                "inspect the radiation zone."
            )
        else:
            severity = "NORMAL"
            condition = "Radiation level within project threshold"
            recommendation = "Continue routine monitoring."

        print("\nAlert Status:", severity)
        print("Condition:", condition)
        print("Recommendation:", recommendation)

        if severity != "NORMAL":
            create_role_notifications(
                conn,
                severity,
                condition,
                recommendation
            )
            print("\n🔔 Notification created for:")
            print("   Admin | Plant Manager | Engineer | Safety Officer")
        else:
            print("\nNo new notification required.")

    except (Error, ValueError) as e:
        print("Radiation Alert Error:", e)


def dashboard(conn, username, role):

    while True:

        print("\n")
        print("=" * 75)
        print("                         NUCLEUS OS")
        print("            Nuclear Waste & Radiation Monitoring System")
        print("=" * 75)

        print("\nWelcome,", username)
        print("Role    :", role)
        dashboard_notification_header(conn, role)

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
            print("17. Intelligent Safety Engine")
            print("18. Recommendation History")
            print("19. Notification Centre")
            print("20. Logout")

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

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "18":

                recommendation_history(conn)

            elif choice == "19":

                notification_center(conn, role)

            elif choice == "20":

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
            print("14. Intelligent Safety Engine")
            print("15. Recommendation History")
            print("16. Notification Centre")
            print("17. Logout")

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

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "15":

                recommendation_history(conn)

            elif choice == "16":

                notification_center(conn, role)

            elif choice == "17":

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
            print("7. Intelligent Safety Engine")
            print("8. Recommendation History")
            print("9. Notification Centre")
            print("10. Logout")

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

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "8":

                recommendation_history(conn)

            elif choice == "9":

                notification_center(conn, role)

            elif choice == "10":

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
            print("7. Intelligent Safety Engine")
            print("8. Recommendation History")
            print("9. Notification Centre")
            print("10. Logout")

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

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "8":

                recommendation_history(conn)

            elif choice == "9":

                notification_center(conn, role)

            elif choice == "10":

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

        # Small notification centre shown ABOVE the start menu.
        notification_summary(conn)

        print("\n------------------- START MENU -------------------")
        print("1. Sign Up")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

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

