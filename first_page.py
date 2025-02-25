import customtkinter as ctk
import random
from PIL import Image
import second_page_login

def open_second_page():
    second_window=second_page_login.run_login_page(app)
    if second_window:
        app.withdraw()
        second_window.wait_window()
        app.deiconify
    

#Intilialize App
app = ctk.CTk()
app.title("Physiotherapy App")


screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app.geometry(f"{screen_width}x{screen_height}+0+0")


# Create Canvas for Background Pattern
canvas = ctk.CTkCanvas(app, width=screen_width, height=screen_height, bg= "#89B4B7", highlightthickness=0)
canvas.place(relwidth=1, relheight=1)

# Generate Random Circles for Background
positions = [(100, 30),(400,90),(300,screen_height-170),(624,233),(-30,300),(screen_width-30,100),(screen_width-750,70),(screen_width-423,235),(screen_width-320,623),(screen_width-50,screen_height-50)]
for pos in positions:
    size = random.randint(40, 100)  # Adjust for better visibility
    canvas.create_oval(pos[0], pos[1], pos[0] + size, pos[1] + size, fill="#789FA1", outline="")

# UI Elements (Centered)
logo_image = ctk.CTkImage(light_image=Image.open("assets_gui/logo.png"),
                          dark_image=Image.open("assets_gui/logo.png"),
                          size=(300, 300))  # Adjust size if needed

# Create a label for the logo
logo_label = ctk.CTkLabel(app, image=logo_image, text="", bg_color="#89B4B7")  # No text, only image
logo_label.place(relx=0.5, rely=0.3, anchor="center")


alt_font=ctk.CTkFont(family="Garamond", size=55, weight='bold')
title2 = ctk.CTkLabel(app, text="An Intelligent Physiotherapy and Recovery App\nfor Personalized and Remote Care",
                      font=alt_font, text_color="black",bg_color= "#89B4B7",justify="center")
title2.place(relx=0.5, rely=0.55, anchor="center")

subtitle = ctk.CTkLabel(app, text="Welcome to our Medical Application",
                        font=("Georgia", 25), text_color="black", bg_color= "#89B4B7")
subtitle.place(relx=0.5, rely=0.66, anchor="center")

# Get Started Button
start_button = ctk.CTkButton(app, text="Get Started", font=("Arial", 23, "bold"), fg_color="#275057", bg_color="#89B4B7",
                             text_color="white", corner_radius=20, width=200, height=50, command=open_second_page)
start_button.place(relx=0.5, rely=0.74, anchor="center")
def exit_app(root):
    root.quit()  # Stop the mainloop
    root.destroy()  # Close all windows

app.protocol("WM_DELETE_WINDOW", lambda: exit_app(app))

# Run App
app.mainloop()
