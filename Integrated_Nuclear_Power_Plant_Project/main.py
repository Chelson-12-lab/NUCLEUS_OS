"""
Integrated Nuclear Power Plant Management System
Class XII CBSE Project
Python + MySQL + Tkinter + Matplotlib

IMPORTANT:
This is an educational management-system simulation. It does not control
real nuclear equipment, reactors, radiation systems, or emergency systems.
All sensor/reactor values are simulated records entered into the database.
"""

import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import mysql.connector

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


# ============================================================
# 1. DATABASE CONNECTION
# ============================================================

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
    return mysql.connector.connect(**DB_CONFIG)

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def execute_query(sql, values=(), fetch=False, many=False):
    con = get_connection()
    cur = con.cursor()
    try:
        if many:
            cur.executemany(sql, values)
        else:
            cur.execute(sql, values)

        if fetch:
            return cur.fetchall(), cur.column_names

        con.commit()
        return cur.lastrowid
    finally:
        cur.close()
        con.close()


# ============================================================
# 2. TABLE CONFIGURATION
# ============================================================

TABLES = {
    "Plants": {
        "table": "plants",
        "title": "Nuclear Power Plant Management",
        "columns": ["plant_id", "plant_name", "location"],
        "editable": ["plant_name", "location"],
    },
    "Reactors": {
        "table": "reactors",
        "title": "Reactor Management",
        "columns": ["reactor_id", "plant_id", "reactor_type",
                    "capacity", "operating_status"],
        "editable": ["plant_id", "reactor_type", "capacity",
                     "operating_status"],
    },
    "Power Generation": {
        "table": "power_generation",
        "title": "Power Generation",
        "columns": ["generation_id", "reactor_id", "generation_date",
                    "electricity_generated", "efficiency"],
        "editable": ["reactor_id", "generation_date",
                     "electricity_generated", "efficiency"],
    },
    "Fuel Management": {
        "table": "fuel",
        "title": "Nuclear Fuel Management",
        "columns": ["fuel_id", "reactor_id", "fuel_type",
                    "stock_percentage", "usage_date", "replacement_date"],
        "editable": ["reactor_id", "fuel_type", "stock_percentage",
                     "usage_date", "replacement_date"],
    },
    "Fuel Rod Tracking": {
        "table": "fuel_rods",
        "title": "Fuel Rod Tracking",
        "columns": ["rod_id", "reactor_id", "installation_date",
                    "remaining_life_months", "status"],
        "editable": ["reactor_id", "installation_date",
                     "remaining_life_months", "status"],
    },
    "Radioactive Waste": {
        "table": "radioactive_waste",
        "title": "Radioactive Waste Management",
        "columns": ["waste_id", "waste_category", "radiation_level",
                    "storage_id", "registration_date", "status"],
        "editable": ["waste_category", "radiation_level",
                     "storage_id", "registration_date", "status"],
    },
    "Waste Storage": {
        "table": "waste_storage",
        "title": "Waste Storage Facility",
        "columns": ["storage_id", "building_name", "capacity",
                    "used_capacity", "last_inspection", "status"],
        "editable": ["building_name", "capacity", "used_capacity",
                     "last_inspection", "status"],
    },
    "Radiation Monitoring": {
        "table": "radiation_monitoring",
        "title": "Radiation Monitoring (Simulated)",
        "columns": ["reading_id", "sensor_id", "area_name",
                    "reading_date", "radiation_reading", "alert_status"],
        "editable": ["sensor_id", "area_name", "reading_date",
                     "radiation_reading", "alert_status"],
    },
    "Employees": {
        "table": "employees",
        "title": "Employee Management",
        "columns": ["employee_id", "name", "department_id",
                    "designation", "date_of_joining", "contact",
                    "shift", "qualification"],
        "editable": ["name", "department_id", "designation",
                     "date_of_joining", "contact", "shift",
                     "qualification"],
    },
    "Employee Exposure": {
        "table": "employee_exposure",
        "title": "Employee Radiation Exposure",
        "columns": ["exposure_id", "employee_id", "exposure_date",
                    "daily_exposure", "monthly_exposure", "safe_limit_status"],
        "editable": ["employee_id", "exposure_date", "daily_exposure",
                     "monthly_exposure", "safe_limit_status"],
    },
    "Equipment": {
        "table": "equipment",
        "title": "Equipment Management",
        "columns": ["equipment_id", "equipment_name", "equipment_type",
                    "status", "health_score", "spare_parts"],
        "editable": ["equipment_name", "equipment_type", "status",
                     "health_score", "spare_parts"],
    },
    "Maintenance": {
        "table": "maintenance",
        "title": "Maintenance Management",
        "columns": ["maintenance_id", "equipment_id", "engineer_id",
                    "scheduled_date", "cost", "completion_status"],
        "editable": ["equipment_id", "engineer_id", "scheduled_date",
                     "cost", "completion_status"],
    },
    "Safety Inspection": {
        "table": "safety_inspections",
        "title": "Safety Inspection",
        "columns": ["inspection_id", "inspection_date", "area_name",
                    "compliance_status", "safety_score", "recommendations"],
        "editable": ["inspection_date", "area_name", "compliance_status",
                     "safety_score", "recommendations"],
    },
    "Environment": {
        "table": "environment_monitoring",
        "title": "Environmental Monitoring",
        "columns": ["environment_id", "reading_date", "water_quality",
                    "air_quality", "soil_monitoring",
                    "outside_radiation"],
        "editable": ["reading_date", "water_quality", "air_quality",
                     "soil_monitoring", "outside_radiation"],
    },
    "Visitors & Security": {
        "table": "security_visitors",
        "title": "Visitor & Security",
        "columns": ["visitor_id", "visitor_name", "visit_date",
                    "entry_time", "exit_time", "security_clearance",
                    "restricted_access"],
        "editable": ["visitor_name", "visit_date", "entry_time",
                     "exit_time", "security_clearance",
                     "restricted_access"],
    },
    "Emergency Response": {
        "table": "emergency_incidents",
        "title": "Emergency Response Records",
        "columns": ["incident_id", "incident_date", "incident_type",
                    "emergency_level", "evacuation_status",
                    "rescue_team"],
        "editable": ["incident_date", "incident_type", "emergency_level",
                     "evacuation_status", "rescue_team"],
    },
    "Inventory & Purchase": {
        "table": "inventory",
        "title": "Inventory & Purchase",
        "columns": ["item_id", "item_name", "category",
                    "quantity", "reorder_level", "supplier"],
        "editable": ["item_name", "category", "quantity",
                     "reorder_level", "supplier"],
    },
    "Departments": {
        "table": "departments",
        "title": "Department Management",
        "columns": ["department_id", "department_name", "manager"],
        "editable": ["department_name", "manager"],
    },
    "Job Vacancies": {
        "table": "job_vacancies",
        "title": "Career Portal - Job Opportunities",
        "columns": ["job_id", "job_title", "department_id",
                    "qualification", "experience_years",
                    "salary_min", "salary_max", "vacancies",
                    "closing_date", "status"],
        "editable": ["job_title", "department_id", "qualification",
                     "experience_years", "salary_min", "salary_max",
                     "vacancies", "closing_date", "status"],
    },
    "Candidates": {
        "table": "candidates",
        "title": "Career Portal - Candidates",
        "columns": ["candidate_id", "name", "qualification",
                    "experience_years", "contact", "email"],
        "editable": ["name", "qualification", "experience_years",
                     "contact", "email"],
    },
    "Applications": {
        "table": "job_applications",
        "title": "Career Portal - Applications",
        "columns": ["application_id", "candidate_id", "job_id",
                    "application_date", "application_status",
                    "interview_date", "final_selection"],
        "editable": ["candidate_id", "job_id", "application_date",
                     "application_status", "interview_date",
                     "final_selection"],
    },
    "Payroll": {
        "table": "payroll",
        "title": "Payroll Management",
        "columns": ["payroll_id", "employee_id", "pay_month",
                    "basic_salary", "allowances", "risk_allowance",
                    "overtime", "bonus", "income_tax", "provident_fund",
                    "medical_insurance", "deductions", "net_salary"],
        "editable": ["employee_id", "pay_month", "basic_salary",
                     "allowances", "risk_allowance", "overtime",
                     "bonus", "income_tax", "provident_fund",
                     "medical_insurance", "deductions", "net_salary"],
    },
    "Promotions": {
        "table": "promotions",
        "title": "Promotion Management",
        "columns": ["promotion_id", "employee_id", "promotion_date",
                    "years_of_service", "performance_rating",
                    "training_completed", "old_designation",
                    "new_designation"],
        "editable": ["employee_id", "promotion_date",
                     "years_of_service", "performance_rating",
                     "training_completed", "old_designation",
                     "new_designation"],
    },
    "Attendance": {
        "table": "attendance",
        "title": "Attendance Management",
        "columns": ["attendance_id", "employee_id", "attendance_date",
                    "status", "shift", "night_shift"],
        "editable": ["employee_id", "attendance_date", "status",
                     "shift", "night_shift"],
    },
    "Performance": {
        "table": "performance",
        "title": "Performance Evaluation",
        "columns": ["performance_id", "employee_id", "evaluation_month",
                    "rating", "supervisor_comments", "awards",
                    "improvement_areas"],
        "editable": ["employee_id", "evaluation_month", "rating",
                     "supervisor_comments", "awards",
                     "improvement_areas"],
    },
    "Training": {
        "table": "training",
        "title": "Training & Certification",
        "columns": ["training_id", "employee_id", "training_type",
                    "training_date", "certificate_no", "status"],
        "editable": ["employee_id", "training_type", "training_date",
                     "certificate_no", "status"],
    },
    "Retirement": {
        "table": "retirement",
        "title": "Retirement Management",
        "columns": ["retirement_id", "employee_id", "retirement_date",
                    "pension_details", "service_years"],
        "editable": ["employee_id", "retirement_date",
                     "pension_details", "service_years"],
    },
    "Awards": {
        "table": "employee_awards",
        "title": "Employee Awards",
        "columns": ["award_id", "employee_id", "award_name",
                    "award_date", "certificate_no", "reward"],
        "editable": ["employee_id", "award_name", "award_date",
                     "certificate_no", "reward"],
    },
    "Leave Management": {
        "table": "leave_records",
        "title": "Leave Management",
        "columns": ["leave_id", "employee_id", "leave_type",
                    "start_date", "end_date", "reason",
                    "approval_status"],
        "editable": ["employee_id", "leave_type", "start_date",
                     "end_date", "reason", "approval_status"],
    },
}


