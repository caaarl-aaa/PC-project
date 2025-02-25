import customtkinter as ctk
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk  # For handling images/icons
import tkinter as tk
from tkcalendar import Calendar
import pywinstyles
from pathlib import Path
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("C:/Users/Carl/Desktop/Tkinter-Designer-master/Tkinter-Designer-master/build/assets/frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)
today_date = datetime.today().strftime("%Y-%m-%d")
selected_date=today_date
todayy=datetime.today().strftime("%d %B %Y")
current_year=datetime.today().year
current_month=datetime.today().month
current_day=datetime.today().day
sidebar_buttons={}
def run_third_page(current_user):
    notifications="No Notifications to show"
    third_app = ctk.CTkToplevel()
    third_app.title("Physio Session")
    
    if not current_user:
        print("Error: current_user is None")
        return
    
    conn = sqlite3.connect('hospital.db')
    c = conn.cursor()
    patient_id = current_user[1]
    c.execute('''SELECT exercise_name, sets, reps FROM exercises WHERE patient_id = ? AND date=?''', (patient_id, today_date))
    exercises = c.fetchall()
    c.execute('''SELECT name, age, injury FROM patients WHERE id=?''', (patient_id,))
    patient_data=c.fetchone()
    if patient_data:
        patient_name, patient_age, patient_injury = patient_data
    else:
        patient_name, patient_age, patient_injury = "Unknown", "Unknown", "Unknown"
    c.execute('''SELECT type,message FROM notifications WHERE patient_id = ? AND date=?''', (patient_id, today_date))
    notifications = c.fetchall()
    conn.close()

    screen_width = third_app.winfo_screenwidth()
    screen_height = third_app.winfo_screenheight()
    third_app.geometry(f"{screen_width}x{screen_height}+0+0")
    third_app.grab_set()

    def create_image_canvas(parent, img_path, width, height, ex, sets, reps,row):
        """
        Function to create a canvas and overlay text on an image inside CustomTkinter.
        """
        
        text_y = (height // 2)-40
        canvas = tk.Canvas(parent, width=width, height=height-120, bg="white", highlightthickness=0)
        canvas.grid(row=row, column=0, columnspan=2, padx=10, pady=0, sticky="ew")

        bar_image = Image.open(img_path).resize((width, height), Image.LANCZOS)
        bar_photo = ImageTk.PhotoImage(bar_image)
        canvas.image = bar_photo  

        canvas.create_image(0, -40, anchor="nw", image=bar_photo)

        canvas.create_text(170, text_y, text=f"{ex}\n{sets} sets", font=("Garamond", 20, "bold"), fill="black", anchor="w")

        canvas.create_text(width - 50, text_y, text=f"x{reps}", font=("Garamond", 25, "bold"), fill="black", anchor="e")

        return canvas 
    def update_exercises():
        global selected_date
        selected_date=calendar.get_date()
        
        conn = sqlite3.connect('hospital.db')
        c = conn.cursor()
        patient_id = current_user[1]
        c.execute('''SELECT exercise_name, sets, reps FROM exercises WHERE patient_id = ? AND date=?''', (patient_id, selected_date))
        exercise_list = c.fetchall()
        conn.close()
        for widget in session_frame.winfo_children():
            if widget != tooday_label:  # ✅ Preserve `tooday_label`
                widget.destroy()

        if exercise_list:
            for i, (ex, sets, reps) in enumerate(exercise_list):
                create_image_canvas(session_frame, "assets_gui/bar.png", 600, 280, ex, sets, reps, row=i+1)
        else:
            no_exercise_label = ctk.CTkLabel(session_frame, text="No exercises found for this date.", font=("Arial", 18))
            no_exercise_label.grid(row=2, column=0, columnspan=2, padx=10, pady=0, sticky="ew")

    # Sidebar Frame
    sidebar = ctk.CTkFrame(third_app, width=180, corner_radius=30, fg_color="#1C5F64", bg_color="#CCDEE0")
    sidebar.pack(side="left", fill="y")

    # Content Frame
    content = ctk.CTkFrame(third_app)
    content.pack(side="right", fill="both", expand=True)

    # Dictionary for Frames (Pages)
    pages = {}

    # Create Frames (Pages)
    for page_name in ["Dashboard", "My Session", "My Progress", "Notifications", "Contact"]:
        if page_name=="Notifications":
            frame = ctk.CTkFrame(content, fg_color="#76A0A4", width=1500, height=1100)
            frame.grid(row=0, column=0, sticky="nsew")
            pages[page_name] = frame
        else:
            frame = ctk.CTkFrame(content, fg_color="#CCDEE0", width=1500, height=1100)
            frame.grid(row=0, column=0, sticky="nsew")
            pages[page_name] = frame

    # Function to switch pages
    def switch_page(page_name):
        for name, btn in sidebar_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#D9D9D9")  # Selected button
            else:
                btn.configure(fg_color="#A0B5B6")  # Not selected
        pages[page_name].tkraise()

    # Sidebar Buttons with Icons
    dashboard_icon=ctk.CTkImage(light_image=Image.open("assets_gui/dashboard_icon.png"), size=(60, 60))
    my_session_icon=ctk.CTkImage(light_image=Image.open("assets_gui/my_session.png"), size=(60, 60))
    my_progress_icon=ctk.CTkImage(light_image=Image.open("assets_gui/my_progress.png"), size=(60, 50))
    notifications_icon=ctk.CTkImage(light_image=Image.open("assets_gui/notifications.png"), size=(60, 60))
    contact_icon=ctk.CTkImage(light_image=Image.open("assets_gui/contact.png"), size=(60, 60))
    buttons = [
        ("Dashboard", dashboard_icon, lambda: switch_page("Dashboard")),
        ("My Session", my_session_icon, lambda: switch_page("My Session")),
        ("My Progress", my_progress_icon, lambda: switch_page("My Progress")),
        ("Notifications", notifications_icon, lambda: switch_page("Notifications")),
        ("Contact", contact_icon, lambda: switch_page("Contact"))
    ]

    for btn_text, icon, command in buttons:
        btn = ctk.CTkButton(sidebar, text=f"{btn_text}", image=icon,compound='top',height=135, fg_color="#A0B5B6", hover_color="#D9D9D9",
                            corner_radius=30, command=lambda p=btn_text: switch_page(p), font=("Arial", 14, "bold"), text_color='black')
        btn.pack(fill="x", pady=7, padx=10)
        sidebar_buttons[btn_text] = btn
    switch_page("Dashboard")
    
    # 🎨 **DASHBOARD PAGE**
    stars_icon=ctk.CTkImage(light_image=Image.open("assets_gui/stars.png"), size=(100, 100))
    dashboard_label = ctk.CTkLabel(pages["Dashboard"],width=500,height=105,corner_radius=20, text="Doing Great,\nKeep it up!      ",image=stars_icon,compound="right", font=("Garamond", 43, "bold"),text_color="#D9D9D9", fg_color="#0B2B32", bg_color="#CCDEE0")
    dashboard_label.place(x=730, y=20)
    profile_frame = ctk.CTkFrame(pages["Dashboard"], width=310,fg_color="white", corner_radius=20)
    profile_frame.place(x=100, y=100)
    profile_frame.pack_propagate(False)
    profile_img = Image.open("assets_gui/profile.png").convert("RGBA")  
    profile_img = Image.open("assets_gui/profile.png")
    profile_icon = ctk.CTkImage(light_image=profile_img, size=(100, 100))
    profile_label = ctk.CTkLabel(pages["Dashboard"],text="",image=profile_icon,fg_color="#000001", bg_color="#000001")
    profile_label.place(x=210,y=45)
    pywinstyles.set_opacity(profile_label, color="#000001")
    name_label = ctk.CTkLabel(profile_frame, text=f"{patient_name}", font=("Garamond", 35, "bold"))
    name_label.pack(pady=(40, 5))
    info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent",corner_radius=20)
    info_frame.pack(fill="x", padx=10, pady=10)
    info_frame.pack_propagate(False)
    age_label = ctk.CTkLabel(info_frame, text=f"Age", font=("Georgia", 17), text_color="#1C5F64")
    age_label.grid(row=0, column=0, padx=60)
    injury_label = ctk.CTkLabel(info_frame, text=f"Injury", font=("Georgia", 17),text_color="#1C5F64")
    injury_label.grid(row=0, column=1, padx=(30,60))
    age_value = ctk.CTkLabel(info_frame, text=patient_age, font=("Georgia", 16, "bold"))
    age_value.grid(row=1, column=0, padx=60, pady=(0,20))
    injury_value = ctk.CTkLabel(info_frame, text=patient_injury, font=("Georgia", 16, "bold"))
    injury_value.grid(row=1, column=1, padx=(30,60),pady=(0,20))
    
    notifeed_label = ctk.CTkLabel(pages["Dashboard"],text="Notifications | Feedback", text_color="#1C5F64",fg_color="transparent",font=("Georgia", 25))
    notifeed_label.place(x=100,y=330)
    date_label = ctk.CTkLabel(pages["Dashboard"],text=f"{todayy}", text_color="#3D5051",fg_color="transparent",font=("Georgia", 18))
    date_label.place(x=230,y=370)
    scroll_frame = ctk.CTkScrollableFrame(pages["Dashboard"], width=280, height=300, fg_color="white", corner_radius=20)
    scroll_frame.place(x=100, y=410)
    for idx, (title, message) in enumerate(notifications):
        frame = ctk.CTkFrame(scroll_frame, fg_color="white", corner_radius=5)
        frame.pack(fill="x", pady=5, padx=5)

        title_label = ctk.CTkLabel(frame, text=title, font=("Georgia", 18, "bold"), text_color="black")
        title_label.pack(anchor="w", padx=10, pady=(5, 0))

        message_label = ctk.CTkLabel(frame, text=message, font=("Georgia", 17), text_color="#3D5051", wraplength=250, justify="left")
        message_label.pack(anchor="w", padx=10, pady=(0, 5))

    exscroll_frame = ctk.CTkScrollableFrame(pages["Dashboard"], width=600, height=500, fg_color="white", corner_radius=20)
    exscroll_frame.place(x=600, y=150)
    today_label = ctk.CTkLabel(exscroll_frame, text="Today's Session", font=("Garamond", 37, "bold"))
    today_label.grid(row=0, column=0, padx=(30,0))
    see_label = ctk.CTkLabel(exscroll_frame, text="See My Session", font=("Georgia", 17,"underline"),text_color="#3D5051", cursor="hand2")
    see_label.grid(row=0, column=1, padx=(180,10))
    see_label.bind("<Button-1>", lambda event: switch_page("My Session")) 
    for i,(ex, sets, reps) in enumerate(exercises):
        create_image_canvas(exscroll_frame, "assets_gui/bar.png", 600, 280, ex, sets, reps, row=i+1)


    # 🎨 **MY SESSION PAGE**
    ccanvas = ctk.CTkCanvas(pages["My Session"], width=1800, height=1000, bg="#CCDEE0", highlightthickness=0)
    ccanvas.place(x=0, y=0)
    #shadow circle
    ccanvas.create_oval(1150, 400, 1950, 1375, fill="#39526D", outline="")
    ccanvas.create_oval(950, -520, 2050, 775, fill="#1C5F64", outline="")
    ccanvas.create_oval(-100, 720, 1850, 1875, fill="#39526D", outline="")
    session_frame = ctk.CTkScrollableFrame(pages["My Session"], fg_color="white", width=600, height=640)
    session_frame.place(x=100,y=50)
    tooday_label = ctk.CTkLabel(session_frame, text="Today's Session", font=("Garamond", 37, "bold"))
    tooday_label.grid(row=0, column=0, padx=(30,0))

    calendar = Calendar(pages["My Session"], selectmode="day", font="Arial 17",background="#99C0C4",foreground="black",
                        headersbackground="#004D40",headersforeground="white",selectbackground="#00796B",selectedforeground="white",
                        normalbackground="#B2DFDB",normalforeground="black",
                        year=current_year, month=current_month, day=current_day, date_pattern="yyyy-mm-dd")
    calendar.place(x=1150,y=50)
    calendar.bind("<<CalendarSelected>>", lambda e: update_exercises())
    
    update_exercises()
    inst_frame = ctk.CTkFrame(pages["My Session"], width=350, height=500, fg_color="white")
    inst_frame.place(x=920, y=350)
    inst_textbox = ctk.CTkTextbox(inst_frame, width=350, height=250, font=("Georgia", 17), wrap="word")
    inst_textbox.pack(padx=10, pady=10)
    instruction_text = (
    "Instructions\n\n"
    "To perform the exercises, select one from the list and press Start to watch the instructional video. "
    "Try a trial exercise to adjust the intensity based on your progress. Ensure your device is at a good "
    "angle, with proper lighting and clothing for accurate motion tracking. Once ready, perform the exercise with proper form."
    )
    inst_textbox.insert("1.0", instruction_text)
    inst_textbox.configure(state="disabled")

    start_button = ctk.CTkButton(pages["My Session"], text="Start", width=100, height=45, corner_radius=20, fg_color="#092E34", bg_color="#39526D", font=('Arial', 23, 'bold'))
    start_button.place(x=620, y=715)

    
    # 🎨 **MY PROGRESS PAGE**
    progress_label = ctk.CTkLabel(pages["My Progress"], text="Therapy Progress", font=("Arial", 24, "bold"))
    progress_label.pack(pady=20)

    progress_chart = ctk.CTkFrame(pages["My Progress"], width=400, height=200, fg_color="white")
    progress_chart.pack(pady=20)
    progress_text = ctk.CTkLabel(progress_chart, text="📊 Progress Chart (Mock Data)", font=("Arial", 16))
    progress_text.pack()

    # 🎨 **NOTIFICATIONS PAGE**
    notif_label = ctk.CTkLabel(pages["Notifications"], text="Notifications", font=("Arial", 24, "bold"))
    notif_label.pack(pady=10)
    circle_img = Image.open("assets_gui/circle2.png").convert("RGBA")  
    circle_icon = ctk.CTkImage(light_image=circle_img, size=(900, 900))
    circle_label = ctk.CTkLabel(pages["Notifications"],text="",image=circle_icon, width=500, height=500, fg_color="#000001", bg_color="#000001")
    circle_label.place(x=-500,y=-500)
    pywinstyles.set_opacity(circle_label,value=0.2,color="#000001")
    notif_frame = ctk.CTkFrame(pages["Notifications"], width=500, height=300, fg_color="white")
    notif_frame.pack(pady=20)

    notif_list = [
        ("March 25, 2025", "Reminder: Complete your session"),
        ("March 24, 2025", "Doctor's Feedback: Good progress!"),
    ]

    for date, msg in notif_list:
        notif_item = ctk.CTkFrame(notif_frame, fg_color="#D9D9D9")
        notif_item.pack(fill="x", padx=10, pady=5)
        date_label = ctk.CTkLabel(notif_item, text=date, font=("Arial", 12, "bold"), fg_color="white")
        date_label.pack(side="left", padx=5)
        msg_label = ctk.CTkLabel(notif_item, text=msg, font=("Arial", 12))
        msg_label.pack(side="left", padx=10)

    # 🎨 **CONTACT PAGE**
    contact_label = ctk.CTkLabel(pages["Contact"], text="Contact Us", font=("Arial", 24, "bold"))
    contact_label.pack(pady=10)

    contact_info = ctk.CTkLabel(pages["Contact"], text="📧 info@gmail.com\n📞 321-221-331", font=("Arial", 18))
    contact_info.pack(pady=10)

    contact_form = ctk.CTkFrame(pages["Contact"], width=400, height=200, fg_color="white")
    contact_form.pack(pady=20)
    form_label = ctk.CTkLabel(contact_form, text="📝 Get in Touch", font=("Arial", 16, "bold"))
    form_label.pack()

    contact_entry = ctk.CTkEntry(contact_form, width=300, placeholder_text="Type your message here...")
    contact_entry.pack(pady=10)

    submit_button = ctk.CTkButton(contact_form, text="Submit", font=("Arial", 16, "bold"), corner_radius=10)
    submit_button.pack(pady=10)

    # Show Default Page
    switch_page("Dashboard")

    third_app.protocol("WM_DELETE_WINDOW", lambda: third_app.destroy())

    return third_app
