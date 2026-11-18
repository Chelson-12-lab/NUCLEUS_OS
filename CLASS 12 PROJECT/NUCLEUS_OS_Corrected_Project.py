
import mysql.connector

MONITORING_INTERVAL = 30  # simulated radiation sampling interval
FUEL_CHANGE_PER_MINUTE = 1.0
STORAGE_INCREASE_PER_90_SECONDS = 100.0
OTHER_VALUES_INTERVAL_CYCLES = 3  # 3 x 30 seconds = 90 seconds

from mysql.connector import Error
from tabulate import tabulate
import random
import time
import threading


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
# UPDATE RECORD
# ==========================================================

def update_record(conn, table, primary_key):
    """Update a selected field in an existing record for any database module."""
    cursor = None
    try:
        cursor = conn.cursor()
        # Get real columns from MySQL so the update menu follows each table schema.
        cursor.execute(f"SHOW COLUMNS FROM `{table}`")
        schema = cursor.fetchall()
        column_names = [row[0] for row in schema]

        if not column_names:
            print("No columns were found for this table.")
            return

        if primary_key not in column_names:
            print(f"Update unavailable: primary key '{primary_key}' was not found in {table}.")
            return

        record_id = input(f"\nEnter {primary_key.replace('_', ' ')} of the record to update: ").strip()
        if not record_id:
            print("Record ID is required.")
            return

        cursor.execute(
            f"SELECT * FROM `{table}` WHERE `{primary_key}` = %s LIMIT 1",
            (record_id,)
        )
        record = cursor.fetchone()
        if record is None:
            print("Record not found.")
            return

        print("\nCurrent record:")
        print(tabulate([record], headers=column_names, tablefmt="grid", stralign="left"))

        editable_columns = [c for c in column_names if c != primary_key]
        print("\nSelect the field to update:")
        for index, column in enumerate(editable_columns, 1):
            print(f"{index}. {column.replace('_', ' ').title()}")
        print(f"{len(editable_columns) + 1}. Cancel")

        choice = input("Enter field choice: ").strip()
        if choice == str(len(editable_columns) + 1):
            print("Update cancelled.")
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(editable_columns)):
            print("Invalid field choice.")
            return

        column = editable_columns[int(choice) - 1]
        new_value = input(f"Enter new value for {column.replace('_', ' ')}: ").strip()
        if new_value == "":
            print("The new value cannot be empty. Update cancelled.")
            return

        cursor.execute(
            f"UPDATE `{table}` SET `{column}` = %s WHERE `{primary_key}` = %s",
            (new_value, record_id)
        )
        conn.commit()
        print("Record updated successfully!" if cursor.rowcount else "No changes were made.")

    except Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Database Error while updating record:", e)
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass


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


def generate_automatic_radiation_readings(conn, cycle_number):
    """Generate one automatic set of simulated readings for the project.

    No hardware is used. These values are simulated by Python for demonstration.
    """
    sensors = [
        ("RAD-001", "Reactor Building", 0.18),
        ("RAD-002", "Turbine Building", 0.12),
        ("RAD-003", "Control Room", 0.09),
        ("RAD-004", "Fuel Handling Area", 0.65),
        ("RAD-005", "Waste Storage Area", 0.80),
        ("RAD-006", "Reactor Area", 0.35),
        ("RAD-007", "Radiation Monitoring Room", 0.15),
        ("RAD-008", "Equipment Area", 0.35),
    ]

    # Normal small variation keeps the readings realistic-looking for a demo.
    readings = []
    for sensor_id, location, base in sensors:
        reading = max(0.01, random.gauss(base, max(0.02, base * 0.08)))
        readings.append([sensor_id, location, reading])

    # One demonstration alert is generated only after each COMPLETE 10-cycle block.
    # Therefore alerts occur at cycle 10, then 30, then 50, then 70, etc.
    # There are NO alerts on cycles 3, 8, 13, 18, 20, etc.
    # All radiation values are simulated project data.
    if cycle_number >= 10 and cycle_number % 20 == 10:
        alert_index = random.randrange(len(readings))
        alert_type = random.choice(["Warning", "High", "Critical"])

        if alert_type == "Warning":
            readings[alert_index][2] = round(random.uniform(1.05, 1.60), 2)
        elif alert_type == "High":
            readings[alert_index][2] = round(random.uniform(2.05, 2.35), 2)
        else:
            readings[alert_index][2] = round(random.uniform(2.60, 3.20), 2)

    cursor = conn.cursor()
    inserted = []

    try:
        for sensor_id, location, reading in readings:
            reading = round(reading, 2)
            status = radiation_status(reading)
            alert = radiation_alert_value(reading)

            cursor.execute("""
                INSERT INTO radiation_monitoring
                (sensor_name, radiation_reading, alert_generation, area_monitoring)
                VALUES (%s, %s, %s, %s)
            """, (sensor_id, reading, alert, location))

            inserted.append([sensor_id, location, f"{reading:.2f}", status, alert])

            if alert != "No":
                severity = "CRITICAL" if alert == "Critical" else status.upper()
                condition = (
                    f"Radiation reading {reading:.2f} µSv/h detected at {location}"
                )
                recommendation = (
                    "Project simulation: review the affected area and follow the "
                    "plant safety workflow."
                )
                create_role_notifications(
                    conn, severity, condition, recommendation
                )
                create_safety_task_if_new(conn, condition, recommendation, severity)

        conn.commit()
        return inserted

    except Error:
        conn.rollback()
        raise
    finally:
        cursor.close()


def automatic_radiation_monitoring(conn):
    """Run continuous automatic simulated radiation monitoring."""
    cycle = 0

    print("\n" + "=" * 72)
    print("              LIVE AUTOMATIC RADIATION MONITORING")
    print("=" * 72)
    print("SIMULATION MODE - No hardware is connected.")
    print("Python will automatically generate and store readings in MySQL.")
    print("Project demonstration thresholds only - not real nuclear limits.")
    print("\nPress Ctrl+C to close the live display and return to your role dashboard.")
    print("Background automatic monitoring will continue running every 30 seconds.")

    try:
        while True:
            cycle += 1
            rows = generate_automatic_radiation_readings(conn, cycle)

            print("\n" + "-" * 72)
            print(f"Automatic reading cycle #{cycle}")
            print("-" * 72)
            print(tabulate(
                rows,
                headers=[
                    "Sensor ID",
                    "Location",
                    "Radiation (µSv/h)",
                    "Status",
                    "Alert"
                ],
                tablefmt="simple",
                stralign="left"
            ))

            alert_rows = [row for row in rows if row[4] != "No"]
            if alert_rows:
                print("\n🔔 ALERT DETECTED - Notification Centre updated for:")
                print("   Admin | Plant Manager | Engineer | Safety Officer")
            else:
                print("\n✓ All simulated readings are within project thresholds.")

            print("\nNext automatic reading in 30 seconds... (Ctrl+C to stop)")
            time.sleep(MONITORING_INTERVAL)

    except KeyboardInterrupt:
        # Ctrl+C closes only the live monitoring display.
        # The background automatic monitoring continues every 30 seconds.
        print("\n\nLive monitoring display closed.")
        print("Background automatic monitoring is still running.")
        print("Returning to your role dashboard...")
        return True
    except Error as e:
        print("\nDatabase Error during automatic monitoring:", e)
    except Exception as e:
        print("\nMonitoring Error:", e)
    return False


