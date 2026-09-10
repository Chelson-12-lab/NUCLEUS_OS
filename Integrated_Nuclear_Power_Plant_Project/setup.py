import hashlib
from database import get_connection

PASSWORDS = {
    "admin": ("admin123", "admin@example.com", "Admin"),
    "manager": ("manager123", "manager@example.com", "Plant Manager"),
    "engineer": ("engineer123", "engineer@example.com", "Engineer"),
    "safety": ("safety123", "safety@example.com", "Safety Officer"),
    "security": ("security123", "security@example.com", "Security Officer")
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


try:
    print("Connecting to nuclear_project...")

    con = get_connection()
    cur = con.cursor()

    print("Database connection successful.")

    for username, (password, email, role) in PASSWORDS.items():

        cur.execute(
            """
            INSERT INTO users
            (username, password_hash, email, role)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            password_hash = VALUES(password_hash),
            email = VALUES(email),
            role = VALUES(role)
            """,
            (username, hash_password(password), email, role)
        )

    con.commit()

    print()
    print("Demo users created successfully!")
    print("-------------------------------")
    print("admin    / admin123")
    print("manager  / manager123")
    print("engineer / engineer123")
    print("safety   / safety123")
    print("security / security123")

except Exception as e:
    print()
    print("SETUP ERROR:")
    print(e)

finally:
    try:
        cur.close()
        con.close()
    except:
        pass

input("\nPress Enter to close...")
