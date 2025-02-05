import sqlite3
import tkinter as tk
from tkinter import messagebox
from main import *

# Database setup
def init_db():
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    date TEXT,
                    doctor_id INTEGER,
                    FOREIGN KEY (doctor_id) REFERENCES users (id)
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS exercises (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER,
                    exercise TEXT,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                 )''')

    conn.commit()
    conn.close()

# Global variables
current_user = None

# Helper functions
def authenticate(username, password, role):
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()

    c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', (username, password, role))
    user = c.fetchone()
    conn.close()
    return user

def register_user(username, password, role):
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()

    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, role))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists!")
    conn.close()

def register_doctor():
    register_window = tk.Toplevel()
    register_window.title("Register Doctor")
    screen_width = register_window.winfo_screenwidth()
    screen_height = register_window.winfo_screenheight()
    register_window.geometry(f"{screen_width}x{screen_height}")
    register_window.configure(bg="#C5EBE8")
    def submit():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Register the doctor in the database
        register_user(username, password, "doctor")
        register_window.destroy()

    def go_to_login():
        register_window.destroy()
        doctor_login()

    # Title Label
    title_label = tk.Label(
        register_window,
        text="Doctor Registration",
        font=("Arial", 20, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=(30, 10))

    # Username Label and Entry
    tk.Label(
        register_window,
        text="Username",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    ).pack(pady=(10, 5))

    username_entry = tk.Entry(
        register_window,
        font=("Arial", 14),
        width=30
    )
    username_entry.pack(pady=5)

    # Password Label and Entry
    tk.Label(
        register_window,
        text="Password",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    ).pack(pady=(10, 5))

    password_entry = tk.Entry(
        register_window,
        font=("Arial", 14),
        width=30,
        show="*"
    )
    password_entry.pack(pady=5)

    # Submit Button
    tk.Button(
        register_window,
        text="Register",
        command=submit,
        font=("Arial", 16),
        width=15,
        bg="#008878",
        fg="white"
    ).pack(pady=(20, 10))

    # Already have an account? Button
    tk.Button(
        register_window,
        text="Already have an account? Sign in",
        command=go_to_login,
        font=("Arial", 12),
        bg="#C5EBE8",
        fg="#008878",
        bd=0
    ).pack(pady=(10, 20))

#######
def patient_login():
    login_window = tk.Toplevel()
    login_window.title("Patient Login")
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    login_window.geometry(f"{screen_width}x{screen_height}")
    login_window.configure(bg="#C5EBE8")
    

    # Add title label
    title_label = tk.Label(
        login_window,
        text="Patient Login",
        font=("Arial", 20, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=(30, 10))

    # Add username label and entry
    username_label = tk.Label(
        login_window,
        text="Username",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    username_label.pack(pady=(10, 5))
    username_entry = tk.Entry(login_window, font=("Arial", 14))
    username_entry.pack(pady=(0, 20))

    # Add password label and entry
    password_label = tk.Label(
        login_window,
        text="Password",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    password_label.pack(pady=(10, 5))
    password_entry = tk.Entry(login_window, show="*", font=("Arial", 14))
    password_entry.pack(pady=(0, 20))

    # Add login button
    def submit():
        username = username_entry.get()
        password = password_entry.get()
        user = authenticate(username, password, 'patient')

        if user:
            global current_user
            current_user = user
             # Fetch patient ID based on user
            with sqlite3.connect('hospital.db') as conn:
                c = conn.cursor()
                c.execute("SELECT id FROM patients WHERE name = ?", (username,))
                patient_data = c.fetchone()
                if patient_data:
                    current_user = (current_user[0], patient_data[0])  # Include patient ID
            print("Logged-in Patient:", current_user)
            display_patient_dashboard()
        else:
            messagebox.showerror("Error", "Wrong Username/Password!")

    login_button = tk.Button(
        login_window,
        text="Login",
        command=submit,
        font=("Arial", 16),
        bg="#008878",
        fg="white",
        width=20
    )
    login_button.pack(pady=20)

# GUI functions
def doctor_login():
    login_window = tk.Toplevel()
    login_window.title("Doctor Login")
    screen_width = login_window.winfo_screenwidth()
    screen_height = login_window.winfo_screenheight()
    login_window.geometry(f"{screen_width}x{screen_height}")
    login_window.configure(bg="#C5EBE8")

    # Add the title label
    title_label = tk.Label(
        login_window,
        text="Doctor Login",
        font=("Arial", 20, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=(30, 10))

    # Add the username label and entry
    username_label = tk.Label(
        login_window,
        text="Username",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    username_label.pack(pady=(10, 5))

    username_entry = tk.Entry(
        login_window,
        font=("Arial", 14),
        width=30
    )
    username_entry.pack(pady=5)

    # Add the password label and entry
    password_label = tk.Label(
        login_window,
        text="Password",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    password_label.pack(pady=(10, 5))

    password_entry = tk.Entry(
        login_window,
        font=("Arial", 14),
        width=30,
        show="*"
    )
    password_entry.pack(pady=5)

    # Add the login button
    login_button = tk.Button(
        login_window,
        text="Login",
        command=lambda: submit(username_entry.get(), password_entry.get()),
        font=("Arial", 16),
        width=15,
        bg="#008878",
        fg="white"
    )
    login_button.pack(pady=(20, 10))

    def submit(username, password):
        global current_user
        user = authenticate(username, password, 'doctor')

        if user:
            current_user = user
            display_doctor_dashboard()
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

# Dashboards
def display_patient_dashboard():
    dashboard = tk.Toplevel()
    dashboard.title("Patient Dashboard")
    dashboard.geometry("800x600")
    dashboard.configure(bg="#E0F7FA")

    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()

    # Use the correct patient ID
    patient_id = current_user[1]  # Assuming patient ID is stored in current_user[1]
    c.execute('''SELECT exercise FROM exercises WHERE patient_id = ?''', (patient_id,))
    exercises = c.fetchall()
    conn.close()

    print(f"Exercises for Patient ID {patient_id}: {exercises}")

    # Add title
    tk.Label(
        dashboard, 
        text="Your Exercises:", 
        font=("Arial", 18, "bold"),
        bg="#E0F7FA",
        fg="#00796B"
    ).pack(pady=20)

    # Check if exercises are retrieved
    if not exercises:
        tk.Label(
            dashboard,
            text="No exercises assigned.",
            font=("Arial", 14),
            bg="#E0F7FA",
            fg="#00796B"
        ).pack(pady=20)
        return

    # Generate buttons for each exercise
    for exercise in exercises:
        exercise_name = exercise[0]

        # Fetch the associated command and video path from main.py
        exercise_command = globals().get(f"start_{exercise_name.replace(' ', '_')}", None)
        video_path = exercise_videos.get(exercise_name, "")

        # Debugging: Print resolved values
        print(f"Exercise: {exercise_name}, Command: {exercise_command}, Video Path: {video_path}")
    
        if exercise_command and video_path:
            btn = tk.Button(
                dashboard,
                text=exercise_name,
                command=lambda c=exercise_command, v=video_path: show_instructional_video(dashboard, c, v, display_patient_dashboard),
                font=("Arial", 14),
                bg="#008878",
                fg="white",
                width=25
            )
            btn.pack(pady=10)
            """exercise_buttons[exercise_name]=btn"""
        else:
            print(f"Skipping exercise: {exercise_name} (Command or Video Path missing)")
        """if exercise_status[exercise_name]:
            update_button_state(exercise_name)"""
    
    """def update_button_state(Exercise):
            btn = exercise_buttons.get(Exercise)
            if btn and btn.winfo_exists():  # Ensure button exists
                btn["bg"] = "gray"
                btn["state"] = "disabled"""
            

    # Back button
    tk.Button(
        dashboard,
        text="Back",
        command=dashboard.destroy,
        font=("Arial", 14),
        bg="#00796B",
        fg="white",
        width=10
    ).pack(pady=20)


def display_doctor_dashboard():
    dashboard = tk.Toplevel()
    dashboard.title("Doctor Dashboard")
    screen_width = dashboard.winfo_screenwidth()
    screen_height = dashboard.winfo_screenheight()
    dashboard.geometry(f"{screen_width}x{screen_height}")
    dashboard.configure(bg="#E0F7FA")

    # Add a title label
    title_label = tk.Label(
        dashboard,
        text="Doctor Dashboard",
        font=("Arial", 20, "bold"),
        bg="#E0F7FA",
        fg="#00796B"
    )
    title_label.pack(pady=(30, 10))

    # Add instructions for the doctor
    instruction_text = tk.Label(
        dashboard,
        text="Manage your patients effectively with the options below:",
        font=("Arial", 14),
        bg="#E0F7FA",
        fg="#00796B",
        wraplength=700,
        justify="center"
    )
    instruction_text.pack(pady=(10, 20))

    # Add a button to add a new patient
    btn_add_patient = tk.Button(
        dashboard,
        text="Add Patient",
        command=lambda: add_patient(dashboard),
        font=("Arial", 16),
        width=20,
        bg="#00796B",
        fg="white"
    )
    btn_add_patient.pack(pady=20)

    # Add a button to view patient overview
    btn_patient_overview = tk.Button(
        dashboard,
        text="Patient Overview",
        command=lambda: patient_overview(dashboard),
        font=("Arial", 16),
        width=20,
        bg="#00796B",
        fg="white"
    )
    btn_patient_overview.pack(pady=20)

def add_patient(parent_window):
    add_patient_window = tk.Toplevel(parent_window)
    add_patient_window.title("Add Patient")
    screen_width = add_patient_window.winfo_screenwidth()
    screen_height = add_patient_window.winfo_screenheight()
    add_patient_window.geometry(f"{screen_width}x{screen_height}")
    add_patient_window.configure(bg="#E0F7FA")

    # Add form elements for patient name and age
    tk.Label(
        add_patient_window,
        text="Patient Name",
        font=("Arial", 14),
        bg="#E0F7FA"
    ).pack(pady=(10, 5))
    name_entry = tk.Entry(add_patient_window, font=("Arial", 14))
    name_entry.pack(pady=5)

    tk.Label(
        add_patient_window,
        text="Patient Age",
        font=("Arial", 14),
        bg="#E0F7FA"
    ).pack(pady=(10, 5))
    age_entry = tk.Entry(add_patient_window, font=("Arial", 14))
    age_entry.pack(pady=5)

    tk.Label(
        add_patient_window,
        text="Patient birthdate (YYYY.MM.DD)",
        font=("Arial", 14),
        bg="#E0F7FA"
    ).pack(pady=(10, 5))
    date_entry = tk.Entry(add_patient_window, font=("Arial", 14))
    date_entry.pack(pady=5)

    tk.Label(
        add_patient_window,
        text="Assign Exercises",
        font=("Arial", 14),
        bg="#E0F7FA"
    ).pack(pady=(10, 5))

    # Exercise selection
    selected_exercises = []
    exercise_vars = {}

    def toggle_exercise(exercise):
        if exercise_vars[exercise].get():
            selected_exercises.append(exercise)
        else:
            selected_exercises.remove(exercise)

    for exercise in [
        "Elbow Up Down", "Arm Extension", "Wall Walk Left Hand",
        "Standing Leg Front Lift", "Single Leg Squat", "Side Leg Raise",
        "Side Box Step Ups", "Front Box Step Ups", "Step Reaction Training",
        "Calf Stretch", "Hamstring Stretch", "Partial Wall Squat",
        "Seated Knee Extension"
    ]:
        exercise_vars[exercise] = tk.BooleanVar()
        cb = tk.Checkbutton(
            add_patient_window,
            text=exercise,
            variable=exercise_vars[exercise],
            command=lambda ex=exercise: toggle_exercise(ex),
            font=("Arial", 12),
            bg="#E0F7FA"
        )
        cb.pack(anchor="w", padx=20)

    # Submit button to add patient and exercises to the database
    def submit():
        name = name_entry.get()
        age = age_entry.get()
        date=date_entry.get()
        if name and date and age.isdigit() and selected_exercises:
            try:
                with sqlite3.connect('hospital.db') as conn:
                    c = conn.cursor()
                    c.execute('INSERT INTO patients (name, age, date, doctor_id) VALUES (?, ?, ?, ?)', (name, age, date, current_user[0]))
                    c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (name, date, "patient"))
                    patient_id = c.lastrowid

                    for exercise in selected_exercises:
                        c.execute('INSERT INTO exercises (patient_id, exercise) VALUES (?, ?)', (patient_id, exercise))

                    conn.commit()
                messagebox.showinfo("Success", "Patient and exercises added successfully!")
                add_patient_window.destroy()
            except sqlite3.OperationalError as e:
                messagebox.showerror("Error", f"Database error: {e}")
        else:
            messagebox.showerror("Error", "Please fill out all fields and select at least one exercise!")

    tk.Button(
        add_patient_window,
        text="Add Patient",
        command=submit,
        font=("Arial", 14),
        bg="#00796B",
        fg="white"
    ).pack(pady=(20, 10))

def patient_overview(parent_window):
    overview_window = tk.Toplevel(parent_window)
    overview_window.title("Patient Overview")
    screen_width = overview_window.winfo_screenwidth()
    screen_height = overview_window.winfo_screenheight()
    overview_window.geometry(f"{screen_width}x{screen_height}")
    overview_window.configure(bg="#E0F7FA")

    # Add title for patient overview
    title_label = tk.Label(
        overview_window,
        text="Patient Overview",
        font=("Arial", 16, "bold"),
        bg="#E0F7FA",
        fg="#00796B"
    )
    title_label.pack(pady=(20, 10))

    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()

    c.execute('''SELECT id,name, age,date FROM patients WHERE doctor_id = ?''', (current_user[0],))
    patients = c.fetchall()


    # Display each patient's details
    if patients:
        for patient in patients:
            tk.Label(
                overview_window,
                text=f"Name: {patient[1]}, Age: {patient[2]}, Username: {patient[1]}, Password: {patient[3]}",
                font=("Arial", 14),
                bg="#E0F7FA",
                fg="#00796B"
            ).pack(pady=5)

            conn = sqlite3.connect('hospital.db')
            c = conn.cursor()

            c.execute('''SELECT exercise FROM exercises WHERE patient_id = ?''', (patient[0],))
            exercises = c.fetchall()

            if exercises:
                for exercise in exercises:
                    tk.Label(
                        overview_window,
                        text=f"  - {exercise[0]}",
                        font=("Arial", 12),
                        bg="#E0F7FA",
                        fg="#004D40"
                    ).pack(anchor="w", padx=40)
            else:
                tk.Label(
                    overview_window,
                    text="  No exercises assigned.",
                    font=("Arial", 12),
                    bg="#E0F7FA",
                    fg="#004D40"
                ).pack(anchor="w", padx=40)
    else:
        tk.Label(
            overview_window,
            text="No patients found.",
            font=("Arial", 14),
            bg="#E0F7FA",
            fg="#00796B"
        ).pack(pady=20)
    conn.close()

def show_main_page(window):
    for widget in window.winfo_children():
        widget.destroy()

    # Add the title label
    title_label = tk.Label(
        window,
        text="My Pocket Physio",
        font=("Arial", 20, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=(30, 10))

    # Add a body of text
    body_text = tk.Label(
        window,
        text="Welcome to My Pocket Physio, the solution to all your body aches and injuries.",
        font=("Arial", 16),
        bg="#C5EBE8",
        fg="#008878",
        wraplength=700,
        justify="center"
    )
    body_text.pack(pady=(10, 30))

    # Add text for instructions
    instruction_text = tk.Label(
        window,
        text="I am....",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    instruction_text.pack(pady=20)

    # Add buttons for injury types
    btn_patient = tk.Button(
        window,
        text="Patient",
        command=patient_login,
        font=("Arial", 16),
        width=20,
        bg="#008878",
        fg="white"
    )
    btn_patient.pack(pady=20)

    btn_doc = tk.Button(
        window,
        text="Doctor",
        command=register_doctor,
        font=("Arial", 16),
        width=20,
        bg="#008878",
        fg="white"
    )
    btn_doc.pack(pady=20)


# Main GUI
def main():
    init_db()

    root = tk.Tk()

    root.title("Doctor-Patient Management")
    root.geometry("1920x1080")

    root.configure(bg="#C5EBE8")

    show_main_page(root)
    root.mainloop()

if __name__ == "__main__":
    main()