def radiation_monitoring_module(conn):
    """Radiation Monitoring with automatic simulated sensor readings."""
    while True:
        print("\n")
        print("=" * 72)
        print("                    RADIATION MONITORING")
        print("=" * 72)
        print("1. View Records")
        print("2. Start Automatic Monitoring")
        print("3. Add Record Manually")
        print("4. Update Record")
        print("5. Delete Record")
        print("6. Back")

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
            # Ctrl+C returns from the live screen directly to the user's
            # role dashboard. Background monitoring continues in its thread.
            returned_to_dashboard = automatic_radiation_monitoring(conn)
            if returned_to_dashboard:
                return

        elif choice == "3":
            print("\nManual entry is available, but automatic simulation is recommended.")
            print("Enter the following details:")
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

        elif choice == "4":
            update_record(conn, "radiation_monitoring", "sensor_record_id")

        elif choice == "5":
            delete_record(conn, "radiation_monitoring", "sensor_record_id")

        elif choice == "6":
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
        print("3. Update Record")
        print("4. Delete Record")
        if table == "fuel_management":
            print("5. Refuel / Update Fuel Quantity")
            print("6. Back")
        else:
            print("5. Back")

        choice = input("\nEnter your choice: ").strip()

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

            update_record(
                conn,
                table,
                primary_key
            )

        elif choice == "4":

            delete_record(
                conn,
                table,
                primary_key
            )

        elif table == "fuel_management" and choice == "5":
            refuel_fuel_record(conn)

        elif (table == "fuel_management" and choice == "6") or (
            table != "fuel_management" and choice == "5"
        ):
            break

        else:
            print("\nInvalid choice!")



