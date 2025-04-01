import customtkinter as ctk
import tkinter as tk
from video_utils import show_instructional_video
from ElbowUpDown import ExerciseApp
from exercise_ui import ExerciseUI

def open_exercise_page(app, page_container, exercise_name, sets, reps, start_function, current_user=None):
    # Clear existing widgets in the page container
    for widget in page_container.winfo_children():
        widget.destroy()

    # Create the embedded exercise page
    exercise_frame = ctk.CTkFrame(page_container, fg_color="white", corner_radius=20)
    exercise_frame.pack(fill="both", expand=True)

    # Title Label
    title_label = ctk.CTkLabel(exercise_frame, text=f"Exercise: {exercise_name}\nSets: {sets}\nReps: {reps}",
                             font=("Arial", 24, "bold"))
    title_label.pack(pady=10)

    # Video Frame
    video_frame = ctk.CTkFrame(exercise_frame, width=1000, height=600, fg_color="#D9D9D9")
    video_frame.pack(pady=10)

    def start_exercise():
        # Create a new Toplevel window for the exercise
        exercise_window = tk.Toplevel(page_container.winfo_toplevel())
        exercise_window.attributes('-fullscreen', True)
        
        # Initialize ExerciseUI in the new window
        ui = ExerciseUI(exercise_window, title=exercise_name)
        exercise = ExerciseApp(ui)
        def safe_stop():
            exercise.stop_exercise()
            exercise_window.destroy()
        
        ui.set_callbacks(exercise.start_exercise, safe_stop)
        
        # Make sure window close triggers cleanup
        exercise_window.protocol("WM_DELETE_WINDOW", safe_stop)

    # Start Exercise Button
    start_button = ctk.CTkButton(
        exercise_frame,
        text="Start Exercise",
        width=200,
        height=50,
        corner_radius=15,
        font=("Arial", 20, "bold"),
        fg_color="#39526D",
        text_color="white",
        command=start_exercise
    )
    start_button.pack(pady=20)

    def go_back_to_session():
        from third_page import create_third_page
        # Use the passed current_user or create a default if not provided
        user = current_user or {"patient_id": "default_id"}
        create_third_page(app, user)
    
    # Back Button
    back_button = ctk.CTkButton(
        exercise_frame,
        text="← Back",
        width=200,
        height=50,
        corner_radius=15,
        font=("Arial", 20, "bold"),
        fg_color="#39526D",
        text_color="white",
        command=go_back_to_session
    )
    back_button.pack(pady=20)


    show_instructional_video(video_frame, lambda: start_function(exercise_frame) if start_function else start_exercise())
