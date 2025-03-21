import customtkinter as ctk
import random
from PIL import Image, ImageTk

def open_second_page():
    import second_page_login
    for widget in app.winfo_children():
        widget.destroy()  # Remove current widgets
    second_page_login.create_login_page(app)
    

#Intilialize App
app = ctk.CTk()
app.title("Physiotherapy App")
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.geometry(f"{screen_width}x{screen_height}+0+0")


# Create Canvas for Background Pattern
canvas = ctk.CTkCanvas(app, width=screen_width, height=screen_height, bg= "#89B4B7", highlightthickness=0)
canvas.place(relwidth=1, relheight=1)
screen_width+=350   

# Generate Random Circles for Background
positions = [(150, 30),(450,90),(350,screen_height-170),(674,233),(-30,300),(screen_width-80,100),(screen_width-700,70),(screen_width-400,235),(screen_width-300,623),(screen_width-50,screen_height-50)]
for pos in positions:
    size = random.randint(60, 150)  # Adjust for better visibility
    canvas.create_oval(pos[0], pos[1], pos[0] + size, pos[1] + size, fill="#789FA1", outline="")

prof_image = Image.open("assets_gui/logo.png").resize((400, 400), Image.LANCZOS)
prof_photo = ImageTk.PhotoImage(prof_image)
canvas.create_image(950,250,image=prof_photo)
canvas.profimage = prof_photo
canvas.create_text(950,550,text="An Intelligent Physiotherapy and Recovery App\n           for Personalized and Remote Care",fill="#000000",font=("Garamond", 60, 'bold'))
canvas.create_text(700,650,anchor="nw",text="Welcome to our Medical Application",fill="#000000",font=("Garamond", 30))

# Get Started Button
start_button = ctk.CTkButton(app, text="Get Started", font=("Arial", 23, "bold"), fg_color="#275057", bg_color="#89B4B7",
                             text_color="white", corner_radius=20, width=200, height=50, command=open_second_page)
start_button.place(relx=0.5, rely=0.74, anchor="center")
def exit_app(root):
    root.quit()  # Stop the mainloop
    root.destroy()  # Close all windows

# Run App
app.mainloop()