def refuel_fuel_record(conn):
    """Update a simulated fuel record to record a refuelling action."""
    print("\n" + "=" * 60)
    print("REFUEL / UPDATE FUEL QUANTITY")
    print("=" * 60)
    print("Educational simulation only; this records project data and does not control real equipment.")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fuel_id, reactor_id, fuel_type, quantity, usage_status
            FROM fuel_management
            ORDER BY fuel_id
        """)
        rows = cursor.fetchall()
        if not rows:
            print("No fuel records found.")
            cursor.close()
            return

        print(tabulate(rows, headers=["Fuel ID", "Reactor ID", "Fuel Type", "Quantity (%)", "Usage Status"], tablefmt="grid"))
        fuel_id_text = input("\nEnter Fuel ID to update: ").strip()
        if not fuel_id_text.isdigit():
            print("Fuel ID must be a number.")
            cursor.close()
            return

        fuel_id = int(fuel_id_text)
        cursor.execute("""
            SELECT fuel_id, reactor_id, fuel_type, quantity, usage_status
            FROM fuel_management WHERE fuel_id = %s
        """, (fuel_id,))
        record = cursor.fetchone()
        if not record:
            print("Fuel record not found.")
            cursor.close()
            return

        print(f"Current quantity: {record[3]}%")
        print(f"Current status: {record[4]}")
        quantity_text = input("Enter updated fuel quantity (0-100%): ").strip()
        try:
            new_quantity = float(quantity_text)
        except ValueError:
            print("Enter a valid numeric quantity.")
            cursor.close()
            return
        if not 0 <= new_quantity <= 100:
            print("Quantity must be between 0 and 100 for this simulation.")
            cursor.close()
            return

        new_status = "Empty" if new_quantity <= 0 else ("Low" if new_quantity < FUEL_LOW_LIMIT else "Available")
        confirm = input(f"Confirm updating Fuel ID {fuel_id} to {new_quantity:.1f}% with status '{new_status}'? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("Update cancelled.")
            cursor.close()
            return

        cursor.execute("""
            UPDATE fuel_management SET quantity = %s, usage_status = %s
            WHERE fuel_id = %s
        """, (new_quantity, new_status, fuel_id))
        conn.commit()
        cursor.close()
        print("\nFuel record updated successfully.")
        print(f"Fuel ID: {fuel_id} | Updated quantity: {new_quantity:.1f}% | Status: {new_status}")
        print("Fuel update recorded. Continue the task response, then submit a completion report to Admin when ready.")
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Could not update fuel record:", e)


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
        created_count = 0
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
                created_count += 1
        conn.commit()
        cursor.close()
        return created_count
    except Error as e:
        conn.rollback()
        print("Could not create role notifications:", e)
        return 0


def notification_center(conn, role):
    """Display a compact notification centre for the logged-in role."""
    ensure_notification_table(conn)
    while True:
        print("\n" + "=" * 72)
        print(f"🔔 {role.upper()} NOTIFICATION CENTRE")
        print("=" * 72)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT notification_id, created_at, severity,
                       condition_detected, message, status
                FROM alert_notifications
                WHERE recipient_role=%s
                ORDER BY notification_id DESC
                LIMIT 10
            """, (role,))
            rows = cursor.fetchall()
            cursor.close()

            unread = unread_notification_count(conn, role)
            print(f"Unread notifications: {unread}")

            if rows:
                # Keep the notification centre narrow enough for the IDLE window.
                compact_rows = []
                for row in rows:
                    notification_id, created_at, severity, condition, message, status = row
                    if created_at:
                        created = created_at.strftime("%d-%m %H:%M")
                    else:
                        created = "-"
                    short_message = str(message)
                    if len(short_message) > 42:
                        short_message = short_message[:39] + "..."
                    compact_rows.append([
                        notification_id,
                        created,
                        severity,
                        short_message,
                        status
                    ])

                print(tabulate(
                    compact_rows,
                    headers=["ID", "Time", "Severity", "Message", "Status"],
                    tablefmt="simple",
                    stralign="left",
                    maxcolwidths=[5, 12, 10, 45, 8]
                ))
            else:
                print("No notifications.")
        except Error as e:
            print("Notification Error:", e)

        print("\n1. Mark all as read")
        print("2. Back to Dashboard")
        choice = input("Enter your choice: ")

        if choice == "1":
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE alert_notifications SET status='Read'
                    WHERE recipient_role=%s AND status='Unread'
                """, (role,))
                conn.commit()
                print(f"{cursor.rowcount} notification(s) marked as read.")
                cursor.close()
            except Error as e:
                conn.rollback()
                print("Database Error:", e)
        elif choice == "2":
            break
        else:
            print("Invalid choice!")


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


def _show_safety_module_findings(conn, username, role, module_title, findings):
    """Display, save, and notify findings from one focused safety module."""
    print("\n" + "=" * 76)
    print(module_title.upper())
    print("=" * 76)
    print("Educational simulation only; not for real plant operations.\n")

    if not findings:
        print("No matching conditions were found in the available demo data.")
        return

    for index, (severity, condition, recommendation) in enumerate(findings, 1):
        print(f"{index}. [{severity}] {condition}")
        print(f"   Recommendation: {recommendation}")
        try:
            save_recommendation(
                conn, username, role, severity, condition, recommendation,
                1 if severity == "CRITICAL" else 2
            )
        except Exception:
            pass
        try:
            create_role_notifications(conn, severity, condition, recommendation)
            create_safety_task_if_new(conn, condition, recommendation, severity)
        except Exception:
            pass
    print("\nFindings saved; Admin notifications and safety tasks were attempted.")


def waste_storage_safety_module(conn, username, role):
    """Module 1: detect waste-storage occupancy greater than 90%."""
    findings = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT storage_building, capacity, available_space FROM waste_storage")
        for building, capacity, available in cursor.fetchall():
            if capacity is None or available is None or float(capacity) <= 0:
                continue
            occupancy = ((float(capacity) - float(available)) / float(capacity)) * 100
            if occupancy > 90.0:
                findings.append(("HIGH", f"Storage {building} is {occupancy:.1f}% full",
                                 "Transfer waste to long-term storage."))
        cursor.close()
    except Error as e:
        print("Waste storage check unavailable:", e)
    _show_safety_module_findings(conn, username, role, "Waste Storage Capacity Check", findings)


def overdue_maintenance_safety_module(conn, username, role):
    """Module 2: find past-due maintenance records not marked complete."""
    from datetime import date, datetime
    findings = []
    completed = {"completed", "complete", "done", "closed", "resolved"}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT equipment_name, maintenance_date, maintenance_status FROM maintenance")
        for equipment_name, maintenance_date, status in cursor.fetchall():
            if not maintenance_date or str(status or "").strip().lower() in completed:
                continue
            if isinstance(maintenance_date, datetime):
                due_date = maintenance_date.date()
            else:
                due_date = maintenance_date
            if due_date < date.today():
                findings.append(("HIGH", f"Maintenance overdue for {equipment_name} (due {due_date})",
                                 "Generate maintenance work order."))
        cursor.close()
    except Error as e:
        print("Maintenance check unavailable:", e)
    _show_safety_module_findings(conn, username, role, "Overdue Maintenance Check", findings)


def employee_exposure_safety_module(conn, username, role):
    """Module 3: compare recorded employee exposure against its stored demo limit."""
    findings = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id, monthly_exposure, safe_limit FROM employee_exposure")
        for employee_id, monthly, safe_limit in cursor.fetchall():
            if monthly is not None and safe_limit is not None and float(monthly) > float(safe_limit):
                findings.append(("CRITICAL", f"Employee {employee_id} exposure exceeds the recorded limit ({monthly} > {safe_limit})",
                                 "Remove employee from radiation zone."))
        cursor.close()
    except Error as e:
        print("Employee exposure check unavailable:", e)
    _show_safety_module_findings(conn, username, role, "Employee Radiation Exposure Check", findings)


def equipment_health_safety_module(conn, username, role):
    """Module 4: flag equipment records with poor/failed/unsafe status."""
    findings = []
    poor_statuses = {"poor", "critical", "failed", "failure", "damaged", "replace", "unsafe"}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT equipment_name, equipment_status FROM equipment")
        for equipment_name, status in cursor.fetchall():
            if str(status or "").strip().lower() in poor_statuses:
                findings.append(("HIGH", f"Equipment health is poor: {equipment_name} ({status})",
                                 "Replace equipment after appropriate inspection and authorization."))
        cursor.close()
    except Error as e:
        print("Equipment health check unavailable:", e)
    _show_safety_module_findings(conn, username, role, "Equipment Health Check", findings)


def reactor_temperature_safety_module(conn, username, role):
    """Module 5: check a user-entered simulated reactor temperature."""
    findings = []
    print("This module uses a project-defined simulated threshold, not a real operating limit.")
    temperature = get_float_input("Enter simulated reactor temperature in °C: ")
    if temperature >= REACTOR_TEMP_HIGH_LIMIT:
        findings.append(("CRITICAL", f"Simulated reactor temperature is high: {temperature:.1f} °C",
                         "Initiate controlled shutdown."))
    elif temperature >= REACTOR_TEMP_HIGH_LIMIT * 0.90:
        findings.append(("WARNING", f"Simulated reactor temperature is approaching the project threshold: {temperature:.1f} °C",
                         "Review the simulated condition and continue monitoring the demonstration."))
    else:
        print(f"Temperature {temperature:.1f} °C is below the project's simulated warning threshold.")
    _show_safety_module_findings(conn, username, role, "Simulated Reactor Temperature Check", findings)


def additional_safety_checks_module(conn, username, role):
    """Submenu for the five independent additional safety modules."""
    while True:
        print("\n" + "=" * 72)
        print("          ADDITIONAL SAFETY MODULES")
        print("=" * 72)
        print("1. Waste Storage Capacity Check")
        print("2. Overdue Maintenance Check")
        print("3. Employee Radiation Exposure Check")
        print("4. Equipment Health Check")
        print("5. Simulated Reactor Temperature Check")
        print("6. Back to Dashboard")
        choice = input("\nChoose a safety module: ").strip()

        if choice == "1":
            waste_storage_safety_module(conn, username, role)
        elif choice == "2":
            overdue_maintenance_safety_module(conn, username, role)
        elif choice == "3":
            employee_exposure_safety_module(conn, username, role)
        elif choice == "4":
            equipment_health_safety_module(conn, username, role)
        elif choice == "5":
            reactor_temperature_safety_module(conn, username, role)
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please select 1-6.")


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



# ==========================================================
# SAFETY TASK ASSIGNMENT, TWO-WAY MESSAGES AND AUDIT TRAIL
# ==========================================================

def ensure_safety_task_tables(conn):
    """Create workflow tables without changing existing project tables."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_tasks (
            task_id INT AUTO_INCREMENT PRIMARY KEY,
            condition_detected VARCHAR(255) NOT NULL,
            recommendation VARCHAR(500) NOT NULL,
            priority VARCHAR(30) DEFAULT 'HIGH',
            assigned_by VARCHAR(100) DEFAULT NULL,
            assigned_to VARCHAR(100) DEFAULT NULL,
            assigned_role VARCHAR(50) DEFAULT NULL,
            task_status VARCHAR(40) DEFAULT 'Pending Assignment',
            admin_review VARCHAR(60) DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            closed_at DATETIME DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_task_messages (
            message_id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT NOT NULL,
            sender_username VARCHAR(100) NOT NULL,
            sender_role VARCHAR(50) NOT NULL,
            message_type VARCHAR(40) NOT NULL,
            message_text VARCHAR(1000) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_safety_task_messages_task (task_id)
        )
    """)
    conn.commit()
    cursor.close()


def send_direct_task_notification(conn, recipient_role, severity, condition, message):
    """Send a task-specific notification to one role."""
    ensure_notification_table(conn)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alert_notifications
        (recipient_role, severity, condition_detected, message, status)
        VALUES (%s, %s, %s, %s, 'Unread')
    """, (recipient_role, severity, condition[:255], message[:500]))
    conn.commit()
    cursor.close()


