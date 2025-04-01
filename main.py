import tkinter as tk
import threading
import vlc
import os
import customtkinter as ctk
from PIL import Image, ImageTk  # For handling images/icons
from exercise_page import open_exercise_page
from video_utils import show_instructional_video
# Import your exercise modules
import Arm_Extension
import ElbowUpDown
import SideLegRaise
import Single_Leg_Squat
import wallWalk_leftHand
import Standing_LeftLeg_Front_Lift
import calf
#import calf_stretch
import Step_Reaction_Training
import Single_Leg_Squat
import Side_Box_Step_Ups
import Front_Box_Step_Ups
import Hamstring_Stretch
import Partial_Wall_Squat
import Seated_Knee_Extension
from exercise_ui import ExerciseUI

exercise_status={
    "Elbow Up Down":False,
    "Arm Extension":False,
    "Wall Walk Left Hand":False,
    "Standing_Leg_Front_Lift": False,
    "Single Leg Squat":False,
    "Side Leg Raise":False,
    "Side Box Step Ups": False,
    "Front Box Step Ups":False,
    "Step Reaction Training": False,
    "Calf Stretch": False,
    "Hamstring Stretch": False,
    "Partial Wall Squat": False,
    "Seated Knee Extension": False,
}
exercise_conditions = {
    "Elbow Up Down": lambda: exercise_status.get("Elbow Up Down", False),
    "Arm Extension": lambda: exercise_status.get("Arm Extension", False),
    "Wall Walk Left Hand": lambda: exercise_status.get("Wall Walk Left Hand", False),
    "Standing Leg Front Lift": lambda: exercise_status.get("Standing Leg Front Lift", False),
    "Single Leg Squat": lambda: exercise_status.get("Single Leg Squat", False),
    "Side Leg Raise": lambda: exercise_status.get("Side Leg Raise", False),
    "Side Box Step Ups": lambda: exercise_status.get("Side Box Step Ups", False),
    "Front Box Step Ups": lambda: exercise_status.get("Front Box Step Ups", False),
    "Step Reaction Training": lambda: exercise_status.get("Step Reaction Training", False),
    "Calf Stretch": lambda: exercise_status.get("Calf Stretch", False),
    "Hamstring Stretch": lambda: exercise_status.get("Hamstring Stretch", False),
    "Partial Wall Squat": lambda: exercise_status.get("Partial Wall Squat", False),
    "Seated Knee Extension": lambda: exercise_status.get("Seated Knee Extension", False)
}
video_path = r"C:\Users\Carl\Desktop\pose-estim\pose-estimation\poseVideos\tutorial.mp4"
#video_path = r"C:\Users\Notnik_kg\Desktop\PoseEstimation\poseVideos\6.mp4"

def create_fullscreen_window():
    win = tk.Toplevel()
    win.configure(bg="#C5EBE8")  # Match your CTk style if needed
    win.attributes('-fullscreen', True)
    #win.state("zoomed")
    win.update()
    return win


# Define a function to start exercises
def start_ElbowUpDown_Camera(exercise_frame):
    exercise_window = tk.Toplevel(exercise_frame.winfo_toplevel())
    exercise_window.attributes('-fullscreen', True)
    
    # Initialize ExerciseUI in the new window
    ui = ExerciseUI(exercise_window, title="Elbow Up Down")
    exercise = ElbowUpDown.ExerciseApp(ui)
    ui.set_callbacks(exercise.start_exercise, exercise.stop_exercise)
    exercise.start_exercise()
def start_Arm_Extension_Camera():
    x=0