# ============================================================
# 3. APPLICATION
# ============================================================

class NuclearApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Integrated Nuclear Power Plant Management System")
        self.geometry("1250x760")
        self.minsize(1050, 650)

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("TLabel", font=("Segoe UI", 10))

        self.current_user = None
        self.show_login()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()

        canvas = tk.Canvas(self, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Attractive simulated-tech background
        self._draw_background(canvas)

        card = tk.Frame(canvas, bg="#101827", bd=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=470, height=480)

        tk.Label(card, text="☢", font=("Segoe UI Symbol", 48),
                 fg="#8be9fd", bg="#101827").pack(pady=(25, 0))

        tk.Label(card, text="NUCLEAR POWER PLANT",
                 font=("Segoe UI", 21, "bold"),
                 fg="white", bg="#101827").pack()

        tk.Label(card, text="INTEGRATED MANAGEMENT SYSTEM",
                 font=("Segoe UI", 11),
                 fg="#8be9fd", bg="#101827").pack(pady=(0, 25))

        tk.Label(card, text="Username", fg="#d7e3f4", bg="#101827",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=55)
        self.login_user = tk.Entry(card, font=("Segoe UI", 12),
                                   bg="#182438", fg="white",
                                   insertbackground="white", relief="flat")
        self.login_user.pack(fill="x", padx=55, ipady=9, pady=(5, 15))

        tk.Label(card, text="Password", fg="#d7e3f4", bg="#101827",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=55)
        self.login_pass = tk.Entry(card, show="*", font=("Segoe UI", 12),
                                   bg="#182438", fg="white",
                                   insertbackground="white", relief="flat")
        self.login_pass.pack(fill="x", padx=55, ipady=9, pady=(5, 20))

        tk.Button(card, text="LOGIN", command=self.do_login,
                  bg="#238636", fg="white", activebackground="#2ea043",
                  activeforeground="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), cursor="hand2"
                  ).pack(fill="x", padx=55, ipady=10)

        tk.Label(card, text="Educational simulation • Python + MySQL",
                 fg="#8190a5", bg="#101827",
                 font=("Segoe UI", 9)).pack(pady=25)

        self.login_user.focus_set()
        self.bind("<Return>", lambda e: self.do_login())

    def _draw_background(self, canvas):
        width = max(self.winfo_width(), 1100)
        height = max(self.winfo_height(), 650)
        canvas.configure(bg="#07111f")

        # Decorative grid
        for x in range(0, width, 50):
            canvas.create_line(x, 0, x, height, fill="#0e2235")
        for y in range(0, height, 50):
            canvas.create_line(0, y, width, y, fill="#0e2235")

        # Reactor-like rings
        cx, cy = 170, 170
        for r in (55, 90, 125):
            canvas.create_oval(cx-r, cy-r, cx+r, cy+r,
                               outline="#173c57", width=2)
        canvas.create_oval(cx-20, cy-20, cx+20, cy+20,
                           outline="#8be9fd", width=3)

        # Decorative data lines
        for i in range(6):
            y = 500 + i * 25
            canvas.create_line(40, y, 330, y, fill="#173c57", width=2)

        # Right-side panels
        for i in range(5):
            x = width - 300
            y = 80 + i * 95
            canvas.create_rectangle(x, y, x+220, y+55,
                                    outline="#173c57", width=2)

    def do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get()

        if not username or not password:
            messagebox.showwarning("Login", "Enter username and password.")
            return

        try:
            rows, _ = execute_query(
                """SELECT user_id, username, role
                   FROM users
                   WHERE username=%s AND password_hash=%s""",
                (username, hash_password(password)),
                fetch=True
            )
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Database Error",
                "Could not connect to MySQL.\n\n" + str(err)
            )
            return

        if rows:
            self.current_user = {
                "id": rows[0][0],
                "username": rows[0][1],
                "role": rows[0][2]
            }
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed",
                                 "Invalid username or password.")

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    def show_dashboard(self):
        self.clear_window()

        root = tk.Frame(self, bg="#f2f6fb")
        root.pack(fill="both", expand=True)

        sidebar = tk.Frame(root, bg="#0b1726", width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="☢", font=("Segoe UI Symbol", 38),
                 fg="#8be9fd", bg="#0b1726").pack(pady=(20, 0))
        tk.Label(sidebar, text="NUCLEAR PMS", font=("Segoe UI", 17, "bold"),
                 fg="white", bg="#0b1726").pack()
        tk.Label(sidebar, text="Management System",
                 font=("Segoe UI", 9), fg="#8aa0b7",
                 bg="#0b1726").pack(pady=(0, 15))

        tk.Label(sidebar, text=f"{self.current_user['username']}\n"
                 f"{self.current_user['role']}",
                 font=("Segoe UI", 10, "bold"), fg="#d7e3f4",
                 bg="#122235", justify="center").pack(
                     fill="x", padx=15, pady=(0, 15), ipady=8)

        btn_frame = tk.Frame(sidebar, bg="#0b1726")
        btn_frame.pack(fill="both", expand=True)

        modules = [
            ("⌂  Dashboard", self.dashboard_home),
            ("▣  Plant Management", lambda: self.open_table("Plants")),
            ("⚙  Reactor Management", lambda: self.open_table("Reactors")),
            ("⚡ Power Generation", lambda: self.open_table("Power Generation")),
            ("◈  Fuel Management", lambda: self.open_table("Fuel Management")),
            ("●  Fuel Rod Tracking", lambda: self.open_table("Fuel Rod Tracking")),
            ("☣  Radioactive Waste", lambda: self.open_table("Radioactive Waste")),
            ("▤  Waste Storage", lambda: self.open_table("Waste Storage")),
            ("◉  Radiation Monitoring", lambda: self.open_table("Radiation Monitoring")),
            ("♙  Employees", lambda: self.open_table("Employees")),
            ("△  Employee Exposure", lambda: self.open_table("Employee Exposure")),
            ("▤  Equipment", lambda: self.open_table("Equipment")),
            ("🔧 Maintenance", lambda: self.open_table("Maintenance")),
            ("✓  Safety Inspection", lambda: self.open_table("Safety Inspection")),
            ("♣  Environment", lambda: self.open_table("Environment")),
            ("▥  Security & Visitors", lambda: self.open_table("Visitors & Security")),
            ("⚠  Emergency Response", lambda: self.open_table("Emergency Response")),
            ("▦  Inventory & Purchase", lambda: self.open_table("Inventory & Purchase")),
            ("🏢 Departments", lambda: self.open_table("Departments")),
            ("💼 Job Vacancies", lambda: self.open_table("Job Vacancies")),
            ("👤 Candidates", lambda: self.open_table("Candidates")),
            ("📄 Applications", lambda: self.open_table("Applications")),
            ("💰 Payroll", lambda: self.open_table("Payroll")),
            ("↗  Promotions", lambda: self.open_table("Promotions")),
            ("☷  Attendance", lambda: self.open_table("Attendance")),
            ("★  Performance", lambda: self.open_table("Performance")),
            ("🎓 Training", lambda: self.open_table("Training")),
            ("🏅 Awards", lambda: self.open_table("Awards")),
            ("✚  Leave Management", lambda: self.open_table("Leave Management")),
            ("📊 Analytics & Reports", self.analytics_page),
            ("🧠 Decision Support", self.decision_support_page),
        ]

        # Canvas scrollbar for many modules
        nav_canvas = tk.Canvas(btn_frame, bg="#0b1726",
                               highlightthickness=0)
        scrollbar = ttk.Scrollbar(btn_frame, orient="vertical",
                                  command=nav_canvas.yview)
        nav_inner = tk.Frame(nav_canvas, bg="#0b1726")

        nav_inner.bind(
            "<Configure>",
            lambda e: nav_canvas.configure(
                scrollregion=nav_canvas.bbox("all"))
        )
        nav_canvas.create_window((0, 0), window=nav_inner, anchor="nw")
        nav_canvas.configure(yscrollcommand=scrollbar.set)

        nav_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for text, command in modules:
            tk.Button(
                nav_inner, text=text, command=command,
                anchor="w", bg="#0b1726", fg="#d7e3f4",
                activebackground="#173c57", activeforeground="#8be9fd",
                relief="flat", bd=0, font=("Segoe UI", 9),
                cursor="hand2"
            ).pack(fill="x", padx=8, pady=2, ipady=5)

        tk.Button(sidebar, text="LOG OUT", command=self.show_login,
                  bg="#8b2635", fg="white", activebackground="#a52a3b",
                  relief="flat", font=("Segoe UI", 9, "bold"),
                  cursor="hand2").pack(fill="x", padx=15, pady=12, ipady=7)

        self.content = tk.Frame(root, bg="#f2f6fb")
        self.content.pack(side="right", fill="both", expand=True)

        self.dashboard_home()

    def dashboard_home(self):
        for w in self.content.winfo_children():
            w.destroy()

        top = tk.Frame(self.content, bg="#f2f6fb")
        top.pack(fill="x", padx=28, pady=25)

        tk.Label(top, text="System Dashboard",
                 font=("Segoe UI", 25, "bold"),
                 bg="#f2f6fb", fg="#14243a").pack(anchor="w")
        tk.Label(top, text="Centralized plant, safety and human-resource management",
                 font=("Segoe UI", 11), bg="#f2f6fb",
                 fg="#617389").pack(anchor="w", pady=3)

        cards = tk.Frame(self.content, bg="#f2f6fb")
        cards.pack(fill="x", padx=28)

        stats = [
            ("Plants", "plants"),
            ("Reactors", "reactors"),
            ("Employees", "employees"),
            ("Equipment", "equipment"),
            ("Waste Records", "radioactive_waste"),
        ]

        for i, (label, table) in enumerate(stats):
            count = "—"
            try:
                rows, _ = execute_query(
                    f"SELECT COUNT(*) FROM {table}", fetch=True)
                count = str(rows[0][0])
            except Exception:
                pass

            card = tk.Frame(cards, bg="white", bd=0,
                            highlightthickness=1,
                            highlightbackground="#d8e1ec")
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=count, font=("Segoe UI", 24, "bold"),
                     bg="white", fg="#183b56").pack(pady=(16, 2))
            tk.Label(card, text=label, font=("Segoe UI", 10),
                     bg="white", fg="#66788a").pack(pady=(0, 15))

        info = tk.Frame(self.content, bg="white",
                        highlightthickness=1,
                        highlightbackground="#d8e1ec")
        info.pack(fill="both", expand=True, padx=28, pady=22)

        tk.Label(info, text="Project Scope",
                 font=("Segoe UI", 17, "bold"), bg="white",
                 fg="#14243a").pack(anchor="w", padx=25, pady=(22, 8))

        scope = (
            "This educational application combines 25 management modules "
            "using Python and MySQL. It covers plant records, reactor and "
            "power-generation records, simulated radiation and waste data, "
            "equipment and maintenance, safety, environment, security, "
            "emergency records, HR, recruitment, payroll, promotions, "
            "attendance, training, awards and leave management."
        )
        tk.Label(info, text=scope, wraplength=850, justify="left",
                 font=("Segoe UI", 11), bg="white",
                 fg="#536577").pack(anchor="w", padx=25)

        tk.Label(info, text="Educational safety note",
                 font=("Segoe UI", 13, "bold"), bg="white",
                 fg="#8b2635").pack(anchor="w", padx=25, pady=(25, 5))
        tk.Label(
            info,
            text=("Reactor, radiation and emergency values in this project "
                  "are simulated records. The software is a database and "
                  "decision-support demonstration, not a real plant-control system."),
            wraplength=850, justify="left", font=("Segoe UI", 10),
            bg="white", fg="#536577"
        ).pack(anchor="w", padx=25)

    # --------------------------------------------------------
    # GENERIC CRUD TABLE PAGE
    # --------------------------------------------------------

    def open_table(self, module_name):
        config = TABLES[module_name]
        for w in self.content.winfo_children():
            w.destroy()

        header = tk.Frame(self.content, bg="#f2f6fb")
        header.pack(fill="x", padx=25, pady=(22, 10))

        tk.Label(header, text=config["title"],
                 font=("Segoe UI", 21, "bold"),
                 bg="#f2f6fb", fg="#14243a").pack(side="left")

        tk.Button(header, text="Refresh",
                  command=lambda: self.load_table(tree, config),
                  bg="#173c57", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="right")

        toolbar = tk.Frame(self.content, bg="#f2f6fb")
        toolbar.pack(fill="x", padx=25, pady=5)

        tk.Label(toolbar, text="Search:", bg="#f2f6fb",
                 fg="#45586d").pack(side="left")
        search = tk.Entry(toolbar, width=35, font=("Segoe UI", 10))
        search.pack(side="left", padx=8, ipady=5)

        tree_frame = tk.Frame(self.content, bg="white")
        tree_frame.pack(fill="both", expand=True, padx=25, pady=10)

        cols = config["columns"]
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")

        vs = ttk.Scrollbar(tree_frame, orient="vertical",
                           command=tree.yview)
        hs = ttk.Scrollbar(tree_frame, orient="horizontal",
                           command=tree.xview)
        tree.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)

        for col in cols:
            tree.heading(col, text=col.replace("_", " ").title())
            tree.column(col, width=max(110, min(180, len(col) * 12)))

        tree.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        buttons = tk.Frame(self.content, bg="#f2f6fb")
        buttons.pack(fill="x", padx=25, pady=(0, 18))

        tk.Button(buttons, text="Add Record",
                  command=lambda: self.record_form(config, tree, None),
                  bg="#238636", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        tk.Button(buttons, text="Edit Selected",
                  command=lambda: self.edit_selected(config, tree),
                  bg="#1769aa", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        tk.Button(buttons, text="Delete Selected",
                  command=lambda: self.delete_selected(config, tree),
                  bg="#8b2635", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        tk.Button(buttons, text="View All",
                  command=lambda: self.load_table(tree, config),
                  bg="#5f6b7a", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="left", padx=4)

        def do_search():
            term = search.get().strip()
            if not term:
                self.load_table(tree, config)
                return
            # Search all columns by converting row values to text.
            sql = f"SELECT {', '.join(cols)} FROM {config['table']}"
            try:
                rows, _ = execute_query(sql, fetch=True)
                tree.delete(*tree.get_children())
                for row in rows:
                    if term.lower() in " ".join(str(v) for v in row).lower():
                        tree.insert("", "end", values=row)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", str(err))

        tk.Button(toolbar, text="Search", command=do_search,
                  bg="#173c57", fg="white", relief="flat",
                  font=("Segoe UI", 9, "bold")).pack(side="left")

        self.load_table(tree, config)

    def load_table(self, tree, config):
        try:
            rows, _ = execute_query(
                f"SELECT {', '.join(config['columns'])} "
                f"FROM {config['table']} ORDER BY 1 DESC",
                fetch=True
            )
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", "end", values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    def edit_selected(self, config, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Edit", "Select a record first.")
            return
        values = tree.item(selected[0], "values")
        self.record_form(config, tree, values)

    def delete_selected(self, config, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Delete", "Select a record first.")
            return

        values = tree.item(selected[0], "values")
        pk = config["columns"][0]

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete {config['table']} record {values[0]}?"
        ):
            return

        try:
            execute_query(
                f"DELETE FROM {config['table']} WHERE {pk}=%s",
                (values[0],)
            )
            self.load_table(tree, config)
        except mysql.connector.Error as err:
            messagebox.showerror(
                "Delete Failed",
                "The record may be referenced by another table.\n\n" + str(err)
            )

    def record_form(self, config, tree, existing):
        form = tk.Toplevel(self)
        form.title(("Edit " if existing else "Add ") + config["title"])
        form.geometry("620x650")
        form.configure(bg="#f2f6fb")
        form.transient(self)
        form.grab_set()

        tk.Label(form, text=("Edit Record" if existing else "Add Record"),
                 font=("Segoe UI", 18, "bold"),
                 bg="#f2f6fb", fg="#14243a").pack(pady=18)

        frame = tk.Frame(form, bg="white")
        frame.pack(fill="both", expand=True, padx=25, pady=10)

        entries = {}
        editable = config["editable"]

        for r, col in enumerate(editable):
            tk.Label(frame, text=col.replace("_", " ").title(),
                     bg="white", fg="#45586d",
                     font=("Segoe UI", 10, "bold")).grid(
                         row=r, column=0, sticky="w", padx=20, pady=8)

            ent = tk.Entry(frame, font=("Segoe UI", 10))
            ent.grid(row=r, column=1, sticky="ew", padx=20, pady=8,
                     ipady=5)
            frame.grid_columnconfigure(1, weight=1)
            entries[col] = ent

            if existing:
                index = config["columns"].index(col)
                ent.insert(0, str(existing[index]))

        def save():
            values = [entries[c].get().strip() for c in editable]

            if any(v == "" for v in values):
                messagebox.showwarning(
                    "Input", "Please fill all editable fields.", parent=form)
                return

            try:
                if existing:
                    assignments = ", ".join(f"{c}=%s" for c in editable)
                    sql = (f"UPDATE {config['table']} SET {assignments} "
                           f"WHERE {config['columns'][0]}=%s")
                    execute_query(sql, tuple(values) + (existing[0],))
                else:
                    columns = ", ".join(editable)
                    placeholders = ", ".join(["%s"] * len(values))
                    sql = (f"INSERT INTO {config['table']} "
                           f"({columns}) VALUES ({placeholders})")
                    execute_query(sql, tuple(values))

                form.destroy()
                self.load_table(tree, config)

            except mysql.connector.Error as err:
                messagebox.showerror(
                    "Database Error", str(err), parent=form)

        tk.Button(form, text="SAVE", command=save,
                  bg="#238636", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold")).pack(
                      side="left", padx=30, pady=18, ipadx=25, ipady=7)

        tk.Button(form, text="CANCEL", command=form.destroy,
                  bg="#687386", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold")).pack(
                      side="right", padx=30, pady=18, ipadx=20, ipady=7)

    # --------------------------------------------------------
    # ANALYTICS
    # --------------------------------------------------------

    def analytics_page(self):
        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(self.content, text="Analytics & Reports",
                 font=("Segoe UI", 22, "bold"),
                 bg="#f2f6fb", fg="#14243a").pack(
                     anchor="w", padx=25, pady=(22, 5))

        tk.Label(self.content,
                 text="Charts are generated from records stored in MySQL.",
                 bg="#f2f6fb", fg="#617389").pack(
                     anchor="w", padx=25)

        if not MATPLOTLIB_OK:
            tk.Label(
                self.content,
                text="Matplotlib is not installed. Run: py -m pip install matplotlib",
                bg="#f2f6fb", fg="#8b2635",
                font=("Segoe UI", 11, "bold")
            ).pack(pady=30)
            return

        buttons = tk.Frame(self.content, bg="#f2f6fb")
        buttons.pack(fill="x", padx=25, pady=15)

        tk.Button(buttons, text="Power Generation Trend",
                  command=lambda: self.make_chart("power"),
                  bg="#173c57", fg="white", relief="flat").pack(
                      side="left", padx=5)
        tk.Button(buttons, text="Waste Trend",
                  command=lambda: self.make_chart("waste"),
                  bg="#173c57", fg="white", relief="flat").pack(
                      side="left", padx=5)
        tk.Button(buttons, text="Employee Departments",
                  command=lambda: self.make_chart("employees"),
                  bg="#173c57", fg="white", relief="flat").pack(
                      side="left", padx=5)
        tk.Button(buttons, text="Equipment Health",
                  command=lambda: self.make_chart("equipment"),
                  bg="#173c57", fg="white", relief="flat").pack(
                      side="left", padx=5)

        self.chart_frame = tk.Frame(self.content, bg="white")
        self.chart_frame.pack(fill="both", expand=True, padx=25, pady=10)

    def make_chart(self, kind):
        for w in self.chart_frame.winfo_children():
            w.destroy()

        fig = Figure(figsize=(8, 4.8), dpi=100)
        ax = fig.add_subplot(111)

        try:
            if kind == "power":
                rows, _ = execute_query(
                    """SELECT generation_date,
                              electricity_generated
                       FROM power_generation
                       ORDER BY generation_date""",
                    fetch=True
                )
                if not rows:
                    raise ValueError("No power-generation data available.")
                x = [str(r[0]) for r in rows]
                y = [float(r[1]) for r in rows]
                ax.plot(x, y, marker="o")
                ax.set_title("Power Generation Trend")
                ax.set_ylabel("Electricity Generated")

            elif kind == "waste":
                rows, _ = execute_query(
                    """SELECT registration_date, COUNT(*)
                       FROM radioactive_waste
                       GROUP BY registration_date
                       ORDER BY registration_date""",
                    fetch=True
                )
                if not rows:
                    raise ValueError("No waste data available.")
                x = [str(r[0]) for r in rows]
                y = [int(r[1]) for r in rows]
                ax.bar(x, y)
                ax.set_title("Waste Registration Trend")
                ax.set_ylabel("Number of Records")

            elif kind == "employees":
                rows, _ = execute_query(
                    """SELECT d.department_name, COUNT(e.employee_id)
                       FROM departments d
                       LEFT JOIN employees e
                       ON d.department_id=e.department_id
                       GROUP BY d.department_id, d.department_name
                       ORDER BY d.department_name""",
                    fetch=True
                )
                if not rows:
                    raise ValueError("No department data available.")
                x = [str(r[0]) for r in rows]
                y = [int(r[1]) for r in rows]
                ax.bar(x, y)
                ax.set_title("Employees by Department")
                ax.set_ylabel("Employees")
                ax.tick_params(axis="x", rotation=45)

            else:
                rows, _ = execute_query(
                    """SELECT equipment_name, health_score
                       FROM equipment ORDER BY equipment_id""",
                    fetch=True
                )
                if not rows:
                    raise ValueError("No equipment data available.")
                x = [str(r[0]) for r in rows]
                y = [float(r[1]) for r in rows]
                ax.bar(x, y)
                ax.set_title("Equipment Health Score")
                ax.set_ylabel("Health Score")
                ax.tick_params(axis="x", rotation=45)

            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except (mysql.connector.Error, ValueError) as err:
            messagebox.showinfo("Report", str(err))

    # --------------------------------------------------------
    # DECISION SUPPORT
    # --------------------------------------------------------

    def decision_support_page(self):
        for w in self.content.winfo_children():
            w.destroy()

        tk.Label(self.content, text="Intelligent Decision Support System",
                 font=("Segoe UI", 22, "bold"),
                 bg="#f2f6fb", fg="#14243a").pack(
                     anchor="w", padx=25, pady=(22, 5))

        tk.Label(
            self.content,
            text=("Rule-based educational decision support. "
                  "It evaluates simulated database records and produces "
                  "management recommendations; it does not control real equipment."),
            bg="#f2f6fb", fg="#617389", wraplength=850,
            justify="left"
        ).pack(anchor="w", padx=25)

        output = tk.Text(self.content, font=("Consolas", 11),
                         bg="#101827", fg="#d7e3f4",
                         insertbackground="white", relief="flat")
        output.pack(fill="both", expand=True, padx=25, pady=18)

        def run_rules():
            output.delete("1.0", "end")
            messages = []

            try:
                rows, _ = execute_query(
                    "SELECT AVG(radiation_reading) FROM radiation_monitoring",
                    fetch=True
                )
                avg_rad = float(rows[0][0] or 0)
                if avg_rad > 5:
                    messages.append(
                        "SIMULATED ALERT: Radiation average is above "
                        "the demonstration threshold. Review the record "
                        "and follow the plant's approved safety procedure."
                    )
                else:
                    messages.append(
                        "Radiation rule: No demonstration threshold exceeded."
                    )

                rows, _ = execute_query(
                    """SELECT building_name,
                              (used_capacity / NULLIF(capacity,0))*100
                       FROM waste_storage""",
                    fetch=True
                )
                for name, pct in rows:
                    if pct is not None and float(pct) > 90:
                        messages.append(
                            f"Storage rule: {name} is above 90% simulated "
                            "capacity. Plan a storage review."
                        )

                rows, _ = execute_query(
                    "SELECT AVG(stock_percentage) FROM fuel",
                    fetch=True
                )
                avg_fuel = float(rows[0][0] or 0)
                if avg_fuel < 15:
                    messages.append(
                        "Fuel rule: Average fuel stock is below 15%. "
                        "Schedule a planned refueling review."
                    )

                rows, _ = execute_query(
                    """SELECT equipment_name
                       FROM equipment
                       WHERE health_score < 40""",
                    fetch=True
                )
                for (name,) in rows:
                    messages.append(
                        f"Equipment rule: {name} has a low simulated "
                        "health score. Create a maintenance review."
                    )

                rows, _ = execute_query(
                    """SELECT e.name
                       FROM employees e
                       JOIN employee_exposure x
                       ON e.employee_id=x.employee_id
                       WHERE x.monthly_exposure > 20""",
                    fetch=True
                )
                for (name,) in rows:
                    messages.append(
                        f"Exposure rule: Review radiation-zone assignment "
                        f"for {name} according to approved safety procedures."
                    )

                rows, _ = execute_query(
                    """SELECT equipment_name
                       FROM equipment
                       WHERE status='Maintenance Overdue'""",
                    fetch=True
                )
                for (name,) in rows:
                    messages.append(
                        f"Maintenance rule: {name} is overdue. "
                        "Generate a maintenance work order."
                    )

                rows, _ = execute_query(
                    """SELECT reactor_id
                       FROM reactors
                       WHERE operating_status='High Temperature (Simulated)'""",
                    fetch=True
                )
                for (rid,) in rows:
                    messages.append(
                        f"Reactor rule: Reactor {rid} has a simulated "
                        "high-temperature status. Review the approved "
                        "controlled-shutdown procedure."
                    )

                if not messages:
                    messages.append("No rule-based recommendations at present.")

            except mysql.connector.Error as err:
                messages.append("Database error: " + str(err))

            output.insert("end", "\n\n".join(
                "• " + m for m in messages
            ))

        tk.Button(self.content, text="RUN DECISION SUPPORT",
                  command=run_rules, bg="#6b46c1", fg="white",
                  relief="flat", font=("Segoe UI", 10, "bold")
                  ).pack(pady=(0, 20), ipadx=15, ipady=7)

        run_rules()


# ============================================================
# 4. START APPLICATION
# ============================================================

if __name__ == "__main__":
    app = NuclearApp()
    app.mainloop()
