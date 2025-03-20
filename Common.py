import numpy as np
import os
from pygame import mixer
import cv2
import time
import tkinter as tk
from exercise_state import exercise_status, stop_exercise_event
mixer.init()
stop_exercise=False
success_path = os.path.join("sounds", "success.wav")
success_sound = mixer.Sound(success_path)
countdown_path = os.path.join("sounds", "countdown.wav")
countdown_sound = mixer.Sound(countdown_path)
lower_path = os.path.join("sounds", "loweryourleg.wav")
lower_sound = mixer.Sound(lower_path)
upper_path = os.path.join("sounds", "goupper.wav")
upper_sound = mixer.Sound(upper_path)
golower_path = os.path.join("sounds", "golower.wav")
golower_sound = mixer.Sound(golower_path)
visible_path = os.path.join("sounds", "visible.wav")
visible_sound = mixer.Sound(visible_path)
ext_leg_path=os.path.join("sounds","ext_leg.wav")
ext_leg_sound=mixer.Sound(ext_leg_path)
bend_hip_path=os.path.join("sounds","bend_hip.wav")
bend_hip_sound=mixer.Sound(bend_hip_path)

great_path = os.path.join("sounds", "great.wav")
great_sound = mixer.Sound(great_path)

beep_path=os.path.join("sounds", "beep.wav")
beep_sound=mixer.Sound(beep_path)

goodjob_path=os.path.join("sounds", "Good_job_Keep_going.mp3")
goodjob_sound=mixer.Sound(goodjob_path)



# tutorial_path=os.path.join("poseVideos", "tutorial.mp4")
# tutorial=mixer.Sound(tutorial_path)

timer_duration = 6
is_timer_active = False
Hold_duration=10
stop_exercise = False
counter_box_height = 120
counter_box_width = 250
up_arrow = cv2.imread('C:/Users/Notnik_kg/Desktop/project1/PoseEstimation/poseVideos/up_arrow.png', cv2.IMREAD_UNCHANGED)
down_arrow = cv2.imread('C:/Users/Notnik_kg/Desktop/project1/PoseEstimation/poseVideos/down_arrow.png', cv2.IMREAD_UNCHANGED)
up_arrow_scale=0.5
down_arrow_scale=0.5
up_arrow_size = (int(up_arrow.shape[1] * up_arrow_scale), int(up_arrow.shape[0] * up_arrow_scale))
down_arrow_size = (int(down_arrow.shape[1] * down_arrow_scale), int(down_arrow.shape[0] * down_arrow_scale))
resized_up_arrow= cv2.resize(up_arrow, up_arrow_size, interpolation=cv2.INTER_AREA)
down_arrow = cv2.resize(down_arrow, down_arrow_size, interpolation=cv2.INTER_AREA)

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points a, b, and c.
    """
    a = np.array(a)  # First point
    b = np.array(b)  # Midpointf
    c = np.array(c)  # Endpoint

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    # Normalize the angle within [0, 180]
    if angle > 180.0:
        angle = 360 - angle

    return angle


def create_tkinter_window(exercise_name):
    root = tk.Tk()
    root.title("Control Panel")
    root.geometry("300x100")
    root.configure(bg="#C5EBE8")

    label = tk.Label(root, text="Exercise", font=("Arial", 14), bg="#C5EBE8", fg="#008878")
    label.pack(pady=10)

    btn_done = tk.Button(
        root,
        text="Done",
        command=lambda: [set_exercise_done(exercise_name), root.destroy()],
        font=("Arial", 14),
        bg="#FF6347",
        fg="white",
        width=10
    )
    btn_done.pack(pady=10)
    root.mainloop()

def set_exercise_done(exercise_name):
        if exercise_name in exercise_status:
            exercise_status[exercise_name] = True
            print(f"Exercise '{exercise_name}' marked as done.")
            stop_exercise_event.set()
        else:
            print(f"Exercise '{exercise_name}' not found.")
def stop_exercise_callback():
    x=0

def display_countdown(image, seconds_remaining):

        overlay = image.copy()
        alpha = 0.6  # Transparency factor

        # Create a semi-transparent rectangle for the countdown text
        cv2.rectangle(overlay, (0, 0), (image.shape[1], image.shape[0]), (0, 0, 0), -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        # Display the countdown number in the center of the screen
        cv2.putText(
            image,
            str(seconds_remaining),
            (image.shape[1] // 2 - 50, image.shape[0] // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            12,  # Font size
            (255, 255, 255),
            16,
            cv2.LINE_AA
        )

def perform_countdown(cap, countdown_sound, timer_duration, display_countdown, window_name="Exercise Countdown"):
    start_time = time.time()
    countdown_sound.play()

    while time.time() - start_time < timer_duration:
        ret, frame = cap.read()
        if not ret:
            print("Camera frame not available.")
            return False

        seconds_remaining = int(timer_duration - (time.time() - start_time))
        display_countdown(frame, seconds_remaining)
        cv2.imshow(window_name, frame)

        # Break loop if 'q' key is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            print("Countdown interrupted.")
            return False

    return True


def create_feedback_overlay(image, warning_message=None, counter=None, reps=None):
    """
    Add feedback overlays for warnings, counters, and repetitions.
    """
    overlay = image.copy()

    # Feedback box
    feedback_box_height = 80
    cv2.rectangle(overlay, (0, 0), (1280, feedback_box_height), (232, 235, 197), -1)

    # Counter box at bottom-left
    cv2.rectangle(overlay, (0, 720 - counter_box_height), (counter_box_width, 720), (232, 235, 197), -1)

    # Counter box at bottom-right
    cv2.rectangle(overlay, (1280 - counter_box_width, 720 - counter_box_height), (1280, 720), (232, 235, 197), -1)

    # Blend overlay with the original image to make boxes transparent
    alpha = 0.5  # Transparency factor
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Display warning message
    if warning_message:
        color = (0, 255, 0) if "Good Job! Keep going" in warning_message else (0, 255, 0)
        cv2.putText(image, warning_message, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3, cv2.LINE_AA)

    # Render counters
    if counter is not None:
        counter=int(counter)
        cv2.putText(image, str(counter), (20, 720 - 30), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 4, cv2.LINE_AA)
    if reps is not None:
        cv2.putText(image, "REPS", (1280 - counter_box_width , 720 - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(reps), (1280 - counter_box_width + 8, 720 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA)

    return image

def overlay_image_alpha(image, overlay, position, alpha_mask):#for arrows
    x, y = position
    h, w = overlay.shape[:2]
    h_image, w_image = image.shape[:2]

    # Ensure the overlay does not exceed the boundaries of the image
    if y + h > h_image:
        h = h_image - y
        overlay = overlay[:h, :, :]
        alpha_mask = alpha_mask[:h, :]
    if x + w > w_image:
        w = w_image - x
        overlay = overlay[:, :w, :]
        alpha_mask = alpha_mask[:, :w]

    # Blend the overlay with the image
    alpha = alpha_mask / 255.0
    for c in range(0, 3):
        image[y:y+h, x:x+w, c] = (
            alpha * overlay[:, :, c] + (1 - alpha) * image[y:y+h, x:x+w, c]
        )