def start_wallWalk_leftHand_Camera():
    def run():
        wallWalk_leftHand.run_exercise(exercise_status)
        if exercise_status["Wall Walk Left Hand"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Standing_Leg_Front_Lift():
    def run():
        Standing_LeftLeg_Front_Lift.run_exercise(exercise_status)
        if exercise_status["Standing Leg Front Lift"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Single_Leg_Squat():
    def run():
        Single_Leg_Squat.run_exercise(exercise_status)
        if exercise_status["Single Leg Squat"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_SideLegRaise_camera():
    def run():
        SideLegRaise.run_exercise(exercise_status)
        if exercise_status["Side Leg Raise"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Side_Box_Step_Ups():
    def run():
        Side_Box_Step_Ups.run_exercise(exercise_status)
        if exercise_status["Side Box Step Ups"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Front_Box_Step_Ups():
    def run():
        Front_Box_Step_Ups.run_exercise(exercise_status)
        if exercise_status["Front Box Step Ups"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Step_Reaction_Training():
    def run():
        Step_Reaction_Training.run_exercise(exercise_status)
        if exercise_status["Step Reaction Training"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_calf():
    def run():
        calf.run_exercise(exercise_status)
        if exercise_status["Calf Stretch"]:
            update_button_state()
    threading.Thread(target=run).start()

#def startcalf_stretch():
 #   threading.Thread(target=calf_stretch.run_exercise).start()

def start_Hamstring_Stretch():
    def run():
        Hamstring_Stretch.run_exercise(exercise_status)
        if exercise_status["Hamstring Stretch"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Partial_Wall_Squat():
    def run():
        Partial_Wall_Squat.run_exercise(exercise_status)
        if exercise_status["Partial Wall Squat"]:
            update_button_state()
    threading.Thread(target=run).start()

def start_Seated_Knee_Extension():
    def run():
        Seated_Knee_Extension.run_exercise(exercise_status)
        if exercise_status["Seated Knee Extension"]:
            update_button_state()
    threading.Thread(target=run).start()

def update_button_state():
    if exercise_status["Standing_Leg_Front_Lift"]:
        btn_leg_raise["bg"]="gray"
        btn_leg_raise["state"]="disabled"


"""def show_instructional_video(window, start_function):
    def play_video(video_path):
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return

        # VLC Instance
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(video_path)
        player.set_media(media)

        # Embed the video in the Tkinter Canvas
        player.set_hwnd(video_canvas.winfo_id())

        # Play the video
        player.play()

    # Clear the current window
    for widget in window.winfo_children():
        widget.destroy()

    # Video Canvas
    video_canvas = tk.Canvas(window, width=900, height=500, bg="black", highlightthickness=0)
    video_canvas.pack()

    # Start playing the video
    play_video(video_path)"""


# Function to clear the current window and show the main page again
def show_main_page(window):
    for widget in window.winfo_children():
        widget.destroy()

    # Add the title label
    title_label = tk.Label(
        window,
        text="My Pocket Physio",
        font=("Arial", 20, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=(30, 10))

    # Add a body of text
    body_text = tk.Label(
        window,
        text="Welcome to My Pocket Physio, the solution to all your body aches and injuries.",
        font=("Arial", 16),
        bg="#C5EBE8",
        fg="#008878",
        wraplength=700,
        justify="center"
    )
    body_text.pack(pady=(10, 30))

    # Add text for instructions
    instruction_text = tk.Label(
        window,
        text="Please select your injury type:",
        font=("Arial", 14),
        bg="#C5EBE8",
        fg="#008878"
    )
    instruction_text.pack(pady=20)

    # Add buttons for injury types
    btn_arm_injury = tk.Button(
        window,
        text="Arm Injury",
        command=lambda: open_injury_page(window, "Arm Injuries"),
        font=("Arial", 16),
        width=20,
        bg="#008878",
        fg="white"
    )
    btn_arm_injury.pack(pady=20)

    btn_knee_injury = tk.Button(
        window,
        text="Knee Injury",
        command=lambda: open_injury_page(window, "Knee Injuries"),
        font=("Arial", 16),
        width=20,
        bg="#008878",
        fg="white"
    )
    btn_knee_injury.pack(pady=20)

# Function to show injury pages (both arm and knee)
def open_injury_page(window, injury_type):
    # Clear the current window content
    for widget in window.winfo_children():
        widget.destroy()

    # Add the title for the injury page
    title_label = tk.Label(
        window,
        text=injury_type,
        font=("Arial", 18, "bold"),
        bg="#C5EBE8",
        fg="#008878"
    )
    title_label.pack(pady=20)

    global btn_leg_raise

    # Based on the injury type, show the corresponding exercises
    if injury_type == "Arm Injuries":
        exercises = [
            ("Elbow Up Down", lambda: show_instructional_video(window, lambda: start_ElbowUpDown_Camera(window))),
            ("Arm Extension", lambda: window.after(10, start_Arm_Extension_Camera)),
            ("Wall Walk Left Hand", start_wallWalk_leftHand_Camera)
        ]
    else:
        exercises = [
            ("Standing Leg Front Lift", lambda: show_instructional_video(window, start_Standing_Leg_Front_Lift)),
            ("Single Leg Squat", lambda: show_instructional_video(window, start_Single_Leg_Squat)),
            ("Side Leg Raise", lambda:show_instructional_video(window,start_SideLegRaise_camera)),
            ("Side Box Step Ups", lambda:show_instructional_video(window,start_Side_Box_Step_Ups)),
            ("Front Box Step Ups", lambda:show_instructional_video(window,start_Front_Box_Step_Ups)),
            ("Step Reaction Training", lambda: show_instructional_video(window, start_Step_Reaction_Training)),
            ("Calf Stretch", lambda: show_instructional_video(window,start_calf)),
            ("Hamstring Stretch", lambda: show_instructional_video(window,start_Hamstring_Stretch)),
            ("Partial Wall Squat", lambda: show_instructional_video(window,start_Partial_Wall_Squat)),
            ("Seated Knee Extension", lambda: show_instructional_video(window,start_Seated_Knee_Extension)),
        ]

      # Add buttons for exercises
    for text, command in exercises:
        # Determine the state and color dynamically for each exercise
        condition = exercise_conditions.get(text, lambda: False)()
        bg_color = "gray" if condition else "#008878"
        state = "disabled" if condition else "normal"
        
        btn = tk.Button(
            window,
            text=text,
            command=command,
            font=("Arial", 14),
            bg=bg_color,
            fg="white",
            width=22,
            state=state
        )
        btn.pack(pady=10)

    # Add a "Back" button to return to the main page
    btn_back = tk.Button(
        window,
        text="Back",
        command=lambda: show_main_page(window),
        font=("Arial", 14),
        bg="#008878",
        fg="white"
    )
    btn_back.pack(pady=20, anchor="w", padx=20)

# Main Window
def main():
    # Create the main application window
    root = create_fullscreen_window()

    # Show the main page
    show_main_page(root)

    # Start the main event loop
    root.mainloop()


if __name__ == "__main__":
    main()