def recommended_role_for_condition(condition, recommendation=''):
    text = (str(condition) + ' ' + str(recommendation)).lower()
    if 'radiation' in text or 'fuel' in text or 'reactor temperature' in text:
        return 'Plant Manager'
    if 'storage' in text or 'maintenance' in text or 'work order' in text:
        return 'Engineer'
    if 'exposure' in text or 'employee' in text or 'equipment' in text:
        return 'Safety Officer'
    return 'Plant Manager'


def create_safety_task_if_new(conn, condition, recommendation, priority='HIGH'):
    """Create one open task per condition so background cycles don't duplicate it."""
    try:
        ensure_safety_task_tables(conn)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_id FROM safety_tasks
            WHERE condition_detected=%s AND task_status <> 'Closed'
            LIMIT 1
        """, (str(condition)[:255],))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            return existing[0]
        cursor.execute("""
            INSERT INTO safety_tasks
            (condition_detected, recommendation, priority, task_status, admin_review)
            VALUES (%s, %s, %s, 'Pending Assignment', 'Pending')
        """, (str(condition)[:255], str(recommendation)[:500], str(priority)[:30]))
        task_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        send_direct_task_notification(
            conn, 'Admin', priority, condition,
            f'New safety finding TASK-{task_id:04d}: {condition}. Recommendation: {recommendation}. Please assign a responsible staff member.'
        )
        return task_id
    except Error as e:
        try: conn.rollback()
        except Exception: pass
        print('Could not create safety task:', e)
        return None


def add_task_message(conn, task_id, username, role, message_type, message_text):
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO safety_task_messages
        (task_id, sender_username, sender_role, message_type, message_text)
        VALUES (%s, %s, %s, %s, %s)
    """, (task_id, username, role, message_type, message_text[:1000]))
    conn.commit()
    cursor.close()


def show_safety_tasks(conn, role, username, admin_view=False):
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    if admin_view and role == 'Admin':
        cursor.execute("""
            SELECT task_id, condition_detected, priority, assigned_to,
                   assigned_role, task_status, admin_review, created_at
            FROM safety_tasks ORDER BY task_id DESC
        """)
    else:
        cursor.execute("""
            SELECT task_id, condition_detected, priority, assigned_role,
                   task_status, admin_review, created_at
            FROM safety_tasks WHERE assigned_to=%s ORDER BY task_id DESC
        """, (username,))
    rows = cursor.fetchall()
    cursor.close()
    print('\n' + '=' * 100)
    print('SAFETY TASK TRACKER')
    print('=' * 100)
    headers = (['Task ID', 'Condition', 'Priority', 'Assigned To', 'Role', 'Status', 'Admin Review', 'Created']
               if admin_view and role == 'Admin'
               else ['Task ID', 'Condition', 'Priority', 'Assigned Role', 'Status', 'Admin Review', 'Created'])
    print(tabulate(rows, headers=headers, tablefmt='grid', stralign='left') if rows else 'No matching tasks found.')


