import cv2
import mediapipe as mp
import time
import threading
import numpy as np
from pygame import mixer
from Common import *
from exercise_ui import *
import tkinter as tk
from tkinter import Label

# Global variable to control the exercise loop
stop_exercise = False

class ExerciseApp:
    def __init__(self, ui):
        self.ui = ui
        self.root = self.ui.root
        # self.root.geometry("1400x800")
        self.root.attributes('-fullscreen', True)

        # Get screen width and height for scaling elements
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        print(f"{screen_height}*{screen_width}")
        video_width = int(screen_width * 0.85)
        video_height = int(screen_height * 0.85)
        x_position = (screen_width - video_width) // 2
        y_position = 20  # or adjust as needed
        self.video_label = Label(self.root)
        self.video_label.place(x=x_position, y=y_position, width=video_width, height=video_height)

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # resolution of the camera
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.2, min_tracking_confidence=0.2, model_complexity=0)

        self.stop_exercise_flag = False

    def perform_countdown_ui(self):
        start_time = time.time()
        countdown_sound.play()  # Play the countdown sound

        # Run the countdown loop for timer_duration seconds
        while time.time() - start_time < timer_duration:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera frame not available.")
                return False

            # Calculate seconds remaining and draw the overlay on the frame
            seconds_remaining = int(timer_duration - (time.time() - start_time))
            display_countdown(frame, seconds_remaining)

            # Convert frame to format compatible with Tkinter
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)

            # Update the video_label with the countdown frame
            self.video_label.config(image=img_tk)
            self.video_label.image = img_tk  # Avoid garbage collection

            self.root.update()
            time.sleep(0.03)  # Adjust delay as needed

        return True

    def start_exercise(self):
        # Perform the countdown using the video_label (no separate window)
        if self.perform_countdown_ui():
            self.stop_exercise_flag = False
            threading.Thread(target=self.run_exercise, daemon=True).start()
        else:
            print("Countdown was interrupted. Exercise not started.")

    def stop_exercise(self):
        self.stop_exercise_flag = True

    def quit_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()

    def run_exercise(self):
        counter, reps, stage = 0, 0, None
        stage = 'up'
        timer_duration = 6
        warning_message = None
        last_lower_sound_time = None
        timer_remaining = timer_duration
        is_timer_active = False
        last_beep_time = None
        stop_exercise = False
        hold_timer = 5  # Timer for holding the "good position"
        hold_start_time = None
        posture_correct = False
        last_good_job_time = None
        good_job_display = False
        sets = 0
        successful_holds = 0  # Counter to count successful holds

        while self.cap.isOpened() and not self.stop_exercise_flag:
            ret, frame = self.cap.read()
            if not ret:
                break
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            warning_message = None

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Get coordinates for hip, knee, and ankle
                    hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                           landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    # Calculate angle
                    angle = calculate_angle(hip, knee, ankle)

                    # Display angle on the frame
                    cv2.putText(image, f"Angle: {int(angle)}",
                                tuple(np.multiply(knee, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Feedback and repetition logic
                    if 115 <= angle <= 140:  # Wall squat position (approximately 45 degrees)
                        posture_correct = True
                        if hold_start_time is None:
                            hold_start_time = time.time()
                        elapsed = time.time() - hold_start_time
                        hold_remaining = hold_timer - elapsed

                        if hold_remaining > 0:
                            warning_message = f"Hold: {int(hold_remaining)} seconds remaining"
                        else:
                            # Completed hold
                            counter += 1  # Increment successful hold count
                            hold_start_time = None

                            if counter == 3:  # Every 3 successful holds, increment reps
                                reps += 1  # Increment rep count
                                print(f"Reps: {reps}")
                                success_sound.play()
                                time.sleep(0.2)
                                good_job_display = True
                                goodjob_sound.play()
                                last_good_job_time = time.time()
                                warning_message = "Great job! Hold again for next rep."
                                counter = 0  # Reset the hold counter after 3 successful holds

                    else:
                        posture_correct = False
                        hold_start_time = None

            except Exception as e:
                warning_message = "Pose not detected. Make sure full body is visible."
                print("Error:", e)
                current_time = time.time()
                if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                    visible_sound.play()
                    last_lower_sound_time = current_time

            if good_job_display and last_good_job_time:
                if time.time() - last_good_job_time <= 5:
                    warning_message = "Good Job! Keep Going"
                else:
                    good_job_display = False

            # Draw pose landmarks on the image
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                                           self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2,
                                                                       circle_radius=2),
                                           self.mp_drawing.DrawingSpec(
                                               color=(44, 42, 196) if (stage in ['too_high', 'too_low']) else (
                                                   67, 196, 42),
                                               thickness=2, circle_radius=2)
                                           )

            # Ensure hold_remaining is initialized to avoid UnboundLocalError
            if hold_start_time is None or not posture_correct:
                hold_remaining = hold_timer  # Default hold time when posture is incorrect or not started
            else:
                elapsed = time.time() - hold_start_time
                hold_remaining = max(0, hold_timer - elapsed)

            image = create_feedback_overlay(image, warning_message=warning_message, counter=counter, reps=reps)

            # Update the Tkinter UI with the frame
            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (1280, 720))  # Resize to fit the video window
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            photo = tk.PhotoImage(data=cv2.imencode('.png', img)[1].tobytes())
            self.video_label.config(image=photo)
            self.video_label.image = photo
            self.root.update()

            if self.stop_exercise_flag:
                break

        self.cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)


if __name__ == "__main__":
    root = tk.Tk()
    ui = ExerciseUI(root, title="Partial Wall Squat")
    exercise = ExerciseApp(ui)

    ui.set_callbacks(exercise.start_exercise, exercise.stop_exercise)

    root.mainloop()
