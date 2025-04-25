import customtkinter as ctk
from datetime import datetime, timedelta
from PIL import Image, ImageTk  # For handling images/icons
import tkinter as tk
import tkinter.messagebox as messagebox
from tkcalendar import Calendar
from firebase_config import db
import matplotlib.pyplot as plt
import io
from collections import defaultdict
from google.cloud import firestore
import tzlocal

local_tz=tzlocal.get_localzone()
sidebar_buttons={}
selected_dates = [] 
start_date=None
end_date=None
current_year=datetime.today().year
current_month=datetime.today().month
current_day=datetime.today().day
def create_doctor_page(app,current_user):
    
    doctor_id=current_user.get("doctor_id")
    def fetch_patients(doctor_id, status_filter=None):
        patients_ref=db.collection("patients").where("doctor_id","==", doctor_id)

        if status_filter and status_filter!="Total":
            patients_ref=patients_ref.where("status","==", status_filter)
        patients = patients_ref.stream()
        patients_list = [(p.to_dict().get("name"), 
                                p.to_dict().get("age"), 
                                p.to_dict().get("injury"),
                                p.to_dict().get("id")) for p in patients]        
        return patients_list
    def fetch_specific_patients(id):
        patients_ref=db.collection("patients").where("id","==", id)

        patients = patients_ref.stream()
        patients_list = [(p.to_dict().get("birthdate"), 
                                p.to_dict().get("injury"),
                                p.to_dict().get("chronic_conditions"),
                                p.to_dict().get("weight"),
                                p.to_dict().get("height")) for p in patients]        
        
        return patients_list[0] if patients_list else None
    
    def fetch_specific_exercises(id):
        exercises_ref=db.collection("exercises").where("patient_id","==", id)
        exercises = exercises_ref.stream()

        unique_exercises=set()
        exercises_list=[]

        for p in exercises:

            exercise_tuple = (p.to_dict().get("exercise_name"), 
                                p.to_dict().get("reps"),
                                p.to_dict().get("sets"),
                                p.to_dict().get("degrees_from"),
                                p.to_dict().get("degrees_to"),
                                p.id)   
            if exercise_tuple not in unique_exercises:
                unique_exercises.add(exercise_tuple)
                exercises_list.append(exercise_tuple)      
        
        return exercises_list if exercises_list else None
    
    def create_chat_room(doctor_id, patient_id):
        """ Creates a chat document for the doctor and patient if it does not exist """
        
        chat_id = f"{doctor_id}_{patient_id}"  # Unique chat ID for each doctor-patient chat
        chat_ref = db.collection("chats").document(chat_id)  # Reference to chat document

        if not chat_ref.get().exists:
            chat_ref.set({
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "created_at": datetime.now(tzlocal.get_localzone())
  # Store timestamp of chat creation
            })
            print(f"Chat room created for {doctor_id} and {patient_id}")
        else:
            print("Chat room already exists!")

    def send_message(doctor_id, patient_id, sender_id, text):
        """ Sends a message from sender_id (doctor or patient) to Firestore chat """
        
        chat_id = f"{doctor_id}_{patient_id}"
        chat_ref = db.collection("chats").document(chat_id)

        message = {
            "sender_id": sender_id,
            "text": text,
            "timestamp": datetime.now(tzlocal.get_localzone())
        }

        chat_ref.update({
            "messages": firestore.ArrayUnion([message])
        })

        print(f"Message sent: {text}")

    def listen_for_messages(doctor_id, patient_id, callback):
        """ Listens for new messages in a chat and calls the callback function """
        
        chat_id = f"{doctor_id}_{patient_id}"
        chat_ref = db.collection("chats").document(chat_id)

        def on_snapshot(doc_snapshot, changes, read_time):
            if doc_snapshot:
                doc = doc_snapshot[0] if isinstance(doc_snapshot, list) else doc_snapshot

                if doc.exists:
                    chat_data = doc.to_dict()
                    messages = chat_data.get("messages", [])  # Get all messages
                    messages.sort(
                        key=lambda x: x.get("timestamp") or datetime.min.replace(tzinfo=local_tz)
                    )
                    callback(messages) 
        chat_ref.on_snapshot(on_snapshot)
    
    for widget in app.winfo_children():
        widget.destroy() 
    
    main_frame = ctk.CTkFrame(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight(), fg_color="#CCDEE0")
    main_frame.place(x=0, y=0)
    def go_back_to_login():
        from second_page_login import create_login_page
        create_login_page(app)

    logout_button = ctk.CTkButton(app, text="Logout", font=("Arial", 23, "bold"), fg_color="#275057", bg_color="#CCDEE0",
                             text_color="white", corner_radius=20, width=150, height=50, command=go_back_to_login)
    logout_button.place(x=app.winfo_screenwidth()-200, y=app.winfo_screenheight()-135)

    # Sidebar Frame
    sidebar = ctk.CTkFrame(main_frame, width=180, fg_color="#CBE4E4", bg_color="#CBE4E4")
    sidebar.pack(side="left", fill="y")

    # Content Frame
    content = ctk.CTkFrame(main_frame)
    content.pack(side="right", fill="both", expand=True)

    # Dictionary for Frames (Pages)
    pages = {}

    # Create Frames (Pages)
    for page_name in ["Patients", "Add Patient", "Notifications","Treatment", "Appointments", "Specific Patient"]:
        if page_name=="Add Patient" or page_name=="Treatment":
            frame = ctk.CTkFrame(content, fg_color="#8FB8BC", width=1500, height=1100)
            frame.grid(row=0, column=0, sticky="nsew")
            pages[page_name] = frame
        else:
            frame = ctk.CTkFrame(content, fg_color="#BADDE0", width=1500, height=1100)
            frame.grid(row=0, column=0, sticky="nsew")
            pages[page_name] = frame

    # Function to switch pages
    def switch_page(page_name):
        for name, btn in sidebar_buttons.items():
            if name == page_name:
                btn.configure(fg_color="#93C0C2")  # Selected button
            else:
                btn.configure(fg_color="#CBE4E4")  # Not selected
        
        pages[page_name].tkraise()

        if page_name=="Add Patient":
            reset_form()
        elif page_name=="Appointments":
            setup_appointments_page()

    # Sidebar Buttons with Icons
    patients_icon=ctk.CTkImage(light_image=Image.open("assets_gui/patients.png"), size=(40,40))
    add_patient_icon=ctk.CTkImage(light_image=Image.open("assets_gui/add_patients.png"), size=(40,40))
    notifications_icon=ctk.CTkImage(light_image=Image.open("assets_gui/notifications_doctor.png"), size=(40,40))
    appointments_icon=ctk.CTkImage(light_image=Image.open("assets_gui/calendar.png"), size=(40,40))
    app_icon=ctk.CTkImage(light_image=Image.open("assets_gui/mini_logo.png"), size=(40,40))

    buttons = [
        ("Patients", patients_icon, lambda: switch_page("Patients")),
        ("Add Patient", add_patient_icon, lambda: switch_page("Add Patient")),
        ("Notifications", notifications_icon, lambda: switch_page("Notifications")),
        ("Appointments", appointments_icon, lambda: switch_page("Appointments"))
    ]
    icon_label = ctk.CTkLabel(sidebar,image=app_icon,compound='left', anchor='w', text="  PhysioEase", font=("Garamond", 30, "bold"), text_color="black")
    icon_label.pack(fill="x", pady=20,padx=10)
    for btn_text, icon, command in buttons:
        btn = ctk.CTkButton(sidebar, text=f"{btn_text}", image=icon,compound='left', anchor="w", height=50, fg_color="#CBE4E4", hover_color="#93C0C2",
                            corner_radius=30, command=lambda p=btn_text: switch_page(p), font=("Arial", 14, "bold"), text_color='black')
        btn.pack(fill="x", pady=7, padx=10)
        sidebar_buttons[btn_text] = btn

    # ✨✨✨PATIENTS PAGE✨✨✨
    def update_patient_list(choice):
        """Update the patient list based on selected status."""
        selected_status = filter_var.get()
        filtered_patients=fetch_patients(doctor_id, selected_status)
        display_patients(filtered_patients)

    ncanvas = ctk.CTkCanvas(pages["Patients"], width=3500, height=1100,bg = "#CCDEE0",bd = 0,highlightthickness = 0,relief = "ridge")
    ncanvas.place(x=0, y=0)
    circle_image = Image.open("assets_gui/cir_patients.png").resize((700, 900), Image.LANCZOS)
    circle_photo = ImageTk.PhotoImage(circle_image)
    ncanvas.create_image(app.winfo_screenwidth()+20,app.winfo_screenheight()+20,image=circle_photo)
    ncanvas.circleimage = circle_photo

    circle2_image = Image.open("assets_gui/cir2_patients.png").resize((600, 600), Image.LANCZOS)
    circle2_photo = ImageTk.PhotoImage(circle2_image)
    ncanvas.create_image(app.winfo_screenwidth()+20,-30,image=circle2_photo)
    ncanvas.circle2image = circle2_photo

    header_label = ctk.CTkLabel(pages["Patients"], text="Patient Overview", 
                                font=("Garamond", 30, "bold"), text_color="black", bg_color="#CCDEE0")
    header_label.place(x=300, y=30)

    filter_var = ctk.StringVar(value="In Progress")
    filter_menu = ctk.CTkComboBox(pages["Patients"], values=["Total", "In Progress", "Finished"],
                              command=update_patient_list, variable=filter_var,
                              font=("Georgia", 14), width=200)
    filter_menu.place(x=600, y=30)

    scrollable_frame = ctk.CTkScrollableFrame(pages["Patients"], fg_color="#6CA4A9",
                                            corner_radius=20, width=980, height=500)
    scrollable_frame.place(x=50,y=100)

    def display_patients(patients):
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        column_widths = [70,350, 80,250, 200]
        columns = ["#", "Name", "Age", "Injury", "ID"]
        for i, col_name in enumerate(columns):
            col_label = ctk.CTkLabel(scrollable_frame, text=col_name, 
                                    font=("Georgia", 16, "bold"), text_color="black",
                                    fg_color="#E0F2F1", width=column_widths[i], height=40)
            col_label.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)  


        def open_patient_view(patient_data):
            create_patient_view(app, patient_data)  # Open patient page when clicked

        for row_idx, patient in enumerate(patients, start=1):
            patient=(row_idx,)+patient
            for col_idx, value in enumerate(patient):
                cell_bg = "#F7FBFC" if row_idx % 2 == 0 else "#FFFFFF"  # Alternating row colors
                
                # If it's the patient name, make it clickable
                if col_idx == 1:
                    cell = ctk.CTkButton(scrollable_frame, text=value, font=("Georgia", 14, "bold"),
                                        text_color="#092E34", fg_color=cell_bg, hover_color="#D9D9D9",
                                        width=column_widths[col_idx], height=40,
                                        command=lambda p=patient: open_patient_view(p))
                else:
                    cell = ctk.CTkLabel(scrollable_frame, text=value, font=("Georgia", 14),
                                        text_color="black", fg_color=cell_bg,
                                        width=column_widths[col_idx], height=40)
                
                cell.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)
    display_patients(fetch_patients(doctor_id))

    # ✨✨✨SPECIFIC PATIENT PAGE✨✨✨
    def create_patient_view(app, patient_data):
        """ Opens a detailed view of the selected patient """
        for widget in pages["Specific Patient"].winfo_children():
            widget.destroy()
        
        def fetch_weekly_performance(patient_id):
            print(f"Fetching weekly performance patient:{patient_id}")
            reports_ref = db.collection("performance_reports").where("patient_id", "==", patient_id)
            reports = reports_ref.stream()

            weekly_summary = {}

            for report in reports:
                data = report.to_dict()
                timestamp = data.get("timestamp")

                if isinstance(timestamp, datetime):
                    year, week_num, _ = timestamp.isocalendar()
                    week_start = datetime.strptime(f"{year}-W{week_num}-1", "%G-W%V-%u").date()
                    week_end = week_start + timedelta(days=6)
                    week_key = f"{year}-W{week_num} ({week_start.strftime('%b %d')} – {week_end.strftime('%b %d')})"

                    if week_key not in weekly_summary:
                        weekly_summary[week_key] = {
                            "total_sessions": 0,
                            "total_reps": 0,
                            "total_movements": 0,
                            "total_duration": 0.0,
                            "warnings": [],
                            "sessions": [],
                            "sort_key": (year, week_num),
                            "exercise_details": {}  # <- Initialize exercise map
                        }

                    week_data = weekly_summary[week_key]
                    week_data["total_sessions"] += 1
                    week_data["total_reps"] += data.get("reps", 0)
                    week_data["total_movements"] += data.get("movements", 0)
                    week_data["total_duration"] += data.get("duration_seconds", 0)
                    week_data["warnings"].extend(data.get("warnings", []))

                    # Add session info
                    week_data["sessions"].append({
                        "reps": data.get("reps", 0),
                        "movements": data.get("movements", 0),
                        "duration": data.get("duration_seconds", 0),
                        "pain_level": data.get("pain_level", "N/A"),
                        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown"
                    })

                    # 🔥 Add per-exercise aggregation
                    exercise_name = data.get("exercise_name", "Unknown Exercise")
                    exercise_map = week_data["exercise_details"]
                    if exercise_name not in exercise_map:
                        exercise_map[exercise_name] = {"reps": 0, "duration": 0.0, "warnings": 0}
                    exercise_map[exercise_name]["reps"] += data.get("reps", 0)
                    exercise_map[exercise_name]["duration"] += data.get("duration_seconds", 0)
                    exercise_map[exercise_name]["warnings"] += len(data.get("warnings", []))

                else:
                    print("⚠️ Invalid timestamp format, skipping report")

            # Sort weeks chronologically
            sorted_week_items = sorted(weekly_summary.items(), key=lambda item: item[1]["sort_key"])
            sorted_weeks = [item[0] for item in sorted_week_items]

            # Compute deltas for reps and duration
            for i in range(1, len(sorted_weeks)):
                current_week = sorted_weeks[i]
                previous_week = sorted_weeks[i - 1]

                current = weekly_summary[current_week]
                previous = weekly_summary[previous_week]

                current["delta_reps"] = current["total_reps"] - previous["total_reps"]
                current["delta_duration"] = round(current["total_duration"] - previous["total_duration"], 2)

            if sorted_weeks:
                weekly_summary[sorted_weeks[0]]["delta_reps"] = None
                weekly_summary[sorted_weeks[0]]["delta_duration"] = None

            return weekly_summary



        def show_weekly_report_popup(week_key, data):

            popup = ctk.CTkToplevel()
            
            popup.title(f"Weekly Report - {week_key}")
            popup.geometry("550x500")
            popup.grab_set()  # Prevent clicking outside

            container=tk.Frame(popup, bg="white")

            canvas = tk.Canvas(container, width=580, height=520, background="white")
            scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, background="white")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            container.pack(fill="both", expand=True)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")


            ctk.CTkLabel(popup, text=f"📅 Weekly Report: {week_key}", font=("Garamond", 24, "bold")).pack(pady=10)

            # Summary Info
            summary_text = f"""Total Sessions: {data['total_sessions']}
        Total Reps: {data['total_reps']}
        Total Movements: {data['total_movements']}
        Total Duration: {int(data['total_duration']//60)} min {int(data['total_duration']%60)} sec
        Warnings Count: {len(data['warnings'])}"""

            if data.get("delta_reps") is not None:
                summary_text += f"\n🔄 Reps Δ: {data['delta_reps']:+}"
                summary_text += f"\n⏱️ Duration Δ: {int(data['delta_duration']//60)} min {int(data['delta_duration']%60)} sec"


            summary_label = ctk.CTkLabel(scrollable_frame, text=summary_text, font=("Georgia", 16), justify="left", anchor="w")
            summary_label.pack(padx=20, anchor="w")

            if "exercise_details" in data and data["exercise_details"]:
                exercise_details = data["exercise_details"]
                sorted_week_items = sorted(weekly_data.items(), key=lambda item: item[1]["sort_key"])
                all_weeks = [wk for wk, _ in sorted_week_items]

                options = ["Overall"] + list(exercise_details.keys())
                selected_option = tk.StringVar(value=options[0])

                ctk.CTkLabel(scrollable_frame, text="📂 Graph Mode:", font=("Georgia", 15)).pack(pady=(5, 0))
                dropdown = ctk.CTkComboBox(scrollable_frame, values=options, variable=selected_option, width=200)
                dropdown.pack(pady=(0, 10))

                chart_label_ex = tk.Label(scrollable_frame)
                chart_label_ex.pack(pady=(5, 20))

                def draw_chart():
                    option = selected_option.get()
                    sorted_items = sorted(weekly_data.items(), key=lambda item: item[1]["sort_key"])
                    all_weeks = [wk for wk, _ in sorted_items]

                    reps = []
                    durations = []

                    if option == "Overall":
                        reps = [weekly_data[w]["total_reps"] for w in all_weeks]
                        durations = [weekly_data[w]["total_duration"] / 60 for w in all_weeks]
                    else:
                        reps = [weekly_data[w]["exercise_details"].get(option, {}).get("reps", 0) for w in all_weeks]
                        durations = [weekly_data[w]["exercise_details"].get(option, {}).get("duration", 0) / 60 for w in all_weeks]

                    fig, axs = plt.subplots(1, 2, figsize=(15, 5))

                    # --- Reps Bar Chart ---
                    colors = []
                    for i in range(len(reps)):
                        if i == 0:
                            colors.append('gray')
                        else:
                            colors.append('green' if reps[i] > reps[i - 1] else 'red')
                    axs[0].bar(all_weeks, reps, color=colors)
                    axs[0].set_title(f"{option} Reps Over Time")
                    axs[0].tick_params(axis='x', rotation=45)

                    # --- Duration Line Chart ---
                    for i in range(1, len(durations)):
                        color = 'green' if durations[i] > durations[i - 1] else 'red'
                        axs[1].plot(all_weeks[i-1:i+1], durations[i-1:i+1], marker='o', color=color)
                    axs[1].plot(all_weeks[0], durations[0], marker='o', color='gray')
                    axs[1].set_title(f"{option} Duration Over Time (min)")
                    axs[1].set_ylabel('Duration (min)')
                    axs[1].tick_params(axis='x', rotation=45)

                    fig.tight_layout()
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)
                    img = Image.open(buf)
                    tk_img = ImageTk.PhotoImage(img)
                    chart_label_ex.configure(image=tk_img)
                    chart_label_ex.image = tk_img

                dropdown.bind("<<ComboboxSelected>>", lambda _: draw_chart())
                draw_chart()

            if data.get("sessions"):
                ctk.CTkLabel(scrollable_frame, text="📋 Session Details:", font=("Georgia", 18, "bold")).pack(padx=20, anchor="w", pady=(15, 5))
                session_box = ctk.CTkTextbox(scrollable_frame, height=160, width=500, font=("Georgia", 13))
                session_box.pack(padx=20, pady=(5, 10), fill="both", expand=False)

                header = f"{'Date':<20} {'Reps':<6} {'Moves':<8} {'Duration':<10} {'Pain'}\n"
                session_box.insert("1.0", header)
                session_box.insert("2.0", "-" * 60 + "\n")

                for session in data["sessions"]:
                    line = f"{session['timestamp']:<20} {session['reps']:<6} {session['movements']:<8} {int(session['duration']//60)}m {int(session['duration']%60)}s   {session['pain_level']}\n"
                    session_box.insert("end", line)

                session_box.configure(state="disabled")

            # Warnings Section
            if data["warnings"]:
                ctk.CTkLabel(scrollable_frame, text="⚠️ Warnings:", font=("Georgia", 18, "bold"), text_color="red").pack(padx=20, anchor="w", pady=(10, 0))

                warnings_box = ctk.CTkTextbox(scrollable_frame, height=100, width=480, font=("Georgia", 13), wrap="word")
                warnings_box.pack(padx=20, pady=(5, 10), fill="both", expand=False)

                warnings_box.insert("1.0", "\n".join(f"• {w}" for w in data["warnings"]))
                warnings_box.configure(state="disabled")
            else:
                ctk.CTkLabel(scrollable_frame, text="✅ No warnings for this week!", font=("Georgia", 16), text_color="green").pack(padx=20, anchor="w", pady=20)


            # Close Button
            ctk.CTkButton(scrollable_frame, text="Close", command=popup.destroy, fg_color="#275057", font=("Georgia", 14)).pack(pady=10)

        
        create_chat_room(doctor_id, patient_data[4])

        scanvas=ctk.CTkCanvas(pages["Specific Patient"], width=3500, height=1100,bg = "#CCDEE0",bd = 0,highlightthickness = 0,relief = "ridge")
        scanvas.place(x=0, y=0)

        specific_patient_info=fetch_specific_patients(patient_data[4])
        specific_exercises_info=fetch_specific_exercises(patient_data[4])

        circle1_image = Image.open("assets_gui/cir_pg2.png").resize((600, 900), Image.LANCZOS)
        circle1_photo = ImageTk.PhotoImage(circle1_image)
        scanvas.create_image(app.winfo_screenwidth()+20,50,image=circle1_photo)
        scanvas.circle1im = circle1_photo

        circle2_image = Image.open("assets_gui/cir_pg2.png").resize((600, 900), Image.LANCZOS)
        circle2_photo = ImageTk.PhotoImage(circle2_image)
        scanvas.create_image(app.winfo_screenwidth()+20,app.winfo_screenheight()-30,image=circle2_photo)
        scanvas.circle2im = circle2_photo

        #Calendar
        calendar_frame = ctk.CTkFrame(pages['Specific Patient'], fg_color="#8FB8BC", width=300, height=500)
        calendar_frame.place(x=630, y=500)      
        calendar = Calendar(calendar_frame, selectmode="day", font="Arial 17",
                        year=current_year, month=current_month, day=current_day, date_pattern="yyyy-mm-dd")
        calendar.grid(row=0, column=0, padx=10, pady=10)

        # Back Button
        back_button = ctk.CTkButton(scanvas, text="Back to Patients", 
                                    font=("Georgia", 14, "bold"), text_color="white",
                                    fg_color="#275057", width=200, height=40,
                                    command=lambda: switch_page("Patients"))
        back_button.place(x=760,y=740)

        chat_frame = ctk.CTkFrame(scanvas, fg_color="white", corner_radius=10, width=280, height=400)
        chat_frame.place(x=650, y=160)

        chat_textbox = ctk.CTkTextbox(chat_frame, width=300, height=270, font=("Georgia", 14), wrap="word")
        chat_textbox.pack(pady=10)
        def update_chat_ui(messages):
            """ Updates the chat UI with past and new messages """
            
            chat_textbox.delete("1.0", "end")  # Clear previous messages
            
            if not messages:
                chat_textbox.insert("end", "No messages yet. Send feedback to your patient here.\n")
                return
            previous_date=None

            for msg in messages:
                sender = "You" if msg['sender_id'] == doctor_id else "Patient"
                timestamp=msg.get('timestamp')
                # Convert timestamp to readable format
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.astimezone(local_tz)
                    msg_date = timestamp.strftime("%d %b %Y")
                    msg_time = timestamp.strftime("%I:%M %p")
                    
                else:
                    msg_date = "Unknown Date"
                    msg_time = "Unknown Time"
                if previous_date!=msg_date:
                    chat_textbox.insert("end", f"\n--- {msg_date} ---\n", "date")
                    previous_date=msg_date
                
                #message format
                message_bubble=f"{sender}:{msg['text']}       {msg_time}\n"
                
                # Tag messages for styling
                if sender == "You":
                    chat_textbox.insert("end", message_bubble, "doctor_msg")
                else:
                    chat_textbox.insert("end", message_bubble, "patient_msg")

            chat_textbox.see("end")

            # Apply styles
            chat_textbox.tag_config("doctor_msg", foreground="white", background="#007AFF", justify="right", font=("Arial", 12, "bold"))
            chat_textbox.tag_config("patient_msg", foreground="black", background="#E5E5EA", justify="left", font=("Arial", 12))
            chat_textbox.tag_config("date", foreground="gray", justify="center", font=("Arial", 10, "italic"))
                
        listen_for_messages(doctor_id, patient_data[4], update_chat_ui)
    
        message_entry = ctk.CTkEntry(chat_frame, width=220, font=("Arial", 14))
        message_entry.pack(side="left", padx=10, pady=10)

        def send_message_callback():
            text = message_entry.get()
            if text:
                send_message(doctor_id, patient_data[4], doctor_id, text)
                message_entry.delete(0, "end")

        send_button = ctk.CTkButton(chat_frame, text="Send",fg_color="#193E45",width=100, command=send_message_callback)
        send_button.pack(side="right", padx=2, pady=10)

        patient_name = patient_data[1]  # assuming patient_data tuple: (#, name, age, injury, id)
        patient_image=ctk.CTkImage(light_image=Image.open("assets_gui/specific_patient.png"), size=(100,100))
        header_label = ctk.CTkButton(scanvas,
                            text=f"{patient_name}  ", image=patient_image, compound='left', anchor='w',
                            font=("Garamond", 30, "bold"),
                            corner_radius=20,  
                            text_color="black",
                            fg_color="#7EB1B6", bg_color="transparent",
                            hover_color="#7EB1B6")  
        header_label.place(x=50, y=30)

        tab_frame = ctk.CTkFrame(scanvas, fg_color="white", corner_radius=10, width=450, height=50)
        tab_frame.place(x=50, y=160)        
        tabs = {
        "Personal Information": None,
        "Treatments": None,
        "Medical Record": None
    }
        
        def switch_tab(tab_name):
            """Switch between the details frames."""
            for name, frame in details_frames.items():
                if name == tab_name:
                    frame.place(x=50,y=220)
                    tabs[name].configure(fg_color="#7EB1B6")  # Highlight selected tab
                else:
                    frame.place_forget()
                    tabs[name].configure(fg_color="white")  # Reset other tabs

        for i, tab_name in enumerate(tabs.keys()):
            btn = ctk.CTkButton(tab_frame, text=tab_name, width=140, height=40,
                                font=("Arial", 14, "bold"), fg_color="white",
                                hover_color="#7EB1B6", text_color="black",
                                command=lambda name=tab_name: switch_tab(name))
            btn.grid(row=0, column=i, padx=5, pady=5)
            tabs[tab_name] = btn  # Store button reference

        # --- Details Frames ---
        details_frames = {}

        for section in ["Personal Information", "Treatments", "Medical Record"]:
            frame = ctk.CTkScrollableFrame(scanvas, fg_color="#BADDE0", corner_radius=10, width=500, height=300)
            frame.place(x=50, y=220)
            frame.pack_propagate(False)
            details_frames[section] = frame

            # Content for Each Tab
            if section == "Personal Information":
                labels=["Date of birth", "Injury type", "Chronic Conditions", "Weight", "Height"]

                for i in range(len(labels)):
                    ctk.CTkLabel(frame, text=labels[i], font=("Georgia", 18, "bold"), text_color="black").grid(row=i, column=0, padx=5, pady=5, sticky="w")
                    ctk.CTkLabel(frame, text=specific_patient_info[i], font=("Georgia", 18), text_color="black").grid(row=i, column=1, padx=20, pady=5, sticky="w")

            elif section == "Treatments":
                def save_changes(entries):
                    name_entry, reps_entry, sets_entry, from_entry, to_entry, index = entries
                    exercise_id = specific_exercises_info[index-1][-1]  # Assuming you store exercise IDs as the last element in the tuple

                    new_details = {
                        'exercise_name': name_entry.get(),
                        'reps': int(reps_entry.get()),
                        'sets': int(sets_entry.get()),
                        'degrees_from': int(from_entry.get()),
                        'degrees_to': int(to_entry.get())
                    }

                    # Update Firestore document
                    db.collection("exercises").document(exercise_id).update(new_details)
                    messagebox.showinfo("Modification", "Exercise Updated Successfully!")

                    print("Exercise updated successfully!")
                
                def highlight_on_calendar(exercise_id):
                    exercise_ref = db.collection("exercises").document(exercise_id)
                    exercise_details = exercise_ref.get().to_dict()

                    if not exercise_details:
                        print("Exercise details not found.")
                        return

                    calendar.calevent_remove('all')

                    def parse_date(date_str):
                        return datetime.strptime(date_str, '%Y-%m-%d').date()      

                    if 'date' in exercise_details:
                        date_obj=parse_date(exercise_details['date'])
                        calendar.calevent_create(date_obj, 'Exercise', tags="#D9B8A3")
                    elif 'dates' in exercise_details:  
                        for date_str in exercise_details['dates']:
                            date_obj = parse_date(date_str)
                            calendar.calevent_create(date_obj, 'Exercise', tags='#D9B8A3')
                    elif 'date_start' in exercise_details and 'date_end' in exercise_details: 
                        start_date = parse_date(exercise_details['date_start'])
                        end_date = parse_date(exercise_details['date_end'])
                        delta = timedelta(days=1)
                        while start_date <= end_date:
                            calendar.calevent_create(start_date, 'Exercise', tags="#D9B8A3")
                            start_date += delta

                    # Update calendar to show changes
                    calendar.tag_config("#D9B8A3", background='#D9B8A3')
                    calendar.update_idletasks()
                
                def delete_exercise(ex_id):
                    try:
                        db.collection("exercises").document(ex_id).delete()
                        messagebox.showinfo("Success", "Exercise Deleted Successfully!")
                        #refresh_ui()  
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete exercise: {str(e)}")


                labels=["Name","Reps","Sets","Degr-","-Degr"]
                for i in range(len(labels)):
                    ctk.CTkLabel(frame, text=labels[i], font=("Georgia", 18, "bold"), text_color="black").grid(row=0, column=i, padx=10, pady=5)
                
                
                for i, (name, reps,sets,from_,to_,ex_id) in enumerate(specific_exercises_info, start=1):
                    exercise_frame = ctk.CTkFrame(frame,fg_color="#BADDE0", width=600, height=150, corner_radius=10)
                    exercise_frame.grid(row=i, column=0, columnspan=6, padx=10, pady=10, sticky="w")

                    name_entry = ctk.CTkEntry(exercise_frame, textvariable=tk.StringVar(value=name), font=("Georgia", 18))
                    name_entry.grid(row=0, column=0, padx=5, pady=5, sticky="w")
                    reps_entry = ctk.CTkEntry(exercise_frame, textvariable=tk.StringVar(value=str(reps)),width=50, font=("Georgia", 18))
                    reps_entry.grid(row=0, column=1, padx=5, pady=5)
                    sets_entry = ctk.CTkEntry(exercise_frame, textvariable=tk.StringVar(value=str(sets)),width=50, font=("Georgia", 18))
                    sets_entry.grid(row=0, column=2, padx=5, pady=5)
                    from_entry = ctk.CTkEntry(exercise_frame, textvariable=tk.StringVar(value=str(from_)),width=50, font=("Georgia", 18))
                    from_entry.grid(row=0, column=3, padx=5, pady=5)
                    to_entry = ctk.CTkEntry(exercise_frame, textvariable=tk.StringVar(value=str(to_)),width=50, font=("Georgia", 18))
                    to_entry.grid(row=0, column=4, padx=(5,0), pady=5)
                    modify_button = ctk.CTkButton(exercise_frame,width=70, text="Update", command=lambda e=(name_entry, reps_entry, sets_entry, from_entry, to_entry, i): save_changes(e))
                    modify_button.grid(row=0, column=5, padx=(5,0), pady=5)
                    delete_button = ctk.CTkButton(exercise_frame, text="Delete",width=70, command=lambda ex_id=ex_id: delete_exercise(ex_id))
                    delete_button.grid(row=1, column=5, padx=(5,0), pady=5)
                    see_calendar_button = ctk.CTkButton(exercise_frame,width=90, text="See on Calendar", command=lambda ex_id=ex_id: highlight_on_calendar(ex_id))
                    see_calendar_button.grid(row=2, column=5, padx=(5,0), pady=5)
                    
                    

            elif section == "Medical Record":
                ctk.CTkLabel(frame, text="Plan", font=("Georgia", 18, "bold"), text_color="black").grid(row=0, column=0, padx=20, pady=5)
                ctk.CTkLabel(frame, text="Report", font=("Georgia", 18, "bold"), text_color="black").grid(row=0, column=1, padx=20, pady=5)

                weekly_data = fetch_weekly_performance(patient_data[4])  # real weekly report data

                for i, (week_key, data) in enumerate(sorted(weekly_data.items()),start=1):
                    ctk.CTkLabel(frame, text=week_key, font=("Georgia", 18), text_color="black").grid(row=i, column=0, padx=20, pady=5, sticky="w")
                    ctk.CTkButton(frame, text="View", width=100, command= lambda wk=week_key, d=data:show_weekly_report_popup(wk,d)).grid(row=i, column=1, padx=20, pady=5)

            # Set default active tab
        switch_tab("Personal Information")

        switch_page("Specific Patient")

    # ✨✨✨ ADD PATIENT PAGE✨✨✨
    acanvas = ctk.CTkCanvas(pages["Add Patient"], width=3500, height=1100,bg = "#8FB8BC",bd = 0,highlightthickness = 0,relief = "ridge")
    acanvas.place(x=0, y=0)
    circle3_image = Image.open("assets_gui/cir2_pg2.png").resize((700, 700), Image.LANCZOS)
    circle3_photo = ImageTk.PhotoImage(circle3_image)
    acanvas.create_image(app.winfo_screenwidth()-80,app.winfo_screenheight()+180,image=circle3_photo)
    acanvas.circle3image = circle3_photo

    circle2_image = Image.open("assets_gui/add_patient_cir2.png").resize((800, 700), Image.LANCZOS)
    circle2_photo = ImageTk.PhotoImage(circle2_image)
    acanvas.create_image(app.winfo_screenwidth()+10,app.winfo_screenheight()-190,image=circle2_photo)
    acanvas.circle2image = circle2_photo

    circle1_image = Image.open("assets_gui/add_patient_cir1.png").resize((700, 900), Image.LANCZOS)
    circle1_photo = ImageTk.PhotoImage(circle1_image)
    acanvas.create_image(app.winfo_screenwidth()+60,app.winfo_screenheight()+20,image=circle1_photo)
    acanvas.circle1image = circle1_photo

    form_frame = ctk.CTkFrame(pages["Add Patient"], fg_color="#8FB8BC")
    form_frame.place(x=20, y=50)

    def create_entry(row,column, placeholder):
        entry = ctk.CTkEntry(form_frame, width=250, height=40, fg_color="#C7DCDD",
                            font=("Georgia", 20), corner_radius=30, text_color="black", border_color="black")  # Set text color to black
        entry.grid(row=row, column=column, padx=(60,0), pady=20)
        entry.insert(0, placeholder)  # Insert placeholder text
        entry.bind("<FocusIn>", lambda event: on_entry_click(event, entry, placeholder))
        entry.bind("<FocusOut>", lambda event: on_focus_out(event, entry, placeholder))
        return entry

    # Creating the entry fields
    first_name = create_entry(0,1, "First Name")
    last_name = create_entry(1,1, "Last Name")
    username = create_entry(2,1, "Username")
    #Birthdate
    def month_to_number(month_name):
        months = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
            "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        return months.get(month_name, "00")
    
    ctk.CTkLabel(form_frame, text="Birthdate", font=("Georgia",18)).grid(row=3, column=0, padx=10, pady=5)
    date = ctk.CTkOptionMenu(form_frame, values=[str(i) for i in range(1, 32)], fg_color="#C7DCDD", font=("Georgia",20), corner_radius=30, text_color="black")
    date.grid(row=3, column=1, padx=5)
    month = ctk.CTkOptionMenu(form_frame, values=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], fg_color="#C7DCDD", text_color="black", font=("Georgia",20), corner_radius=30)
    month.grid(row=3, column=2, padx=5)
    year = ctk.CTkComboBox(form_frame, values=[str(i) for i in range(1925, 2025)],fg_color="#C7DCDD", font=("Georgia",20), corner_radius=30, text_color="black")
    year.grid(row=3, column=3, padx=5)
    year.set("2000")
    identification=create_entry(4,1,"Identification No.")
    injury_type = create_entry(5,1, "Injury Type")
    chronic_conditions = create_entry(6,1, "Chronic Conditions")
    weight = create_entry(7,1, "Weight (kg)")
    height = create_entry(7,2, "Height (cm)")

    def on_entry_click(event, entry, placeholder):
        """Removes placeholder text when the entry is clicked."""
        if entry.get() == placeholder:
            entry.delete(0, "end")  # Remove text
            entry.configure(text_color="black")  # Change user text color

    def on_focus_out(event, entry, placeholder):
        """Restores placeholder text if the entry is empty."""
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.configure(text_color="black")
    def reset_form():
        entries = [
            (first_name, "First Name"), 
            (last_name, "Last Name"),
            (username, "Username"),
            (identification, "Identification No."), 
            (injury_type, "Injury Type"),
            (chronic_conditions, "Chronic Conditions"),
            (weight, "Weight (kg)"),
            (height, "Height (cm)")
        ]
        
        # Reset Text Entries
        for entry, placeholder in entries:
            entry.delete(0, "end")
            entry.insert(0, placeholder)
            entry.configure(text_color="black")  # Make placeholder text gray
        
        # Reset Dropdowns
        date.set("1")
        month.set("Jan")
        year.set("2000")

    def add_patient():
        def calculate_age(year, month, day):
            today = datetime.today()
            birthdate = datetime(year=int(year), month=int(month), day=int(day))
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            return age
        day = date.get().zfill(2)
        patients_ref = db.collection("patients")
        def get_valid_text(entry, placeholder):
            return "" if entry.get() == placeholder else entry.get()
        # Collect Data from Entry Fields
        month_num=month_to_number(month.get())
        patient_data = {
            "first_name": get_valid_text(first_name, "First Name"),
            "last_name": get_valid_text(last_name, "Last Name"),
            "username": get_valid_text(username, "Username"),
            "birthdate": f"{month.get()} {day}, {year.get()}",
            "id": get_valid_text(identification, "Identification No."),
            "injury": get_valid_text(injury_type, "Injury Type"),
            "chronic_conditions": get_valid_text(chronic_conditions, "Chronic Conditions"),
            "weight": get_valid_text(weight, "Weight (kg)"),
            "height": get_valid_text(height, "Height (cm)"),
            "doctor_id": doctor_id,
            "name":f"{get_valid_text(first_name, "First Name")} {get_valid_text(last_name, "Last Name")}",
            "age": calculate_age(year.get(), month_num, day),
            "status":"In Progress"
        }
        patients_ref.add(patient_data)
        users_ref=db.collection("users")
        user_data={
            "username":get_valid_text(username, "Username"),
            "role":"patient",
            "password":f"{year.get()}.{month_num}.{day}"
        }
        users_ref.add(user_data)
        messagebox.showinfo("Success", "Patient Added Successfully!")

        print("Patient Added Successfully!")
    
    treatment_btn=ctk.CTkButton(pages["Add Patient"], text="Set Treatment",font=("Garamond", 18), width=150, height=40, command=lambda: check_patient_before_treatment(identification.get()))
    treatment_btn.place(x=500, y=650)
    submit_btn = ctk.CTkButton(pages["Add Patient"], text="Add Patient", width=150,font=("Garamond", 18), height=40, command=add_patient)
    submit_btn.place(x=500, y=700)

    # ✨✨✨ TREATMENT PAGE✨✨✨
    def check_patient_before_treatment(patient_id):
            if not patient_id or patient_id=="identification No.":
                messagebox.showerror("Error", "Please enter a valid Identification Number.")
                return 
            patient_ref = db.collection("patients").where("id", "==", patient_id).stream()
            existing_patient = None
            for patient in patient_ref:
                existing_patient = patient.to_dict() 
                break 

            if existing_patient:
                set_treatment(app, patient_id)  
            else:
                messagebox.showerror("Error", "Patient not found. Please add the patient first.")
                
    def set_treatment(app, patient_id):
        """ Set treatment plan of the created patient """
        def create_entry(row, column, placeholder, parent):
            entry = ctk.CTkEntry(parent, width=250, height=40, fg_color="#D2E3E4",
                                font=("Georgia", 20), corner_radius=30, text_color="black", border_color="black")
            entry.grid(row=row, column=column, padx=(60,0), pady=25)
            entry.insert(0, placeholder)  # Insert placeholder text
            entry.bind("<FocusIn>", lambda event: on_entry_click(event, entry, placeholder))
            entry.bind("<FocusOut>", lambda event: on_focus_out(event, entry, placeholder))
            return entry

        for widget in pages["Treatment"].winfo_children():
            widget.destroy()

        tcanvas=ctk.CTkCanvas(pages["Treatment"], width=3500, height=1100,bg = "#8FB8BC",bd = 0,highlightthickness = 0,relief = "ridge")
        tcanvas.pack(fill="both", expand=True)

        circle3_image = Image.open("assets_gui/cir2_pg2.png").resize((700, 700), Image.LANCZOS)
        circle3_photo = ImageTk.PhotoImage(circle3_image)
        tcanvas.create_image(app.winfo_screenwidth()-80,app.winfo_screenheight()+180,image=circle3_photo)
        tcanvas.circle3image = circle3_photo

        circle2_image = Image.open("assets_gui/add_patient_cir2.png").resize((800, 700), Image.LANCZOS)
        circle2_photo = ImageTk.PhotoImage(circle2_image)
        tcanvas.create_image(app.winfo_screenwidth()+10,app.winfo_screenheight()-190,image=circle2_photo)
        tcanvas.circle2image = circle2_photo

        circle1_image = Image.open("assets_gui/add_patient_cir1.png").resize((700, 900), Image.LANCZOS)
        circle1_photo = ImageTk.PhotoImage(circle1_image)
        tcanvas.create_image(app.winfo_screenwidth()+60,app.winfo_screenheight()+20,image=circle1_photo)
        tcanvas.circle1image = circle1_photo

        treatment_header = ctk.CTkLabel(pages["Treatment"], text="Set Treatment Plan",
                                    font=("Garamond", 30, "bold"), text_color="black", bg_color="#8FB8BC")
        treatment_header.place(x=400, y=30)

        form_frame = ctk.CTkFrame(pages["Treatment"], fg_color="#8FB8BC")
        form_frame.place(x=50, y=80)

        # Injury Type
        injury_entry = create_entry(0, 1, "Injury Type", form_frame)

        # Exercise Selection
        ctk.CTkLabel(form_frame, text="Exercise", font=("Georgia", 20)).grid(row=1, column=0, padx=10, pady=5)
        exercise_menu = ctk.CTkOptionMenu(form_frame, values=[
            "Arm Extension", "Front Box Step Ups", "Hamstring Stretch",
            "Partial Wall Squat", "Seated Knee Extension", "Side Box Step Up",
            "Side Leg Raise", "Step Reaction", "Standing Left Leg Front Lift","Wall Walk Left Hand",
            "Calf Stretch","Elbow Up Down"], fg_color="#D2E3E4", font=("Georgia", 20), corner_radius=30, text_color="black")
        exercise_menu.grid(row=1, column=1, padx=5, pady=5)

        # Sets & Reps
        reps_entry = create_entry(2, 1, "Reps", form_frame)
        sets_entry = create_entry(2, 2, "Sets", form_frame)

        # Degree (From - To)
        ctk.CTkLabel(form_frame, text="Degree", font=("Georgia", 20)).grid(row=3, column=0, padx=10, pady=5)
        from_entry = create_entry(3, 1, "From", form_frame)
        to_entry = create_entry(3, 2, "To", form_frame)

        calendar_frame = ctk.CTkFrame(pages["Treatment"], fg_color="#8FB8BC", width=500, height=500)
        calendar_frame.place(x=30, y=400)
        button_frame = ctk.CTkFrame(calendar_frame, fg_color="#8FB8BC")
        button_frame.grid(row=0, column=1, padx=20, pady=10)        
        calendar = Calendar(calendar_frame, selectmode="day", font="Arial 17",background="#99C0C4",foreground="black",
                        headersbackground="#004D40",headersforeground="white",selectbackground="#00796B",selectedforeground="white",
                        normalbackground="#B2DFDB",normalforeground="black",
                        year=current_year, month=current_month, day=current_day, date_pattern="yyyy-mm-dd")
        calendar.grid(row=0, column=0, padx=10, pady=10)
        
        selected_dates_label = ctk.CTkLabel(calendar_frame, text="Selected Dates: None", fg_color="#D2E3E4", text_color="black",font=("Georgia",16))
        selected_dates_label.grid(row=1, column=0, columnspan=2, pady=5)
        #Single date
        def get_selected_date():
            selected_date = calendar.get_date()
            if selected_date not in selected_dates:
                selected_dates.append(selected_date)
            selected_dates_label.configure(text=f"Selected Date: {selected_date}")
            print("Selected Date:", selected_date)
        
        #Multiple Dates
        def add_selected_date():
            selected_date = calendar.get_date()
            if selected_date not in selected_dates:
                selected_dates.append(selected_date)
            selected_dates_label.configure(text=f"Selected Dates: {', '.join(selected_dates)}")
            print("Selected Dates:", selected_dates)

        #Date Range
        def get_date_range():
            global start_date, end_date
            if start_date is None:
                start_date = calendar.get_date()
                selected_dates_label.configure(text=f"Start Date: {start_date}\nSelect End Date")
            else:
                end_date = calendar.get_date()
                selected_dates_label.configure(text=f"Selected Range: {start_date} to {end_date}")
                messagebox.showinfo("Selected Date Range", f"Date Range: {start_date} to {end_date}")            
        single_date_btn = ctk.CTkButton(button_frame, text="Select Single Date", fg_color="#004D40",command=get_selected_date)
        single_date_btn.grid(row=0, column=0, pady=5, sticky="w")

        multiple_dates_btn = ctk.CTkButton(button_frame, text="Add Multiple Dates",fg_color="#004D40", command=add_selected_date)
        multiple_dates_btn.grid(row=1, column=0, pady=5, sticky="w")

        range_dates_btn = ctk.CTkButton(button_frame, text="Select Date Range",fg_color="#004D40", command=get_date_range)
        range_dates_btn.grid(row=2, column=0, pady=5, sticky="w")

        # Reset Selection Button
        def reset_dates():
            global selected_dates
            selected_dates = []
            selected_dates_label.configure(text="Selected Dates: None")
            if start_date in globals():
                del globals()[start_date]
            messagebox.showinfo("Reset", "All dates have been reset.")
            print("All dates have been reset.")
        def add_treatment():
            exercise_ref=db.collection("exercises")
            def get_valid_text(entry, placeholder):
                if exercise_menu.get() not in ["Step Reaction"]:
                    if entry.get() == placeholder or entry.get()=="":
                        messagebox.showerror("Error", f"{placeholder} is missing.")
                        return
                    else:
                        return entry.get()
                if placeholder=="From" or placeholder=="To":
                    return "" if entry.get() == placeholder else entry.get()
                else:
                    if entry.get() == placeholder or entry.get()=="":
                        messagebox.showerror("Error", f"{placeholder} is missing.")
                        return
                    else:
                        return entry.get()

            
            exercise_data={
                "doctor_id": doctor_id,
                "exercise_name":exercise_menu.get(),
                "patient_id":patient_id,
                "reps":get_valid_text(reps_entry, "Reps"),
                "sets":get_valid_text(sets_entry, "Sets"),
                "degrees_from":get_valid_text(from_entry,"From"),
                "degrees_to":get_valid_text(to_entry,"To")
            }
            if len(selected_dates)==1:
                exercise_data["date"]=selected_dates[0]
            elif len(selected_dates)>1:
                exercise_data["dates"]=selected_dates
            elif start_date and end_date:
                exercise_data["date_start"]=start_date
                exercise_data["date_end"]=end_date
            else:
                messagebox.showerror("Error", "Please select a date before adding the treatment.")
                return
            
            exercise_ref.add(exercise_data)
            messagebox.showinfo("Success", "Exercise Added Successfully!")

        reset_btn = ctk.CTkButton(button_frame, text="Reset Selection",fg_color="#004D40", command=reset_dates)
        reset_btn.grid(row=3, column=0, pady=5, sticky="w")

        add_btn = ctk.CTkButton(tcanvas, text="Add Exercise",fg_color="#004D40",height=40, width=150,corner_radius=20,font=('Arial', 23, 'bold'), command=lambda:add_treatment())
        add_btn.place(x=60,y=740)

        
        back_button = ctk.CTkButton(tcanvas, text="Back", 
                                    font=("Georgia", 14, "bold"), text_color="white",
                                    fg_color="#275057", width=200, height=40,
                                    command=lambda: switch_page("Add Patient"))
        back_button.place(x=700,y=740)

        switch_page("Treatment")
    

    # ✨✨✨ APPOINTMENT PAGE✨✨✨

    def setup_appointments_page():
        page = pages["Appointments"]
        for widget in page.winfo_children():
            widget.destroy()

        # === Header ===
        ctk.CTkLabel(page, text="Appointments", font=("Garamond", 30, "bold"), text_color="black", bg_color="#BADDE0").pack(pady=20)

        layout_frame = ctk.CTkFrame(page, fg_color="#BADDE0")
        layout_frame.pack(pady=10)

        # === Left: Create Appointment ===
        create_frame = ctk.CTkFrame(layout_frame, fg_color="white", width=500)
        create_frame.grid(row=0, column=0, padx=20, sticky="n")
        ctk.CTkLabel(create_frame, text="Create Appointment", font=("Georgia", 20, "bold")).pack(pady=10)

        # Patient ID
        patient_id_entry = ctk.CTkEntry(create_frame, placeholder_text="Patient ID", width=300)
        patient_id_entry.pack(pady=5)

        # Patient Name
        patient_name_entry = ctk.CTkEntry(create_frame, placeholder_text="Patient Name", width=300)
        patient_name_entry.pack(pady=5)

        # Date Picker (tkcalendar)
        ctk.CTkLabel(create_frame, text="Select Date", font=("Georgia", 14)).pack(pady=(10, 0))
        cal = Calendar(create_frame, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(pady=5)

        # Time Selection
        ctk.CTkLabel(create_frame, text="Select Time", font=("Georgia", 14)).pack(pady=(10, 0))

        # Example time slots
        time_options = [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
            "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
            "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM"
        ]
        time_var = tk.StringVar(value="09:00 AM")
        time_menu = ctk.CTkOptionMenu(create_frame, variable=time_var, values=time_options)
        time_menu.pack(pady=5)



        def add_appointment():
            patient_id = patient_id_entry.get()
            patient_name = patient_name_entry.get()
            date = cal.get_date()
            time=time_var.get()

            if not patient_id or not patient_name:
                messagebox.showerror("Error", "Please fill all fields.")
                return

            db.collection("appointments").add({
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "patient_name": patient_name,
                "date": date,
                "time":time,
                "status": "Pending"
            })

            messagebox.showinfo("Success", f"Appointment created for {patient_name} on {date}")
            load_appointments()

        ctk.CTkButton(create_frame, text="Create", fg_color="#275057", text_color="white", command=add_appointment).pack(pady=15)

        # === Right: View Appointments ===
        view_frame = ctk.CTkScrollableFrame(layout_frame, fg_color="#BADDE0", width=800, height=600)
        view_frame.grid(row=0, column=1, padx=20, sticky="n")
        def load_appointments():
            for widget in view_frame.winfo_children():
                widget.destroy()

            appts = db.collection("appointments").where("doctor_id", "==", doctor_id).order_by("date").order_by("time").stream()

            for doc in appts:
                appt = doc.to_dict()
                appt_id = doc.id
                if appt.get('status')!="Completed":
                    card = ctk.CTkFrame(view_frame, fg_color="white", corner_radius=15)
                    card.pack(fill="x", padx=10, pady=10)

                    lines = [
                        f"Appointment ID: {appt_id}",
                        f"Patient Name: {appt.get('patient_name', 'N/A')}",
                        f"Patient ID: {appt.get('patient_id', 'N/A')}",
                        f"Date: {appt.get('date', 'N/A')}",
                        f"Time: {appt.get('time', 'N/A')}",
                        f"Status: {appt.get('status', 'Pending')}"
                    ]
                    for line in lines:
                        ctk.CTkLabel(card, text=line, font=("Georgia", 14), text_color="black", anchor="w").pack(anchor="w", padx=10)

                    ctk.CTkLabel(card, text="Update Status:", font=("Georgia", 13)).pack(anchor="w", padx=10, pady=(5, 0))
                    status_var = tk.StringVar(value=appt.get("status", "Pending"))
                    status_menu = ctk.CTkOptionMenu(card, variable=status_var, values=["Pending", "Approved", "Rejected", "Completed"])
                    status_menu.pack(anchor="w", padx=10)

                    def save_status(svar=status_var, doc_id=appt_id):
                        db.collection("appointments").document(doc_id).update({"status": svar.get()})
                        messagebox.showinfo("Updated", f"Status updated to {svar.get()}")
                        load_appointments()

                    ctk.CTkButton(card, text="Save", width=100, fg_color="#275057", text_color="white", command=save_status).pack(anchor="e", padx=10, pady=5)

        load_appointments()

    #✨✨✨NOTIFICATIONS PAGE✨✨✨
    def fetch_notifications(doctor_id):
        chat_docs = db.collection("chats").where("doctor_id", "==", doctor_id).stream()
        notifications = defaultdict(list)
        patient_cache = {}

        for chat in chat_docs:
            chat_data = chat.to_dict()
            patient_id = chat_data.get("patient_id")

            # Cache the patient name lookup
            if patient_id not in patient_cache:
                patient_ref = db.collection("patients").where("id", "==", patient_id).limit(1).stream()
                for p in patient_ref:
                    patient_cache[patient_id] = p.to_dict().get("name", "Unknown")
                if patient_id not in patient_cache:
                    patient_cache[patient_id] = "Unknown"

            patient_name = patient_cache[patient_id]
            messages = chat_data.get("messages", [])

            for msg in messages:
                if msg["sender_id"] != doctor_id:
                    timestamp = msg.get("timestamp")
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.astimezone(local_tz)
                        date_key = timestamp.strftime("%d %b %Y")
                        time_str = timestamp.strftime("%I:%M %p")
                    else:
                        date_key = "Unknown Date"
                        time_str = "Unknown Time"

                    label = f"Message from {patient_name} (ID: {patient_id})"
                    notifications[date_key].append((label, f"{msg['text']} ({time_str})"))

        return dict(notifications)

    notifications = fetch_notifications(doctor_id)

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
        width=(app.winfo_screenwidth()/2)+145,
        height=(app.winfo_screenheight()/2)+145,
        fg_color="#7F9B9E",
        bg_color="#7F9B9E"
    )
    scrollable_frame.place(x=app.winfo_screenwidth()/7, y=140)

    for date, messages in notifications.items():
        date_label = ctk.CTkLabel(scrollable_frame, text=date, font=("Georgia", 16, "bold"), text_color="#3D5051")
        date_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        for type_, message in messages:
            fframe = ctk.CTkFrame(scrollable_frame, fg_color="#BBC4C5", corner_radius=5)
            fframe.pack(fill="x", pady=5, padx=5)

            title_label = ctk.CTkLabel(fframe, text=type_, font=("Georgia", 18, "bold"), text_color="black")
            title_label.pack(anchor="w", padx=10, pady=(5, 0))

            message_label = ctk.CTkLabel(fframe, text=message, font=("Georgia", 17), text_color="black", wraplength=250, justify="left")
            message_label.pack(anchor="w", padx=10, pady=(0, 5))





    switch_page("Patients")