def sync_admin_notifications_to_tasks(conn):
    """Recover Admin findings that have a notification but no safety_tasks row.

    This makes older notifications assignable even if they were created before
    the task workflow was connected to that module.
    """
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT severity, condition_detected, message
            FROM alert_notifications
            WHERE TRIM(recipient_role)='Admin'
            ORDER BY notification_id DESC
        """)
        notifications = cursor.fetchall()
        for severity, condition, message in notifications:
            condition = str(condition or '').strip()
            message = str(message or '').strip()
            # Task-assignment notifications are already linked to an existing task.
            if not condition or condition.upper().startswith('TASK-'):
                continue
            cursor.execute("""
                SELECT task_id FROM safety_tasks
                WHERE condition_detected=%s AND task_status <> 'Closed'
                LIMIT 1
            """, (condition[:255],))
            if cursor.fetchone():
                continue

            recommendation = message
            if 'Recommendation:' in message:
                recommendation = message.split('Recommendation:', 1)[1].strip()
            elif not recommendation:
                recommendation = 'Review the finding and decide the appropriate action.'
            cursor.execute("""
                INSERT INTO safety_tasks
                (condition_detected, recommendation, priority, task_status, admin_review)
                VALUES (%s, %s, %s, 'Pending Assignment', 'Pending')
            """, (condition[:255], recommendation[:500], str(severity or 'HIGH')[:30]))
        conn.commit()
    except Error as e:
        conn.rollback()
        print('Could not sync Admin notifications into the task queue:', e)
    finally:
        cursor.close()


def admin_assign_safety_task(conn, username):
    ensure_safety_task_tables(conn)
    # Recover notifications that were generated before task creation was wired in.
    sync_admin_notifications_to_tasks(conn)

    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, condition_detected, recommendation, priority
        FROM safety_tasks WHERE task_status IN ('Pending Assignment', 'Detected')
        ORDER BY task_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    print('\nPENDING SAFETY FINDINGS')
    print(tabulate(rows, headers=['Task ID', 'Condition', 'Recommendation', 'Priority'], tablefmt='grid') if rows else 'No findings are waiting for assignment.')
    if not rows:
        print('\nIf Admin has unread notifications, open Notification Centre and confirm they describe a safety finding. Only safety findings can be assigned; task-response notifications are not new tasks.')
        return
    try:
        task_id = int(input('Enter task ID to assign (0 to cancel): ').strip())
    except ValueError:
        print('Invalid task ID. Please enter the numeric Task ID shown in the table.')
        return
    if task_id == 0:
        return
    cursor = conn.cursor()
    cursor.execute("""SELECT task_id, condition_detected, recommendation, priority
                      FROM safety_tasks
                      WHERE task_id=%s AND task_status IN ('Pending Assignment', 'Detected')""", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    if not task:
        print('That task is not available for assignment. Refresh the list and use a Task ID from the table.')
        return

    suggested_role = recommended_role_for_condition(task[1], task[2])
    print('\nChoose staff role:')
    print('1. Plant Manager')
    print('2. Engineer')
    print('3. Safety Officer')
    role_map = {'1': 'Plant Manager', '2': 'Engineer', '3': 'Safety Officer'}
    role_choice = input(f'Suggested role is {suggested_role}. Enter choice (1-3): ').strip()
    if role_choice not in role_map:
        print('Invalid role selection.')
        return
    assigned_role = role_map[role_choice]

    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE LOWER(TRIM(role))=LOWER(TRIM(%s)) ORDER BY username", (assigned_role,))
    staff = [r[0] for r in cursor.fetchall()]
    cursor.close()
    if not staff:
        print(f'No registered user found for role {assigned_role}. Check the role values in the MySQL users table.')
        return
    print('\nRegistered staff:')
    for i, name in enumerate(staff, 1):
        print(f'{i}. {name}')
    try:
        staff_choice = int(input('Select staff number: ').strip())
        if not 1 <= staff_choice <= len(staff):
            raise ValueError
    except ValueError:
        print('Invalid staff selection.')
        return
    assigned_to = staff[staff_choice - 1]

    cursor = conn.cursor()
    cursor.execute("""
        UPDATE safety_tasks
        SET assigned_by=%s, assigned_to=%s, assigned_role=%s,
            task_status='Assigned', admin_review='Pending'
        WHERE task_id=%s AND task_status IN ('Pending Assignment', 'Detected')
    """, (username, assigned_to, assigned_role, task_id))
    conn.commit()
    updated = cursor.rowcount
    cursor.close()
    if not updated:
        print('Task status changed before assignment. Please reopen the task list and try again.')
        return
    add_task_message(conn, task_id, username, 'Admin', 'Assignment', f'Assigned to {assigned_to} ({assigned_role}).')
    send_direct_task_notification(conn, assigned_role, task[3], f'TASK-{task_id:04d}',
        f'Admin {username} assigned TASK-{task_id:04d}: {task[1]}. Recommendation: {task[2]}')
    print(f'\nTASK-{task_id:04d} assigned to {assigned_to} ({assigned_role}); notification sent.')


def staff_task_response(conn, username, role, completion=False):
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, condition_detected, recommendation, task_status
        FROM safety_tasks WHERE assigned_to=%s AND task_status <> 'Closed'
        ORDER BY task_id
    """, (username,))
    rows = cursor.fetchall()
    cursor.close()
    print('\nYOUR OPEN TASKS')
    print(tabulate(rows, headers=['Task ID', 'Condition', 'Recommendation', 'Status'], tablefmt='grid') if rows else 'You have no open assigned tasks.')
    if not rows: return
    try: task_id = int(input('Enter task ID (0 to cancel): ').strip())
    except ValueError:
        print('Invalid task ID.'); return
    if task_id == 0: return
    valid_ids = {r[0] for r in rows}
    if task_id not in valid_ids:
        print('That task is not assigned to your account.'); return

    selected_task = next(row for row in rows if row[0] == task_id)
    task_condition = str(selected_task[1] or '').lower()
    task_recommendation = str(selected_task[2] or '').lower()

    # Every staff role completes the relevant project action from Submit Task Response.
    # The assigned task, not the user's role alone, determines which module opens.
    if not completion:
        task_text = task_condition + ' ' + task_recommendation
        action_opened = False
        if any(word in task_text for word in ('fuel', 'refuelling', 'refueling', 'refuel')):
            print('\nAssigned action: review/update simulated fuel quantity.')
            refuel_fuel_record(conn)
            action_opened = True
        elif any(word in task_text for word in ('storage', 'waste', 'long-term')):
            print('\nAssigned action: review radioactive waste / storage records and update the relevant record.')
            database_module(conn, 'Waste Storage', 'waste_storage',
                ['storage_id', 'storage_building', 'capacity', 'available_space', 'inspection_records'],
                ['storage_building', 'capacity', 'available_space', 'inspection_records'], 'storage_id')
            action_opened = True
        elif any(word in task_text for word in ('maintenance', 'work order', 'overdue')):
            print('\nAssigned action: create/update the maintenance work-order record.')
            database_module(conn, 'Maintenance', 'maintenance',
                ['maintenance_id', 'equipment_name', 'maintenance_date', 'maintenance_status'],
                ['equipment_name', 'maintenance_date', 'maintenance_status'], 'maintenance_id')
            action_opened = True
        elif any(word in task_text for word in ('exposure', 'radiation zone', 'employee')):
            print('\nAssigned action: review/update the simulated employee exposure record.')
            database_module(conn, 'Radiation Exposure', 'employee_exposure',
                ['exposure_id', 'employee_id', 'daily_exposure', 'monthly_exposure', 'safe_limit', 'limit_status', 'recorded_date'],
                ['employee_id', 'daily_exposure', 'monthly_exposure', 'safe_limit', 'limit_status', 'recorded_date'], 'exposure_id')
            action_opened = True
        elif any(word in task_text for word in ('equipment', 'replace', 'poor health', 'failed')):
            print('\nAssigned action: review/update the equipment status after simulated inspection.')
            database_module(conn, 'Equipment', 'equipment',
                ['equipment_id', 'equipment_name', 'equipment_type', 'equipment_status'],
                ['equipment_name', 'equipment_type', 'equipment_status'], 'equipment_id')
            action_opened = True
        elif any(word in task_text for word in ('radiation', 'evacuation', 'reactor temperature', 'shutdown')):
            print('\nAssigned action: review the simulated radiation monitoring readings.')
            radiation_monitoring_module(conn)
            print('Reminder: this is a school-project simulation only; it does not control real equipment or replace emergency procedures.')
            action_opened = True

        if action_opened:
            print('\nRelevant task module opened. Finish the required record update, return here, and enter your task response.')
        else:
            print('\nNo dedicated module matched this task text. You can still describe the action taken in your response.')

    message_type = 'Completion Report' if completion else 'Response'
    prompt = 'Describe the simulated action completed and result: ' if completion else 'Enter your response / progress update: '
    message = input(prompt).strip()
    if not message:
        print('A response is required.'); return
    add_task_message(conn, task_id, username, role, message_type, message)
    new_status = 'Report Submitted' if completion else 'In Progress'
    cursor = conn.cursor()
    cursor.execute("UPDATE safety_tasks SET task_status=%s, admin_review=%s WHERE task_id=%s AND assigned_to=%s",
                   (new_status, 'Pending', task_id, username))
    conn.commit(); cursor.close()
    add_task_message(conn, task_id, username, role, 'Status Update', f'Task status changed to {new_status}.')
    send_direct_task_notification(conn, 'Admin', 'HIGH', f'TASK-{task_id:04d}',
        f'{role} {username} submitted a {message_type.lower()} for TASK-{task_id:04d}: {message}')
    print(f'{message_type} sent to Admin. Task status: {new_status}.')


