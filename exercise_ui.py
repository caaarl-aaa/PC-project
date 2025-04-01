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
        print("Screen size (from screen):", self.screen_width, self.screen_height)
        video_width = int(self.screen_width)  # e.g., 60% of the screen width
        video_height = int(self.screen_height)
        x_position = (self.screen_width - video_width) // 2
        y_position = 0
        # Video display label
        self.video_label = Label(self.root)
        self.video_label.place(x=x_position, y=y_position, width=video_width, height=video_height)
        # Exercise description text
        self.exercise_text = (
            "Sit or stand with your back straight. "
            "Bend your elbows at a 90-degree angle. "
            "Lift your elbows up to shoulder height. "
            "Lower them back down slowly. Repeat 10-15 times."
        )

        # Make background square bigger
        label_width = int(self.screen_width * 0.4)  # 60% of screen width
        label_height = int(self.screen_height * 0.2)  # 30% of screen height (bigger)
        label_x = (self.screen_width - label_width) // 2
        label_y = int(self.screen_height * 0.65)  # Positioned below video area

        # Smaller text inside the bigger square
        self.exercise_label = Label(
            self.root,
            text=self.exercise_text,
            font=("Arial", 16, "bold"),  # Smaller text
            fg="black",
            bg="white",
            wraplength=label_width - 50,  # Wrap text properly
            padx=40, pady=30  # Add more padding for space
        )
        self.exercise_label.place(x=label_x, y=label_y, width=label_width, height=label_height)

        # Button colors
        self.default_color = "#84A6AA"
        self.hover_color = "#A5C1C4"

        # Create buttons
        button_y = self.screen_height - 100  # Buttons near the bottom
        self.start_button = self.create_button("Start", self.screen_width * 0.25, button_y, self.start_exercise)
        self.stop_button = self.create_button("Stop", self.screen_width * 0.5, button_y, self.stop_exercise)
        self.quit_button = self.create_button("Finish", self.screen_width * 0.75, button_y, self.quit_app)

        # Placeholder functions
        self.start_exercise_callback = None
        self.stop_exercise_callback = None
    def update_video_frame(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (self.screen_width, int(self.screen_height * 0.6)))
        img = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=img_tk)
        self.video_label.image = img_tk  # Avoid garbage collection
        self.root.update()
    def create_button(self, text, x, y, command):
        """ Helper function to create buttons with hover effect """
        button = Button(self.root, text=text, command=command,
                        bg=self.default_color, fg="black", font=("Arial", 15, "bold"),
                        relief="flat", width=20, height=2)

        button.place(x=int(x - 60), y=y, width=120, height=50)  # Center buttons

        # Add hover effect
        button.bind("<Enter>", lambda event: button.config(bg=self.hover_color))  # Change to hover color
        button.bind("<Leave>", lambda event: button.config(bg=self.default_color))  # Restore original color

        return button

    def set_callbacks(self, start_callback, stop_callback):
        """ Set callback functions for buttons """
        self.start_exercise_callback = start_callback
        self.stop_exercise_callback = stop_callback
        self.start_button.config(command=self.start_exercise)
        self.stop_button.config(command=self.stop_exercise)
    def start_exercise(self):
        """ Hide description and start exercise """
        if self.start_exercise_callback:
            self.start_exercise_callback()

    def stop_exercise(self):
        if self.stop_exercise_callback:
            self.stop_exercise_callback()

    def quit_app(self):
        print("Finish button clicked")
        if self.stop_exercise_callback:
            self.stop_exercise_callback()
        print("Camera should be released now")
        self.root.destroy()
