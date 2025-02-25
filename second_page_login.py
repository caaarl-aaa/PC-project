import customtkinter as ctk
from PIL import Image, ImageTk
import sqlite3
import tkinter.messagebox as messagebox
import third_page

third_window=None

def run_login_page(previous_window):
    def open_third_page(current_user):
        global third_window  # Use the global variable

        if third_window and third_window.winfo_exists():  
            third_window.lift()  # Bring it to front if it already exists
            third_window.focus_force()  # Set focus on the third window
        else:
            app.withdraw()  # Hide login window
            third_window = third_page.run_third_page(current_user)  # Open third page

            # Ensure login window reopens when third page is closed
            third_window.protocol("WM_DELETE_WINDOW", lambda: (third_window.destroy(), app.deiconify()))

    current_user=None
    # Initialize the app
    app = ctk.CTkToplevel()
    app.title("Login")
    screen_width = app.winfo_screenwidth()
    screen_height = app.winfo_screenheight()
    app.geometry(f"{screen_width}x{screen_height}+0+0")
    app.grab_set()
    # Background Frame (to match design color)
    bg_frame = ctk.CTkFrame(app, width=screen_width, height=screen_height, fg_color="#eae7de")
    bg_frame.place(x=0, y=0)

    # Canvas to draw circular elements
    canvas = ctk.CTkCanvas(app, width=2500, height=3000, bg="#E0E0D7", highlightthickness=0)
    canvas.place(x=-50, y=-50)
    #shadow circle
    canvas.create_oval(-420, -370, 965, 755, fill="#AAAAA4", outline="")
    canvas.create_oval(-500, -400, 925, 750, fill="#175E63", outline="")
    canvas.create_oval(-500, -200, 750, 850, fill="#092E34", outline="") 

    # Load Heart + Cross Icon (Replace with actual path if needed)
    try:
        heart_icon = Image.open("assets_gui/heart_icon.png")  # Replace with correct path
        heart_icon = heart_icon.resize((500, 500))
        app.heart_icon = ImageTk.PhotoImage(heart_icon)  # Store in app to prevent garbage collection
        canvas.create_image(350, 400, image=app.heart_icon)  # Use stored reference
    except:
        print("Error")  # If the image isn't available, it won't crash

    # "Log In" Title
    title_label = ctk.CTkLabel(app, text="Log In", font=("Garamond", 65, "bold"), text_color="black", bg_color="#E0E0D7")
    title_label.place(relx=0.75, rely=0.2, anchor="center")

    # Username Entry
    username_entry = ctk.CTkEntry(app, placeholder_text="Enter your username", width=300, height=40, corner_radius=30, bg_color="#E0E0D7", font=("Georgia", 20))
    username_entry.place(relx=0.75, rely=0.35, anchor="center")

    # Password Entry
    password_entry = ctk.CTkEntry(app, placeholder_text="Enter your password", width=300, height=40, corner_radius=30, show="*",bg_color="#E0E0D7", font=("Georgia", 20))
    password_entry.place(relx=0.75, rely=0.45, anchor="center")

    # Function to open a new window
    def open_forgot_password_window():
        new_window = ctk.CTkToplevel(app)
        new_window.title("Forgot Password")
        new_window.geometry("300x200")
        label = ctk.CTkLabel(new_window, text="Forgot Password Window", font=("Arial", 14))
        label.pack(pady=50)

    def open_doctor_login_window():
        new_window = ctk.CTkToplevel(app)
        new_window.title("Doctor Login")
        new_window.geometry("300x200")
        label = ctk.CTkLabel(new_window, text="Doctor Login Window", font=("Arial", 14))
        label.pack(pady=50)


    # Forgot Password Label
    forgot_password_label = ctk.CTkLabel(app, text="Forgot Password? Click here", font=("Georgia", 14,"underline"), text_color="black", cursor="hand2",bg_color="#E0E0D7")
    forgot_password_label.place(relx=0.78, rely=0.52, anchor="center")
    forgot_password_label.bind("<Button-1>", lambda event: open_forgot_password_window())  # Bind click event

    # Log in as Doctor Label
    doctor_login_label = ctk.CTkLabel(app, text="Log In As - Doctor", font=("Georgia", 14, "underline"), text_color="black", cursor="hand2", bg_color='#E0E0D7')
    doctor_login_label.place(relx=0.8, rely=0.57, anchor="center")
    doctor_login_label.bind("<Button-1>", lambda event: open_doctor_login_window())  # Bind click event
    

    # Tagline at the bottom
    tagline_label = ctk.CTkLabel(app, text="An Intelligent Physiotherapy and Recovery App\nfor Personalized and Remote Care",
                                font=("Georgia", 20), text_color="black", justify="center", bg_color="#E0E0D7")
    tagline_label.place(relx=0.15, rely=0.9, anchor="center")

    def go_back():
        app.grab_release()
        app.destroy()
        previous_window.deiconify()
    
    back_button = ctk.CTkButton(app, text="Go Back", width=200, height=40, corner_radius=20, fg_color="#092E34", bg_color="#E0E0D7", font=('Arial', 23,'bold'), command=go_back)
    back_button.place(relx=0.75, rely=0.73, anchor="center")


        
    # Database setup
    def init_db():
        conn = sqlite3.connect('hospital.db')
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT CHECK(role in ('patient','doctor')) NOT NULL
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        age INTEGER CHECK(age>0),
                        birthdate TEXT NOT NULL,
                        injury TEXT NOT NULL,
                        health_conditions TEXT DEFAULT NULL,
                        doctor_id TEXT NOT NULL,
                        FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
                    )''')

        c.execute('''CREATE TABLE IF NOT EXISTS exercises (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        patient_id INTEGER NOT NULL,
                        exercise_name TEXT,
                        date TEXT NOT NULL,
                        doctor_id INTEGER NOT NULL,
                        sets INTEGER DEFAULT 1 CHECK(sets>0),
                        reps INTEGER CHECK(reps>0),
                        FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE
                        FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE SET NULL
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE, 
                    phone_number VARCHAR(15)UNIQUE,
                    profession TEXT,
                    hospital TEXT,
                    name TEXT NOT NULL,
                    username TEXT,
                    FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE
                  )''')
        c.execute('''CREATE TABLE IF NOT EXISTS notifications(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  patient_id INTEGER NOT NULL,
                  date TEXT NOT NULL,
                  type TEXT CHECK(type in ('Reminder', "Doctor's Feedback")) NOT NULL,
                  message TEXT NOT NULL,
                  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
                  )''')
        
        c.execute("INSERT INTO users (username, password, role) VALUES('dd', 'zz','patient')")
        c.execute("INSERT INTO users (username, password, role) VALUES('aa', 'zz','doctor')")
        c.execute("INSERT INTO doctors (id,email, phone_number, profession, hospital, name,username) VALUES (4111, 'dr.raymond@example.com', '321-221-331', 'Therapist', 'California Hospital','Dr. Raymond Bowers' ,'aa')")
        c.execute("INSERT INTO patients (id,name, age, birthdate,injury, doctor_id) VALUES(111,'dd',23,'zz','knee tear',4111)")
        c.execute("INSERT INTO exercises (patient_id, exercise_name, date, doctor_id, sets, reps)  VALUES (111, 'Side Leg Raise', '2025-02-25', 4111, 2, 10)")
        c.execute("INSERT INTO exercises (patient_id, exercise_name, date, doctor_id, sets, reps)  VALUES (111, 'Side Leg Raise1', '2025-02-25', 4111, 2, 10)")
        c.execute("INSERT INTO exercises (patient_id, exercise_name, date, doctor_id, sets, reps)  VALUES (111, 'Side Leg Raise2', '2025-02-25', 4111, 2, 10)")
        c.execute("INSERT INTO exercises (patient_id, exercise_name, date, doctor_id, sets, reps)  VALUES (111, 'Side Leg Raise3', '2025-02-25', 4111, 2, 10)")
        c.execute("INSERT INTO exercises (patient_id, exercise_name, date, doctor_id, sets, reps)  VALUES (111, 'Side Leg Raise4', '2025-02-25', 4111, 2, 10)")
        c.execute("""INSERT INTO notifications (patient_id, date, type, message) VALUES (111, '2025-02-25', "Doctor's Feedback", 'Keep stretching your knee regularly.')""")
        c.execute("INSERT INTO notifications (patient_id, date, type, message) VALUES (111, '2025-02-25', 'Reminder', 'Hydrate well before your next session.')")
        c.execute("""INSERT INTO notifications (patient_id, date, type, message) VALUES (111, '2025-02-25', "Doctor's Feedback", 'Your recovery progress is great!')""")
        c.execute("INSERT INTO notifications (patient_id, date, type, message) VALUES (111, '2025-02-25', 'Reminder', 'Do your morning exercises before breakfast.')")

        conn.commit()
        conn.close()
    
    def authenticate(username, password, role):
        conn = sqlite3.connect('hospital.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ? AND password = ? AND role = ?', (username, password, role))
        user = c.fetchone()
        conn.close()
        return user

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
            #print("Logged-in Patient:", current_user)
            open_third_page(current_user)

        else:
            messagebox.showerror("Error", "Wrong Username/Password!")
    # Login Button
    login_button = ctk.CTkButton(app, text="Log In", width=200, height=45, corner_radius=20, fg_color="#092E34", bg_color="#E0E0D7", font=('Arial', 23, 'bold'), command=submit)
    login_button.place(relx=0.75, rely=0.65, anchor="center")

    # Run the app
    init_db()
    app.protocol("WM_DELETE_WINDOW", lambda: exit_app(app))

    def exit_app(window):
        window.quit()
        window.destroy()

    return app