def admin_review_task_reports(conn, username):
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT task_id, condition_detected, assigned_to, task_status
        FROM safety_tasks WHERE task_status='Report Submitted'
        ORDER BY task_id
    """)
    rows = cursor.fetchall(); cursor.close()
    print('\nREPORTS AWAITING ADMIN REVIEW')
    print(tabulate(rows, headers=['Task ID', 'Condition', 'Submitted By', 'Status'], tablefmt='grid') if rows else 'No reports are awaiting review.')
    if not rows: return
    try: task_id = int(input('Enter task ID to review (0 to cancel): ').strip())
    except ValueError:
        print('Invalid task ID.'); return
    if task_id == 0: return
    if task_id not in {r[0] for r in rows}:
        print('That task is not awaiting review.'); return
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender_username, sender_role, message_type, message_text, created_at
        FROM safety_task_messages WHERE task_id=%s ORDER BY message_id
    """, (task_id,))
    messages = cursor.fetchall(); cursor.close()
    print('\nTASK MESSAGE HISTORY')
    print(tabulate(messages, headers=['Sender', 'Role', 'Type', 'Message', 'Time'], tablefmt='grid') if messages else 'No messages.')
    print('\n1. Approve and close task\n2. Request further action\n3. Reopen task\n4. Cancel')
    choice = input('Choose review action: ').strip()
    cursor = conn.cursor()
    if choice == '1':
        cursor.execute("UPDATE safety_tasks SET task_status='Closed', admin_review='Approved', closed_at=NOW() WHERE task_id=%s", (task_id,))
        msg = 'Admin approved the completion report and closed the task.'
        status = 'Approved'
    elif choice == '2':
        cursor.execute("UPDATE safety_tasks SET task_status='Further Action Required', admin_review='Further Action Required' WHERE task_id=%s", (task_id,))
        msg = input('Enter required follow-up action: ').strip() or 'Please review and provide further action.'
        status = 'Further Action Required'
    elif choice == '3':
        cursor.execute("UPDATE safety_tasks SET task_status='In Progress', admin_review='Reopened', closed_at=NULL WHERE task_id=%s", (task_id,))
        msg = 'Admin reopened the task for further work.'
        status = 'Reopened'
    else:
        cursor.close(); print('Review cancelled.'); return
    conn.commit(); cursor.close()
    add_task_message(conn, task_id, username, 'Admin', 'Admin Review', msg)
    cursor = conn.cursor(); cursor.execute('SELECT assigned_role, assigned_to FROM safety_tasks WHERE task_id=%s', (task_id,)); target = cursor.fetchone(); cursor.close()
    if target and target[0]:
        send_direct_task_notification(conn, target[0], 'HIGH', f'TASK-{task_id:04d}', f'Admin review for TASK-{task_id:04d}: {status}. {msg}')
    print('Review saved and notification sent to assigned staff.')


