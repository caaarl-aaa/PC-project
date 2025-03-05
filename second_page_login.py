import customtkinter as ctk
from PIL import Image, ImageTk
import sqlite3
import tkinter.messagebox as messagebox
import third_page


def create_login_page(app):

    for widget in app.winfo_children():
        widget.destroy()

    def open_third_page(current_user):
        third_page.create_third_page(app, current_user)  # Load third page

    current_user=None
    # Initialize the app
    # Background Frame (to match design color)
    bg_frame = ctk.CTkFrame(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), fg_color="#eae7de")
    bg_frame.place(x=0, y=0)

    # Canvas to draw circular elements
    canvas = ctk.CTkCanvas(app, width=2500, height=3000, bg="#E0E0D7", highlightthickness=0)
    canvas.place(x=-50, y=-50)
    cir_image = Image.open("assets_gui/cir_pg2.png").resize((1200, 1200), Image.LANCZOS)
    cir_photo = ImageTk.PhotoImage(cir_image)
    canvas.create_image(400,100,image=cir_photo)
    canvas.cirimage = cir_photo
    cir2_image = Image.open("assets_gui/cir2_pg2.png").resize((1200, 1200), Image.LANCZOS)
    cir2_photo = ImageTk.PhotoImage(cir2_image)
    canvas.create_image(200,200,image=cir2_photo)
    canvas.cir2image = cir2_photo
    
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
    tagline_label.place(x=15, y=650)



    
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
    


