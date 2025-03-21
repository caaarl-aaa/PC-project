import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter.messagebox as messagebox
import doctor_login
from firebase_config import db

loaded_images={}
def preload_images():
    """Load and resize images once at the beginning to optimize performance"""
    global loaded_images
    image_data = {
    "cir_image": {"path": "assets_gui/cir_pg2.png", "size": (1200, 1200)},
    "cir2_image": {"path": "assets_gui/cir2_pg2.png", "size": (1200, 1200)},
    "heart_icon": {"path": "assets_gui/heart_icon.png", "size": (500, 500)},
    }

    for key, data in image_data.items():
        try:
            image = Image.open(data["path"]).resize(data["size"], Image.LANCZOS)
            loaded_images[key] = ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading {data["path"]}: {e}")


preload_images()

def create_login_page(app):

    for widget in app.winfo_children():
        widget.destroy()

    def open_third_page(current_user):
        import third_page
        third_page.create_third_page(app, current_user)  # Load third page

    current_user=None
    # Initialize the app
    # Background Frame (to match design color)
    bg_frame = ctk.CTkFrame(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), fg_color="#eae7de")
    bg_frame.place(x=0, y=0)

    # Canvas to draw circular elements
    canvas = ctk.CTkCanvas(app, width=2500, height=3000, bg="#E0E0D7", highlightthickness=0)
    canvas.place(x=-50, y=-50)
    if "cir_image" in loaded_images:
        canvas.create_image(400,100, image=loaded_images["cir_image"])
    if "cir2_image" in loaded_images:
        canvas.create_image(200,200, image=loaded_images["cir2_image"])
    
    # Load Heart + Cross Icon (Replace with actual path if needed)
    try:
        if "heart_icon" in loaded_images:
            canvas.create_image(350,400, image=loaded_images["heart_icon"])
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
        for widget in app.winfo_children():
            widget.destroy()  # Remove current widgets
            doctor_login.create_login_page(app)


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
        users_ref = db.collection("users").where("username", "==", username).where("password", "==", password).where("role","==", role)
        users = list(users_ref.stream())
        
        if users:
            return users[0].to_dict()
        return None

    def get_patient_id(username):
        
        patients_ref = db.collection("patients").where("username", "==", username)
        patients = patients_ref.stream()
        
        for patient in patients:
            print(f"ID: {patient.get("id")}")
            return patient.get("id")  # Firestore Document ID
            
        return None


    def submit():
        username = username_entry.get()
        password = password_entry.get()
        user = authenticate(username, password, 'patient')

        if user:
            global current_user
            current_user = user
             # Fetch patient ID based on user
            patient_id=get_patient_id(username)
            if patient_id:
                current_user["patient_id"]=patient_id
            #print("Logged-in Patient:", current_user)
            open_third_page(current_user)

        else:
            messagebox.showerror("Error", "Wrong Username/Password!")
    # Login Button
    login_button = ctk.CTkButton(app, text="Log In", width=200, height=45, corner_radius=20, fg_color="#092E34", bg_color="#E0E0D7", font=('Arial', 23, 'bold'), command=submit)
    login_button.place(relx=0.75, rely=0.65, anchor="center")
    


