"""""Half Circle Arm Extension on wall"""
import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from Common import *
from exercise_state import stop_exercise_event

# Global variable to control the exercise loop
stop_exercise = False

def run_exercise(exercise_status):
    global stop_exercise

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap=cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Arm Extension', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Arm Extension', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    counter = 0
    stage = None
    warning_message=None
    last_lower_sound_time=None
    timer_remaining = None
    is_timer_active = False
    last_beep_time=None
    sets = 0

    threading.Thread(target=create_tkinter_window, daemon=True).start()
    
    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Arm Extension"
    )

    # Set flag after countdown
    countdown_complete = True   

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Arm Extension"] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            warning_message = None  # Reset warning message for each frame
# Extract pose landmarks
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Filter out landmarks with low visibility
                    visibility_threshold = 0.6
                    required_landmarks = {
                        mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                        mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                        #mp_pose.PoseLandmark.LEFT_WRIST.value,
                        mp_pose.PoseLandmark.RIGHT_WRIST.value,
                        #mp_pose.PoseLandmark.LEFT_ELBOW.value
                    }
                    visible_landmarks = [lm for idx, lm in enumerate(landmarks) if idx in required_landmarks and lm.visibility > visibility_threshold]
                    # Ensure key landmarks are detected
                    if len(visible_landmarks) < len(required_landmarks):
                        warning_message = "Ensure full body visibility!"
                        current_time = time.time()
                        if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                            visible_sound.play()
                            last_lower_sound_time = current_time
                    else:
                        rightshoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                        leftwrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
                        rightwrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                        leftshoulder= [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        leftelbow= [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        # Calculate angles
                        angle = calculate_angle(leftwrist, rightshoulder, rightwrist)
                        left_arm_angle=calculate_angle(leftelbow, leftshoulder,rightshoulder)
                        cv2.putText(image, str(int(angle)),
                            tuple(np.multiply(rightshoulder, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, str(int(left_arm_angle)),
                            tuple(np.multiply(leftshoulder, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (44, 42, 196), 2, cv2.LINE_AA)
                       
                        # Exercise logic with state machine
                        # Ensure left leg is raised
                        if left_arm_angle>160:
                            if angle >160:
                                stage='start'
                                warning_message='Good form! Keep it up!'
                            elif angle < 70 and stage == "start":
                                stage = "down"
                                counter += 1
                                beep_sound.play()
                                warning_message = "Complete Circle Down"
                                feedback_locked = True
                                if counter == 6:
                                    sets += 1
                                    success_sound.play()
                                    counter = 0
                            elif angle < 40 or angle > 177:
                                #warning_message = "Bad form! Adjust your arm position!"
                                feedback_locked = False
                        else:
                            warning_message="Bad form! Adjust you left arm position"
                else:
                    warning_message = "Pose not detected. Make sure full body is visible."
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time
            except Exception as e:
                warning_message = "Pose not detected. Make sure full body is visible."
                print("Error:", e)
                current_time = time.time()
                if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                    visible_sound.play()
                    last_lower_sound_time = current_time

            # Draw pose landmarks on the image
            mp_drawing.draw_landmarks(
                image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(
                    color=(44, 42, 196) if (stage in ['too_high', 'too_low']) else (67, 196, 42),
                    thickness=2, circle_radius=2)
            )

            image = create_feedback_overlay(image, warning_message=warning_message, counter=counter, reps=sets)
            cv2.imshow('Arm Extension', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Arm Extension"]=True

if __name__ == "__main__":
    status_dict = {"Arm Extension": False}
    run_exercise(status_dict)