def admin_view_task_messages(conn):
    ensure_safety_task_tables(conn)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.task_id, m.sender_username, m.sender_role, m.message_type, m.message_text, m.created_at
        FROM safety_task_messages m ORDER BY m.message_id DESC LIMIT 100
    """)
    rows = cursor.fetchall(); cursor.close()
    print('\nSTAFF RESPONSES AND AUDIT HISTORY')
    print(tabulate(rows, headers=['Task ID', 'Sender', 'Role', 'Type', 'Message', 'Time'], tablefmt='grid') if rows else 'No task messages have been submitted.')


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
            print("2. Reactor Management")
            print("3. Power Generation")
            print("4. Fuel Management")
            print("5. Fuel Rod Tracking")
            print("6. Radiation Alert")
            print("7. Radiation Monitoring")
            print("8. Radioactive Waste")
            print("9. Waste Storage")
            print("10. Radiation Exposure")
            print("11. Safety Inspection")
            print("12. Maintenance")
            print("13. Recommendation History")
            print("14. Notification Centre")
            print("15. Waste Storage Capacity Check")
            print("16. Overdue Maintenance Check")
            print("17. Employee Radiation Exposure Check")
            print("18. Equipment Health Check")
            print("19. Simulated Reactor Temperature Check")
            print("20. Assign Pending Safety Task")
            print("21. View All Assigned Tasks")
            print("22. View Staff Responses / Audit History")
            print("23. Review Completion Reports")
            print("24. Logout")

            choice = input("\nEnter your choice: ").strip()
            # Translate the compact Admin menu to the existing action handlers.
            admin_choice_map = {str(i): str(i + 1) for i in range(2, 24)}
            admin_choice_map["1"] = "1"
            admin_choice_map["24"] = "25"
            choice = admin_choice_map.get(choice, choice)

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

            # EXPOSURE
            elif choice == "11":

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
            elif choice == "12":

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
            elif choice == "13":

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

            elif choice == "14":

                recommendation_history(conn)

            elif choice == "15":

                notification_center(conn, role)

            elif choice == "16":

                waste_storage_safety_module(conn, username, role)

            elif choice == "17":

                overdue_maintenance_safety_module(conn, username, role)

            elif choice == "18":

                employee_exposure_safety_module(conn, username, role)

            elif choice == "19":

                equipment_health_safety_module(conn, username, role)

            elif choice == "20":

                reactor_temperature_safety_module(conn, username, role)

            elif choice == "21":
                admin_assign_safety_task(conn, username)

            elif choice == "22":
                show_safety_tasks(conn, role, username, admin_view=True)

            elif choice == "23":
                admin_view_task_messages(conn)

            elif choice == "24":
                admin_review_task_reports(conn, username)

            elif choice == "25":
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
            print("3. Fuel Management")
            print("4. Fuel Rod Tracking")
            print("5. Recommendation History")
            print("6. Notification Centre")
            print("7. Additional Safety Checks")
            print("8. My Assigned Tasks")
            print("9. Submit Task Response")
            print("10. Submit Completion Report")
            print("11. Logout")

            choice = input("\nEnter your choice: ").strip()
            plant_choice_map = {"1":"1", "2":"2", "3":"6", "4":"7", "5":"15", "6":"16", "7":"17", "8":"18", "9":"19", "10":"20", "11":"21"}
            choice = plant_choice_map.get(choice, choice)

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

                additional_safety_checks_module(conn, username, role)

            elif choice == "18":
                show_safety_tasks(conn, role, username)

            elif choice == "19":
                staff_task_response(conn, username, role, completion=False)

            elif choice == "20":
                staff_task_response(conn, username, role, completion=True)

            elif choice == "21":
                print("\nLogged out successfully.")
                break

            else:
                print("\nInvalid choice!")


        # ==================================================
        # ENGINEER DASHBOARD
        # ==================================================

        elif role == "Engineer":

            print("\n1. Waste Storage")
            print("2. Maintenance")
            print("3. Intelligent Safety Engine")
            print("4. Recommendation History")
            print("5. Notification Centre")
            print("6. Additional Safety Checks")
            print("7. My Assigned Tasks")
            print("8. Submit Task Response")
            print("9. Submit Completion Report")
            print("10. Logout")

            choice = input("\nEnter your choice: ").strip()
            engineer_choice_map = {"1":"15", "2":"16", "3":"7", "4":"8", "5":"9", "6":"10", "7":"11", "8":"12", "9":"13", "10":"14"}
            choice = engineer_choice_map.get(choice, choice)

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

            elif choice == "15":
                database_module(conn, "Waste Storage", "waste_storage",
                    ["storage_id", "storage_building", "capacity", "available_space", "inspection_records"],
                    ["storage_building", "capacity", "available_space", "inspection_records"], "storage_id")

            elif choice == "16":
                database_module(conn, "Maintenance", "maintenance",
                    ["maintenance_id", "equipment_name", "maintenance_date", "maintenance_status"],
                    ["equipment_name", "maintenance_date", "maintenance_status"], "maintenance_id")

            elif choice == "7":

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "8":

                recommendation_history(conn)

            elif choice == "9":

                notification_center(conn, role)

            elif choice == "10":

                additional_safety_checks_module(conn, username, role)

            elif choice == "11":
                show_safety_tasks(conn, role, username)

            elif choice == "12":
                staff_task_response(conn, username, role, completion=False)

            elif choice == "13":
                staff_task_response(conn, username, role, completion=True)

            elif choice == "14":
                print("\nLogged out successfully.")
                break

            else:
                print("\nInvalid choice!")


        # ==================================================
        # SAFETY OFFICER DASHBOARD
        # ==================================================

        elif role == "Safety Officer":

            print("\n1. Employee Exposure")
            print("2. Equipment Health")
            print("3. Safety Inspection")
            print("4. Recommendation History")
            print("5. Notification Centre")
            print("6. Additional Safety Checks")
            print("7. My Assigned Tasks")
            print("8. Submit Task Response")
            print("9. Submit Completion Report")
            print("10. Logout")

            choice = input("\nEnter your choice: ").strip()
            safety_choice_map = {"1":"15", "2":"16", "3":"5", "4":"8", "5":"9", "6":"10", "7":"11", "8":"12", "9":"13", "10":"14"}
            choice = safety_choice_map.get(choice, choice)

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

            elif choice == "15":
                employee_exposure_safety_module(conn, username, role)

            elif choice == "16":
                equipment_health_safety_module(conn, username, role)

            elif choice == "7":

                intelligent_recommendation_engine(conn, username, role)

            elif choice == "8":

                recommendation_history(conn)

            elif choice == "9":

                notification_center(conn, role)

            elif choice == "10":

                additional_safety_checks_module(conn, username, role)

            elif choice == "11":
                show_safety_tasks(conn, role, username)

            elif choice == "12":
                staff_task_response(conn, username, role, completion=False)

            elif choice == "13":
                staff_task_response(conn, username, role, completion=True)

            elif choice == "14":
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


def simulate_fuel_and_storage_changes(conn, cycle_number):
    """Update simulated quantities and other demo values on their requested schedules.

    Radiation sampling remains on its own 30-second cycle. Fuel changes every
    60 seconds; waste-storage occupancy changes every 90 seconds; the other
    safety-related demo fields are regenerated every 90 seconds.
    This is educational sample data only, not real plant control.
    """
    cursor = None
    try:
        cursor = conn.cursor()

        # Fuel: once per 60 seconds (every second 30-second cycle).
        if cycle_number % 2 == 0:
            cursor.execute("""
                UPDATE fuel_management
                SET quantity = GREATEST(0, quantity - %s),
                    usage_status = CASE
                        WHEN quantity - %s <= 0 THEN 'Empty'
                        WHEN quantity - %s < 15 THEN 'Low'
                        ELSE 'Available'
                    END
            """, (FUEL_CHANGE_PER_MINUTE,
                  FUEL_CHANGE_PER_MINUTE,
                  FUEL_CHANGE_PER_MINUTE))

        # Waste storage: once per 90 seconds (every third 30-second cycle).
        if cycle_number % OTHER_VALUES_INTERVAL_CYCLES == 0:
            cursor.execute("""
                UPDATE waste_storage
                SET available_space = GREATEST(0, available_space - %s)
            """, (STORAGE_INCREASE_PER_90_SECONDS,))

            # Regenerate employee exposure demo values every 90 seconds.
            # Values and limits are illustrative project data, not medical advice.
            cursor.execute("SELECT exposure_id, safe_limit FROM employee_exposure")
            exposure_rows = cursor.fetchall()
            for exposure_id, safe_limit in exposure_rows:
                limit_value = float(safe_limit) if safe_limit is not None else 5.0
                daily = round(random.uniform(0.0, max(0.1, limit_value * 0.35)), 2)
                monthly = round(random.uniform(0.0, max(0.1, limit_value * 1.15)), 2)
                status = 'Above Limit' if monthly > limit_value else 'Within Limit'
                cursor.execute("""
                    UPDATE employee_exposure
                    SET daily_exposure=%s, monthly_exposure=%s, limit_status=%s,
                        recorded_date=CURDATE()
                    WHERE exposure_id=%s
                """, (daily, monthly, status, exposure_id))

            # Regenerate equipment-health demo statuses.
            cursor.execute("SELECT equipment_id FROM equipment")
            for (equipment_id,) in cursor.fetchall():
                status = random.choices(
                    ['Good', 'Fair', 'Poor'], weights=[65, 25, 10], k=1
                )[0]
                cursor.execute(
                    "UPDATE equipment SET equipment_status=%s WHERE equipment_id=%s",
                    (status, equipment_id)
                )

            # Regenerate maintenance demo status without altering equipment/date fields.
            cursor.execute("SELECT maintenance_id FROM maintenance")
            for (maintenance_id,) in cursor.fetchall():
                status = random.choice(['Pending', 'In Progress', 'Completed'])
                cursor.execute(
                    "UPDATE maintenance SET maintenance_status=%s WHERE maintenance_id=%s",
                    (status, maintenance_id)
                )

        conn.commit()
    except Error:
        try:
            conn.rollback()
        except Exception:
            pass
    finally:
        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                pass


def background_intelligent_safety_checks(conn, cycle_number):
    """Run lightweight rule-based checks in the background.

    These checks use the project's simulated/demo data and thresholds.
    They create notifications for all NUCLEUS OS roles when a condition
    requires attention. They do not control any real plant equipment.
    """
    checks = []
    ensure_recommendation_table(conn)

    # 1. Waste storage > 90% full
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT storage_building, capacity, available_space
            FROM waste_storage
        """)
        for building, capacity, available in cursor.fetchall():
            if capacity is not None and float(capacity) > 0 and available is not None:
                occupancy = ((float(capacity) - float(available)) / float(capacity)) * 100
                if occupancy > 90.0:
                    checks.append((
                        "HIGH",
                        f"Waste storage above 90%: {building}",
                        f"Storage {building} is {occupancy:.1f}% full.",
                        "Transfer waste to long-term storage."
                    ))
        cursor.close()
    except Error:
        pass

    # 2. Fuel < 15%
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT reactor_id, quantity, usage_status
            FROM fuel_management
        """)
        for reactor_id, quantity, usage_status in cursor.fetchall():
            if quantity is not None and float(quantity) < 15.0:
                checks.append((
                    "HIGH",
                    f"Fuel level below 15%: Reactor {reactor_id}",
                    f"Fuel level for reactor {reactor_id} is {float(quantity):.1f}%.",
                    "Schedule refueling."
                ))
        cursor.close()
    except Error:
        pass

    # 3. Maintenance overdue
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT equipment_name, maintenance_date, maintenance_status
            FROM maintenance
        """)
        from datetime import date
        today = date.today()
        completed_statuses = {"completed", "complete", "done", "closed", "resolved"}

        for equipment_name, maintenance_date, status in cursor.fetchall():
            if (maintenance_date and maintenance_date < today and
                    str(status).strip().lower() not in completed_statuses):
                checks.append((
                    "HIGH",
                    f"Maintenance overdue: {equipment_name}",
                    f"Maintenance for {equipment_name} is overdue.",
                    "Generate maintenance work order."
                ))
        cursor.close()
    except Error:
        pass

    # 4. High employee exposure
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT employee_id, monthly_exposure, safe_limit
            FROM employee_exposure
        """)
        for employee_id, monthly, safe_limit in cursor.fetchall():
            if (monthly is not None and safe_limit is not None and
                    float(monthly) > float(safe_limit)):
                checks.append((
                    "CRITICAL",
                    f"Employee exposure above limit: {employee_id}",
                    f"Employee {employee_id} has exceeded the recorded exposure limit.",
                    "Remove employee from radiation zone."
                ))
        cursor.close()
    except Error:
        pass

    # 5. Equipment health poor
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT equipment_name, equipment_status
            FROM equipment
        """)
        poor_statuses = {"poor", "critical", "failed", "failure", "damaged", "replace", "unsafe"}
        for equipment_name, status in cursor.fetchall():
            if status and str(status).strip().lower() in poor_statuses:
                checks.append((
                    "HIGH",
                    f"Equipment health poor: {equipment_name}",
                    f"Equipment {equipment_name} has status '{status}'.",
                    "Replace equipment."
                ))
        cursor.close()
    except Error:
        pass

    # 6. Simulated reactor temperature
    # This is generated only for the educational demonstration; it is not
    # a real reactor-temperature sensor or a real nuclear operating limit.
    simulated_temperature = random.uniform(210.0, 285.0)
    if cycle_number % 20 == 10:
        simulated_temperature = random.uniform(305.0, 330.0)

    if simulated_temperature >= REACTOR_TEMP_HIGH_LIMIT:
        checks.append((
            "CRITICAL",
            "Simulated reactor temperature is high",
            f"Simulated reactor temperature is {simulated_temperature:.1f} °C.",
            "Initiate controlled shutdown."
        ))

    # Create notifications only when the condition is new/unread.
    # This prevents the 30-second background cycle from flooding the centre.
    for severity, condition, detail, recommendation in checks:
        # Keep the condition stable for duplicate detection, while the
        # notification message contains the current measured detail.
        notification_text = f"{detail} {recommendation}"
        created_count = create_role_notifications(
            conn, severity, condition, notification_text
        )
        if created_count:
            create_safety_task_if_new(conn, condition, recommendation, severity)

        # Save to Recommendation History only when a new notification event
        # was actually created for this condition.
        if created_count:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO intelligent_recommendations
                    (generated_by, role, severity, condition_detected, recommendation, priority)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    "Background Monitor",
                    "System",
                    severity,
                    condition,
                    notification_text
                    ,
                    1 if severity == "CRITICAL" else 2
                ))
                conn.commit()
                cursor.close()
            except Error:
                try:
                    conn.rollback()
                except Exception:
                    pass

    return checks


