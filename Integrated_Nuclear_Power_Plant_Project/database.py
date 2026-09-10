import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "dani",
    "database": "nuclear_project",
    "connection_timeout": 5,
    "use_pure": True
}

def get_connection():
    try:
        print("Trying to connect...")
        con = mysql.connector.connect(**DB_CONFIG)
        print("Connection successful!")
        return con
    except mysql.connector.Error as e:
        print("MySQL connection error:", e)
        return None
