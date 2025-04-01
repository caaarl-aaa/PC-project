import customtkinter as ctk
from PIL import Image, ImageTk  # For handling images/icons
import tkinter as tk
import tkinter.messagebox as messagebox
from firebase_config import db

loaded_images={}
def preload_images():
    """Load and resize images once at the beginning to optimize performance"""
    global loaded_images
    image_data = {
    "cirtopleft": {"path": "assets_gui/doclog_cirtopleft.png", "size": (1600, 1200)},
    "cirtopright": {"path": "assets_gui/circle2.png", "size": (2100, 1600)},
    "cirbotleft": {"path": "assets_gui/doclog_cirbotleft.png", "size": (1600, 1200)},
    "cirbotright": {"path": "assets_gui/doclog_cirbotright.png", "size": (2400, 1900)}
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
        import doctors_page
        doctors_page.create_doctor_page(app, current_user)  # Load third page

    bg_frame = ctk.CTkFrame(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), fg_color="#E0E0D7")
    bg_frame.place(x=0, y=0)
    current_user=None

    canvas = ctk.CTkCanvas(app, width=2000, height=1000, bg="#E0E0D7", highlightthickness=0)
    canvas.place(x=-50, y=-50)
    if "cirtopleft" in loaded_images:
        canvas.create_image(300, -300, image=loaded_images["cirtopleft"])
    if "cirtopright" in loaded_images:
        canvas.create_image(app.winfo_screenwidth()-100, -450, image=loaded_images["cirtopright"])
    if "cirbotleft" in loaded_images:
        canvas.create_image(400, app.winfo_screenheight()+500, image=loaded_images["cirbotleft"])
    if "cirbotright" in loaded_images:
        canvas.create_image(app.winfo_screenwidth()+200, (app.winfo_screenheight()*2), image=loaded_images["cirbotright"])

    # Prevent garbage collection
    canvas.cirtopleft_image = loaded_images.get("cirtopleft")
    canvas.cirtopright_image = loaded_images.get("cirtopright")
    canvas.cirbotleft_image = loaded_images.get("cirbotleft")
    canvas.cirbotright_image = loaded_images.get("cirbotright")


    title_label = ctk.CTkLabel(app, text="WELCOME BACK!", font=("Garamond", 65, "bold"), text_color="black", bg_color="#E0E0D7")
    title_label.place(x=30, y=400, anchor="w")

    username_entry = ctk.CTkEntry(app, placeholder_text="Enter your username", width=300, height=40, corner_radius=30,fg_color="#E0E0D7", bg_color="#E0E0D7", font=("Georgia", 20), text_color="black")
    username_entry.place(relx=0.75, rely=0.365, anchor="center")

    password_entry = ctk.CTkEntry(app, placeholder_text="Enter your password", width=300, height=40, corner_radius=30, show="*",fg_color="#E0E0D7",bg_color="#E0E0D7", font=("Georgia", 20))
    password_entry.place(relx=0.75, rely=0.45, anchor="center")

    forgot_password_label = ctk.CTkLabel(app, text="Forgot Password? Click here", font=("Georgia", 14,"underline"), text_color="black", cursor="hand2",bg_color="#E0E0D7")
    forgot_password_label.place(relx=0.775, rely=0.52, anchor="e")
    forgot_password_label.bind("<Button-1>", lambda event: open_forgot_password_window())

    register_label = ctk.CTkLabel(app, text="No Account? Register", font=("Georgia", 14, "underline"), text_color="black", cursor="hand2", bg_color='#E0E0D7')
    register_label.place(relx=0.748, rely=0.57, anchor="e")
    register_label.bind("<Button-1>", lambda event: register_window())

    def open_forgot_password_window():
        new_window = ctk.CTkToplevel(app)
        new_window.title("Forgot Password")
        new_window.geometry("300x200")
        label = ctk.CTkLabel(new_window, text="Forgot Password Window", font=("Arial", 14))
        label.pack(pady=50)

    def register_window():
        new_window = ctk.CTkToplevel(app)
        new_window.title("Register")
        new_window.geometry("300x200")
        label = ctk.CTkLabel(new_window, text="No account? Register", font=("Arial", 14))
        label.pack(pady=50)

    def authenticate(username, password, role):
        users_ref = db.collection("users").where("username", "==", username).where("password", "==", password).where("role","==", role)
        users = list(users_ref.stream())
        
        if users:
            return users[0].to_dict()
        return None
    
    def get_doctor_id(username):
        
        doctors_ref = db.collection("doctors").where("username", "==", username)
        doctors = doctors_ref.stream()
        
        for doctor in doctors:
            return doctor.get("id")  # Firestore Document ID
        return None

    def submit():
        global current_user
        username = username_entry.get()
        password = password_entry.get()
        user = authenticate(username, password, 'doctor')

        if user:
            current_user = user
            doctor_id=get_doctor_id(username)
            if doctor_id:
                current_user["doctor_id"]=doctor_id
            open_third_page(current_user)
        else:
            messagebox.showerror("Error", "Wrong Username/Password!")
    # Login Button
    login_button = ctk.CTkButton(app, text="Log In", width=200, height=45, corner_radius=20, fg_color="#092E34", bg_color="#E0E0D7", font=('Arial', 23, 'bold'), command=submit)
    login_button.place(relx=0.75, rely=0.65, anchor="center")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")  
    ctk.set_default_color_theme("blue")  
    
    app = ctk.CTk()
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}")  # Set to full screen
    app.title("Login Page")
    preload_images()
    create_login_page(app)

    app.mainloop()
