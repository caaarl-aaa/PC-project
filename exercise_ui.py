import cv2
import tkinter as tk
from tkinter import Button, Label, ttk
from PIL import Image, ImageTk

class ExerciseUI:
    def __init__(self, root, title="Exercise App"):
        self.root = root
        self.root.title(title)
        self.root.attributes('-fullscreen', True)
        self.style = ttk.Style()

        # Get screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Video display label
        self.video_label = Label(self.root)
        self.video_label.place(x=0, y=0, width=self.screen_width, height=int(self.screen_height * 0.6))

        # Exercise description background
        label_width = int(self.screen_width * 0.6)
        label_height = int(self.screen_height * 0.2)
        label_x = (self.screen_width - label_width) // 2
        label_y = int(self.screen_height * 0.65)

        # Exercise video above the description
        self.exercise_video_label = Label(self.root)
        self.exercise_video_label.place(x=label_x, y=label_y - 180, width=label_width, height=150)

        # Exercise description text
        self.exercise_text = (
            "Sit or stand with your back straight. "
            "Bend your elbows at a 90-degree angle. "
            "Lift your elbows up to shoulder height. "
            "Lower them back down slowly. Repeat 10-15 times."
        )

        self.exercise_label = Label(
            self.root,
            text=self.exercise_text,
            font=("Arial", 16, "bold"),
            fg="black",
            bg="white",
            wraplength=label_width - 50,
            padx=40, pady=30
        )
        self.exercise_label.place(x=label_x, y=label_y, width=label_width, height=label_height)

        # Button colors
        self.default_color = "#84A6AA"
        self.hover_color = "#A5C1C4"

        # Create buttons
        button_y = self.screen_height - 100
        self.start_button = self.create_button("Start", self.screen_width * 0.25, button_y, self.start_exercise)
        self.stop_button = self.create_button("Stop", self.screen_width * 0.5, button_y, self.stop_exercise)
        self.quit_button = self.create_button("Finish", self.screen_width * 0.75, button_y, self.quit_app)

        # Placeholder functions
        self.start_exercise_callback = None
        self.stop_exercise_callback = None

        # Load and display the exercise video
        self.cap = cv2.VideoCapture("exercise.mp4")  # Replace with actual video file
        self.update_exercise_video()

    def create_button(self, text, x, y, command):
        button = Button(self.root, text=text, command=command,
                        bg=self.default_color, fg="black", font=("Arial", 15, "bold"),
                        relief="flat", width=20, height=2)
        button.place(x=int(x - 60), y=y, width=120, height=50)
        button.bind("<Enter>", lambda event: button.config(bg=self.hover_color))
        button.bind("<Leave>", lambda event: button.config(bg=self.default_color))
        return button

    def set_callbacks(self, start_callback, stop_callback):
        self.start_exercise_callback = start_callback
        self.stop_exercise_callback = stop_callback

    def start_exercise(self):
        """ Hide description and video when starting exercise """
        self.exercise_label.place_forget()
        self.exercise_video_label.place_forget()
        if self.start_exercise_callback:
            self.start_exercise_callback()

    def stop_exercise(self):
        if self.stop_exercise_callback:
            self.stop_exercise_callback()

    def quit_app(self):
        self.cap.release()
        self.root.quit()

    def update_exercise_video(self):
        """ Update the exercise video frame """
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (int(self.screen_width * 0.6), 150))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.exercise_video_label.config(image=imgtk)
            self.exercise_video_label.image = imgtk
            self.root.after(30, self.update_exercise_video)  # Update every 30ms
        else:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
            self.update_exercise_video()