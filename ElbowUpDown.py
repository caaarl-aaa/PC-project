import cv2
import mediapipe as mp
import numpy as np
import threading
import time
import tkinter as tk
from tkinter import Label, Toplevel, Scale, Button
from Common import *
from exercise_ui import *
from exercise_state import stop_exercise_event
from firebase_config import db
from datetime import datetime, timezone

# Global variable to control the exercise loop
stop_exercise = False


class ExerciseApp:
    def __init__(self, ui, current_user):
        self.ui = ui
        self.current_user=current_user
        self.patient_id = current_user.get("patient_id", "unknown")
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
        self.performance_doc_id=None
    
    def log_performance_to_firebase(self, reps, total_movements, warnings, start_time, end_time, duration_seconds, formatted_duration):
        print("entered log")
        data = {
            "patient_id": self.patient_id,
            "exercise_name": "Elbow Up Down",
            "start_time": start_time,
            "end_time": end_time,
            "duration_seconds": duration_seconds,
            "formatted_duration":formatted_duration,
            "date": start_time.strftime("%Y-%m-%d"),
            "time": start_time.strftime("%H:%M:%S"),
            "reps": reps,
            "movements": total_movements,
            "warnings": warnings,
            "timestamp": datetime.now(timezone.utc),  # for querying by recency
            "pain_level":None
        }

        try:
            doc_ref=db.collection("performance_reports").add(data)
            self.performance_doc_id=doc_ref[1].id
            print(f"✅ Performance report saved for patient {self.patient_id}")
            return True
        except Exception as e:
            print(f"❌ Error saving to Firebase: {e}")
            return False
    def ask_pain_level(self):
        """Create a popup window to ask for pain level"""
        print("enter ask_pain")
        pain_window = Toplevel(self.root)
        pain_window.title("Pain Level Feedback")
        pain_window.attributes('-fullscreen', True)
        
        # Center the window
        screen_width = pain_window.winfo_screenwidth()
        screen_height = pain_window.winfo_screenheight()
        
        # Create main container
        container = tk.Frame(pain_window)
        container.pack(expand=True, fill='both')
        
        # Add title
        title_label = tk.Label(container, text="How was your pain level during the exercise?", 
                             font=("Arial", 24))
        title_label.pack(pady=50)
        
        # Add scale (0-10)
        pain_scale = Scale(container, from_=0, to=10, orient='horizontal', 
                          length=screen_width*0.6, font=("Arial", 18),
                          tickinterval=1, showvalue=True)
        pain_scale.pack(pady=50)
        
        # Add submit button
        def submit_pain_level():
            pain_level = pain_scale.get()
            self.update_pain_level_in_firebase(pain_level)
            pain_window.destroy()
            
            if self.cap:
                self.cap.release()
                self.cap = None
                cv2.destroyAllWindows()
                cv2.waitKey(1)
            self.root.destroy()
            
        submit_btn = Button(container, text="Submit", command=submit_pain_level,
                          font=("Arial", 18), width=20, height=2)
        submit_btn.pack(pady=50)
        
        # Make sure the window is on top
        pain_window.grab_set()
        pain_window.focus_set()

    def update_pain_level_in_firebase(self, pain_level):
        """Update the document with the pain level"""
        if self.performance_doc_id:
            try:
                db.collection("performance_reports").document(self.performance_doc_id).update({
                    "pain_level": pain_level,
                    "pain_timestamp": datetime.now(timezone.utc)
                })
                print(f"✅ Pain level {pain_level} saved to document {self.performance_doc_id}")
            except Exception as e:
                print(f"❌ Error updating pain level: {e}")
        else:
            print("⚠️ No document ID available to update pain level")
        
    
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
        if self.cap:
            self.cap.release()
            self.cap = None
        cv2.destroyAllWindows()

    def quit_app(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.root.quit()

    def run_exercise(self):
        
        counter, reps, stage = 0, 0, None
        warning_message = None
        warning_list=[]
        last_lower_sound_time = None
        last_good_job_time = None
        good_job_display = False
        start_time= datetime.now()

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
                        if warning_message not in warning_list:
                            warning_list.append(warning_message)
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
                    if warning_message not in warning_list:
                        warning_list.append(warning_message)
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time
            except Exception as e:
                warning_message = "Pose not detected."
                if warning_message not in warning_list:
                    warning_list.append(warning_message)
                print("Error:", e)
                current_time = time.time()
                if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                    visible_sound.play()
                    last_lower_sound_time = current_time

            if good_job_display and last_good_job_time:
                    if time.time() - last_good_job_time <= 5:
                        warning_message = "Good Job! Keep Going"
                        warning_list.append(warning_message)
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
            try:
                if self.video_label.winfo_exists():
                    self.video_label.config(image=photo)
                    self.video_label.image = photo
            except tk.TclError as e:
                print("❌ Window was closed before update:", e)
                break  # Stop the thread to avoid further crashing

            self.root.update()

            if self.stop_exercise_flag or not self.video_label.winfo_exists():
                break

        
        
        end_time=datetime.now()
        duration_seconds = (end_time - start_time).total_seconds()
        duration_minutes=int(duration_seconds//60)
        duration_remainder_seconds=int(duration_seconds%60)
        formatted_duration = f"{duration_minutes} min {duration_remainder_seconds} sec"
        
        success=self.log_performance_to_firebase(
            reps=reps,
            total_movements=reps * 5 + counter,
            warnings=warning_list,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration_seconds,  # ✅ Store as float
            formatted_duration=formatted_duration  # ✅ Optional, display use only
        )

        if success:
            self.root.after(0,self.ask_pain_level)
        


if __name__ == "__main__":
    root = tk.Tk()
    ui = ExerciseUI(root, title="Elbow Exercise")
    exercise = ExerciseApp(ui)

    ui.set_callbacks(exercise.start_exercise, exercise.stop_exercise)

    root.mainloop()
