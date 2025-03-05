import customtkinter as ctk
import sqlite3
from datetime import datetime
from PIL import Image, ImageTk  # For handling images/icons
import tkinter as tk
from tkcalendar import Calendar
import main

today_date = datetime.today().strftime("%Y-%m-%d")
selected_date=today_date
todayy=datetime.today().strftime("%d %B %Y")
current_year=datetime.today().year
current_month=datetime.today().month
current_day=datetime.today().day
sidebar_buttons={}
selected_exercise=None
def create_third_page(app,current_user):
    for widget in app.winfo_children():
        widget.destroy() 


    notifications="No Notifications to show"
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
    c.execute('''SELECT date, type, message FROM notifications WHERE patient_id=? ORDER BY date DESC''',(patient_id,))
    all_notifications=c.fetchall()
    grouped_notifications = {}
    for date, type_, message in all_notifications:
        if date not in grouped_notifications:
            grouped_notifications[date] = []  # Initialize list if date is not in dictionary
        grouped_notifications[date].append((type_, message))
    c.execute('''SELECT injury, doctor_id from patients WHERE id=?''',(patient_id,))
    doc=c.fetchone()
    if doc:
        doctor_id=doc[1]
        dinjury=doc[0]
        c.execute('''SELECT email, phone_number, profession, hospital, name FROM doctors WHERE id=?''',(doctor_id,))
        doc_info=c.fetchone()
        if doc_info:
            demail, dphone, dprofession, dhospital, dname=doc_info
        else:
            demail, dphone, dprofession, dhospital, dname=(None, None, None, None, None)
    else:
        doctor_id=None
        demail, dphone, dprofession, dhospital, dname=(None, None, None, None, None)
    conn.close()

    

    main_frame = ctk.CTkFrame(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), fg_color="#CCDEE0")
    main_frame.place(x=0, y=0)
    def go_back_to_login():
        from second_page_login import create_login_page
        create_login_page(app)

    logout_button = ctk.CTkButton(app, text="Logout", font=("Arial", 23, "bold"), fg_color="#275057", bg_color="#CCDEE0",
                             text_color="white", corner_radius=20, width=150, height=50, command=go_back_to_login)
    logout_button.place(x=app.winfo_screenwidth()-200, y=app.winfo_screenheight()-135)

    def select_exercise(ex, sets, reps, canvas):
        global selected_exercise
        selected_exercise = (ex, sets, reps)

        # Highlight the selected exercise
        for widget in session_frame.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.configure(bg="white")  # Reset all to white
        canvas.configure(bg="#A0B5B6")  # Change selected to another color


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
        
        canvas.bind("<Button-1>", lambda event: select_exercise(ex, sets, reps, canvas))

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
    sidebar = ctk.CTkFrame(main_frame, width=180, corner_radius=30, fg_color="#1C5F64", bg_color="#CCDEE0")
    sidebar.pack(side="left", fill="y")

    # Content Frame
    content = ctk.CTkFrame(main_frame)
    content.pack(side="right", fill="both", expand=True)

    # Dictionary for Frames (Pages)
    pages = {}

    # Create Frames (Pages)
    for page_name in ["Dashboard", "My Session", "My Progress", "Notifications", "Contact"]:
        if page_name=="Notifications":
            frame = ctk.CTkFrame(content, fg_color="white", width=1500, height=1100)
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

    profile_canvas = ctk.CTkCanvas(pages["Dashboard"], width=500, height=740, bg="#CCDEE0", bd=0, highlightthickness=0)
    profile_canvas.place(x=100, y=0)
    profile_frame = ctk.CTkFrame(profile_canvas, width=310,height=120,fg_color="white",bg_color="white")
    profile_frame.pack_propagate(False)
    profile_frame.place(x=25,y=105)
    

    wbox_image = Image.open("assets_gui/white_box.png").resize((400, 275), Image.LANCZOS)
    wbox_photo = ImageTk.PhotoImage(wbox_image)
    profile_canvas.create_image(225,220,image=wbox_photo)
    profile_canvas.wboximage = wbox_photo
    prof_image = Image.open("assets_gui/profile.png").resize((175, 125), Image.LANCZOS)
    prof_photo = ImageTk.PhotoImage(prof_image)
    profile_canvas.create_image(225,80,image=prof_photo)
    profile_canvas.profimage = prof_photo
    
    name_label = ctk.CTkLabel(profile_frame, text=f"{patient_name}", font=("Garamond", 35, "bold"))
    name_label.pack(pady=(0, 5))
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


    def start_exercise():
        global selected_exercise
        if selected_exercise is None:
            print("No exercise selected!")  # You can display a message instead
            return
        
        ex, sets, reps = selected_exercise
        exercise_function_mapping = {
        "Elbow Up Down": main.start_Elbow_Up_Down,
        "Arm Extension": main.start_Arm_Extension,
        "Wall Walk Left Hand": main.start_Wall_Walk_Left_Hand,
        "Standing Leg Front Lift": main.start_Standing_Leg_Front_Lift,
        "Single Leg Squat": main.start_Single_Leg_Squat,
        "Side Leg Raise": main.start_Side_Leg_Raise,
        "Side Box Step Ups": main.start_Side_Box_Step_Ups,
        "Front Box Step Ups": main.start_Front_Box_Step_Ups,
        "Step Reaction Training": main.start_Step_Reaction_Training,
        "Calf Stretch": main.start_Calf_Stretch,
        "Hamstring Stretch": main.start_Hamstring_Stretch,
        "Partial Wall Squat": main.start_Partial_Wall_Squat,
        "Seated Knee Extension": main.start_Seated_Knee_Extension,
    }

        if ex not in exercise_function_mapping:
            print(f"Exercise '{ex}' not found!")
            return

        start_function = exercise_function_mapping[ex]  # Get the function for the selected exercise
        video_path = main.exercise_videos.get(ex, "")

        if not video_path:
            print("No video found for this exercise.")
            return

        # Open a new window for exercise details
        new_window = ctk.CTkToplevel(app)
        new_window.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}") 
        new_window.attributes('-topmost', True)
        new_window.title(f"Exercise: {ex}")

        start_button=None
        def close_and_start():
            new_window.destroy()
            start_function()

        label = ctk.CTkLabel(new_window, text=f"Exercise: {ex}\nSets: {sets}\nReps: {reps}",
                            font=("Arial", 20, "bold"))
        label.pack(pady=20)

        def enable_start():
            if start_button:
                print("Enabling Start button after video ends.")
                start_button.configure(state="normal")

        start_button = ctk.CTkButton(
        new_window,
        text="Start Exercise",
        width=200,
        height=60,
        corner_radius=20,
        font=("Arial", 25, "bold"),
        fg_color="#39526D",
        text_color="#092E34",
        state="disabled",
        command=close_and_start
    )
        start_button.pack(pady=10)

        main.show_instructional_video(new_window, start_function, video_path, lambda: new_window.destroy())

        # Make sure Start button is enabled after video ends
        new_window.after(1000, enable_start) 
        

    ccanvas = ctk.CTkCanvas(pages["My Session"], width=1800, height=1000, bg="#CCDEE0", highlightthickness=0)
    ccanvas.place(x=0, y=0)
    #shadow circle
    
    cir_image = Image.open("assets_gui/cir_mysession.png").resize((1100, 800), Image.LANCZOS)
    cir_photo = ImageTk.PhotoImage(cir_image)
    ccanvas.create_image(1400,830,image=cir_photo)
    ccanvas.cirimage = cir_photo
    cir1_image = Image.open("assets_gui/cir_mysession.png").resize((1400, 900), Image.LANCZOS)
    cir1_photo = ImageTk.PhotoImage(cir1_image)
    ccanvas.create_image(500,1170,image=cir1_photo)
    ccanvas.cir1image = cir1_photo
    cir2_image = Image.open("assets_gui/cir2_mysession.png").resize((1200, 1200), Image.LANCZOS)
    cir2_photo = ImageTk.PhotoImage(cir2_image)
    ccanvas.create_image(1500,70,image=cir2_photo)
    ccanvas.cir2image = cir2_photo
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

    start_button = ctk.CTkButton(pages["My Session"], text="Start", width=100, height=45, corner_radius=20, fg_color="#092E34", bg_color="#39526D", font=('Arial', 23, 'bold'), command=start_exercise)
    start_button.place(x=620, y=715)

    
    # 🎨 **MY PROGRESS PAGE**
    progress_label = ctk.CTkLabel(pages["My Progress"], text="Therapy Progress", font=("Arial", 24, "bold"))
    progress_label.pack(pady=20)

    progress_chart = ctk.CTkFrame(pages["My Progress"], width=400, height=200, fg_color="white")
    progress_chart.pack(pady=20)
    progress_text = ctk.CTkLabel(progress_chart, text="📊 Progress Chart (Mock Data)", font=("Arial", 16))
    progress_text.pack()

    # 🎨 **NOTIFICATIONS PAGE**
    ncanvas = ctk.CTkCanvas(pages["Notifications"], width=3500, height=1100,bg = "#FFFFFF",bd = 0,highlightthickness = 0,relief = "ridge")
    ncanvas.place(x=0, y=0)
    back_image = Image.open("assets_gui/background.png").resize((3500, 2000), Image.LANCZOS)
    back_photo = ImageTk.PhotoImage(back_image)
    ncanvas.create_image(0,0,image=back_photo)
    ncanvas.backimage = back_photo
    circle_image = Image.open("assets_gui/circle.png").resize((1200, 900), Image.LANCZOS)
    circle_photo = ImageTk.PhotoImage(circle_image)
    ncanvas.create_image(10,10,image=circle_photo)
    ncanvas.circleimage = circle_photo
    circle2_image = Image.open("assets_gui/circle2.png").resize((1200, 900), Image.LANCZOS)
    circle2_photo = ImageTk.PhotoImage(circle2_image)
    ncanvas.create_image(1600,1000,image=circle2_photo)
    ncanvas.circle2image = circle2_photo
    box_image = Image.open("assets_gui/Box.png").resize((1200, 800), Image.LANCZOS)
    box_photo = ImageTk.PhotoImage(box_image)
    ncanvas.create_image(850,550,image=box_photo)
    ncanvas.boximage = box_photo
    ncanvas.create_text(950,16.5,anchor="nw",text="Notifications",fill="#000000",font=("Garamond", 60, 'bold'))
    bell_image = Image.open("assets_gui/bell.png").resize((125, 75), Image.LANCZOS)
    bell_photo = ImageTk.PhotoImage(bell_image)
    ncanvas.create_image(1450,55,image=bell_photo)
    ncanvas.bellimage = bell_photo


    scrollable_frame = ctk.CTkScrollableFrame(
    ncanvas,
    width=900,
    height=585,
    fg_color="#7F9B9E",
    bg_color="#7F9B9E"  # This lets the scrollable frame blend with its parent
)
    scrollable_frame.place(x=220, y=140)
    
    for date,messages in grouped_notifications.items():
        date_label = ctk.CTkLabel(scrollable_frame, text=date, font=("Georgia", 16, "bold"), text_color="#3D5051")
        date_label.pack(anchor="w", padx=10, pady=(10, 5))
        for type_,message in messages:
            fframe = ctk.CTkFrame(scrollable_frame, fg_color="#BBC4C5", corner_radius=5)
            fframe.pack(fill="x", pady=5, padx=5)

            title_label = ctk.CTkLabel(fframe, text=type_, font=("Georgia", 18, "bold"), text_color="black")
            title_label.pack(anchor="w", padx=10, pady=(5, 0))

            message_label = ctk.CTkLabel(fframe, text=message, font=("Georgia", 17), text_color="black", wraplength=250, justify="left")
            message_label.pack(anchor="w", padx=10, pady=(0, 5))

    # 🎨 **CONTACT PAGE**
    contact_label = ctk.CTkLabel(pages["Contact"], text="Contact Us", font=("Garamond", 60, "bold"))
    contact_label.place(x=40, y=60)
    
    mess_label = ctk.CTkLabel(pages["Contact"], text="Email, call, or complete the form to learn\nhow we can solve your messaging problem\n\ninfo@gmail.com\n\n321-221-331", font=("Georgia", 30), justify="left", anchor="w")
    mess_label.place(x=40, y=165)

    ncanvas = ctk.CTkCanvas(pages["Contact"], width=700, height=550,bg = "#CCDEE0",bd = 0,highlightthickness = 0,relief = "ridge")
    ncanvas.place(x=10, y=515)
    wbox_image = Image.open("assets_gui/white_box.png").resize((500, 400), Image.LANCZOS)
    wbox_photo = ImageTk.PhotoImage(wbox_image)
    ncanvas.create_image(300,250,image=wbox_photo)
    ncanvas.boximage = wbox_photo
    prof_image = Image.open("assets_gui/profile.png").resize((175, 125), Image.LANCZOS)
    prof_photo = ImageTk.PhotoImage(prof_image)
    ncanvas.create_image(305,50,image=prof_photo)
    ncanvas.profimage = prof_photo
    ncanvas.create_text(305, 120, text=dname, font=("Georgia", 23, "bold"), fill="black", anchor="center")
    ncanvas.create_text(305, 180, text=dhospital, font=("Georgia", 17), fill="black", anchor="center")
    ncanvas.create_text(100, 240, text=dprofession, font=("Georgia", 17), fill="black", anchor="w")  # Left-aligned
    ncanvas.create_text(500, 240, text=dinjury, font=("Georgia", 17), fill="black", anchor="e")  # Right-aligned
    ncanvas.create_text(80, 300, text="Email:", font=("Georgia", 17, "bold"), fill="black", anchor="w")
    ncanvas.create_text(270, 300, text=demail, font=("Georgia", 17), fill="black", anchor="w")
    ncanvas.create_text(80, 360, text="Phone number:", font=("Georgia", 17, "bold"), fill="black", anchor="w")
    ncanvas.create_text(270, 360, text=dphone, font=("Georgia", 17), fill="black", anchor="w")
        
    contact_form = ctk.CTkFrame(pages["Contact"], width=500, height=700, fg_color="white")
    contact_form.place(x=800,y=200)
    form_label = ctk.CTkLabel(contact_form, text="📝 Get in Touch with", font=("Garamond", 25, "bold"))
    form_label.pack(side="top", pady=10,expand=True)
    doc_label= ctk.CTkLabel(contact_form, text=dname, font=("Garamond", 22))
    doc_label.pack(side="top", pady=10,expand=True)

    contact_entry = ctk.CTkTextbox(contact_form, width=400, height=200, font=("Arial", 17))
    contact_entry.insert("0.0", "How can we help?")  # Placeholder text
    contact_entry.pack(pady=10)
    contact_entry.bind("<FocusIn>", lambda e: contact_entry.delete("1.0", "end") if contact_entry.get("1.0", "end-1c") == "How can we help?" else None)
    contact_entry.bind("<FocusOut>", lambda e: contact_entry.insert("1.0", "How can we help?") if contact_entry.get("1.0", "end-1c").strip() == "" else None)
    login_button = ctk.CTkButton(contact_form, text="Submit", width=200, height=45, corner_radius=20, fg_color="#092E34", bg_color="white", font=('Arial', 23, 'bold'))
    login_button.pack()
    dis_label = ctk.CTkLabel(contact_form, text="By contacting us, you agree to our Terms\nof service and Privacy Policy", font=("Arial", 12))
    dis_label.pack()
    # Show Default Page
    switch_page("Dashboard")

    