# ==========================================================
# BACKGROUND AUTOMATIC RADIATION MONITORING
# ==========================================================

def background_radiation_monitor(stop_event):
    """Lightweight background simulation; stays silent unless an error occurs."""
    cycle = 0

    while not stop_event.is_set():
        cycle += 1
        conn = None

        try:
            # Use a separate connection for the background thread.
            # Connect directly so the normal "connection successful" message
            # is not printed every monitoring cycle.
            conn = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                use_pure=True,
                connection_timeout=3
            )

            if conn.is_connected():
                generate_automatic_radiation_readings(conn, cycle)
                simulate_fuel_and_storage_changes(conn, cycle)
                background_intelligent_safety_checks(conn, cycle)

        except Exception:
            # Keep the background thread silent so it never interferes
            # with the user's menu/input.
            pass

        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

        # Wait 30 seconds, but wake immediately if the program is closing.
        stop_event.wait(MONITORING_INTERVAL)


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

            role_choice = input("\nEnter your role choice: ").strip()

            roles = {
                "1": "Admin",
                "2": "Plant Manager",
                "3": "Engineer",
                "4": "Safety Officer"
            }

            if role_choice not in roles:
                print("\nInvalid role choice!")
                continue

            selected_role = roles[role_choice]

            print("\nSelected Role:", selected_role)

            username = input("Username : ").strip()
            password = input("Password : ").strip()

            if username == "" or password == "":
                print("\nUsername and password are compulsory.")
                continue

            try:
                cursor = conn.cursor()

                # The role is selected from the menu; the user does not type it.
                # TRIM() also prevents accidental spaces in stored text from
                # causing a valid login to be rejected.
                query = """
                    SELECT user_id, username, email, role
                    FROM users
                    WHERE TRIM(username) = TRIM(%s)
                      AND BINARY TRIM(password) = BINARY TRIM(%s)
                      AND TRIM(role) = TRIM(%s)
                    LIMIT 1
                """

                cursor.execute(
                    query,
                    (username, password, selected_role)
                )

                user = cursor.fetchone()
                cursor.close()

                if user:
                    print("\n" + "=" * 60)
                    print("LOGIN SUCCESSFUL")
                    print("=" * 60)
                    print("Welcome :", user[1])
                    print("Role    :", user[3])

                    dashboard(
                        conn,
                        user[1],
                        user[3]
                    )
                else:
                    print("\nInvalid username or password for the selected role.")

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

def remove_nuclear_power_plant_table(conn):
    """Remove the obsolete Nuclear Power Plant table from the project schema."""
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS nuclear_power_plants")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    except Error as exc:
        try:
            conn.rollback()
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        except Exception:
            pass
        print("Could not remove obsolete nuclear_power_plants table:", exc)
    finally:
        if cursor is not None:
            cursor.close()

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

    # Remove the obsolete module's table as requested.
    remove_nuclear_power_plant_table(conn)

    # Start automatic simulated radiation monitoring in the background.
    # It runs while the user is at the start menu or inside a dashboard.
    monitor_stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=background_radiation_monitor,
        args=(monitor_stop_event,),
        daemon=True
    )
    monitor_thread.start()

    login(conn)

    monitor_stop_event.set()
    conn.close()

    print("\nNucleus OS closed.")
    print("Thank you.")


# ==========================================================
# RUN PROGRAM
# ==========================================================

if __name__ == "__main__":
    main()

