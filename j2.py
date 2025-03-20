import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import tkinter as tk
import os
from pygame import mixer

from tkinter import Button, Label
from Common import *
from exercise_ui import *
from exercise_state import stop_exercise_event

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

        self.video_label = Label(self.root)
        self.video_label.place(x=300, y=20, width=1280, height=720)  # Adjust size as needed and placement


        # self.start_button = Button(self.root, text="Start", command=self.start_exercise)
        # self.start_button.place(x=400, y=1020, width=120, height=50)
        #
        # self.stop_button = Button(self.root, text="Stop", command=self.stop_exercise)
        # self.stop_button.place(x=900, y=1020, width=120, height=50)
        #
        # self.quit_button = Button(self.root, text="Finish", command=self.quit_app)
        # self.quit_button.place(x=1400, y=1020, width=120, height=50)


        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) #resolution of the camera
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.2, min_tracking_confidence=0.2, model_complexity=0)

        self.stop_exercise_flag = False

    def start_exercise(self):
        self.stop_exercise_flag = False
        threading.Thread(target=self.run_exercise, daemon=True).start()

    def stop_exercise(self):
        self.stop_exercise_flag = True

    def quit_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()

    def run_exercise(self):
        counter, reps, stage = 0, 0, None
        tot_count = 5
        warning_message = None
        last_lower_sound_time = None
        last_good_job_time = None
        good_job_display = False

        while self.cap.isOpened() and not self.stop_exercise_flag:
            ret, frame = self.cap.read()
            if not ret:
                break
            # frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            warning_message = None

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Check if required ones are detected
                    required_landmarks = {
                        'Left Shoulder': self.mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                        'Left Elbow': self.mp_pose.PoseLandmark.LEFT_ELBOW.value,
                        'Left Wrist': self.mp_pose.PoseLandmark.LEFT_WRIST.value

                    }
                    missing_landmarks = []
                    for name, idx in required_landmarks.items():
                        visibility = landmarks[idx].visibility
                        if visibility < 0.5 or np.isnan(landmarks[idx].x) or np.isnan(landmarks[idx].y):
                            missing_landmarks.append(name)

                    if missing_landmarks:
                        warning_message = f"Adjust Position: {', '.join(missing_landmarks)} not detected!"
                        current_time = time.time()
                        if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                            visible_sound.play()
                            last_lower_sound_time = current_time

                    else:
                        landmarks = results.pose_landmarks.landmark
                        shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                 landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                        angle = calculate_angle(shoulder, elbow, wrist)
                        # visualize the angle at elbow
                        frame_height, frame_width, _ = image.shape  # Get actual frame size

                        cv2.putText(image, str(int(angle)),
                                    tuple(np.multiply(elbow, [frame_width, frame_height]).astype(int)),  # Use actual size
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                        if angle > 140:
                            stage = "down"
                        if angle < 40 and stage == 'down':
                            stage = "up"
                            counter += 1
                            beep_sound.play()
                            if counter % 5 == 0 and counter != 0:  # Every 5 counts, increase reps
                                reps += 1
                                counter = 0
                                success_sound.play()
                                time.sleep(0.2)
                                good_job_display = True
                                goodjob_sound.play()
                                last_good_job_time = time.time()

                else:
                    warning_message = "Pose not detected. Make sure full body is visible."
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time
            except Exception as e:
                warning_message = "Pose not detected."
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

            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS, self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                           self.mp_drawing.DrawingSpec(
                                               color=(44, 42, 196) if (stage in ['too_high', 'too_low']) else (
                                               67, 196, 42),
                                               thickness=2, circle_radius=2)
                                           )

            image = create_feedback_overlay(image, warning_message=warning_message, counter=counter, reps=reps)

            img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (1280, 720))#1920, 1000
            # img = cv2.flip(img, 1)
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
    ui = ExerciseUI(root, title="Elbow Exercise")
    exercise = ExerciseApp(ui)

    ui.set_callbacks(exercise.start_exercise, exercise.stop_exercise)

    root.mainloop()
