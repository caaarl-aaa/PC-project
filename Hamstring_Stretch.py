import cv2
import mediapipe as mp
import numpy as np
import time
import os
from pygame import mixer
import tkinter as tk
import threading
from Common import *


def run_exercise(status_dict):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Hamstring Stretch', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Hamstring Stretch', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    reps = 0
    timer_duration = 6  
    is_timer_active = False
    timer_remaining = timer_duration
    warning_message = None 
    stop_exercise = False
    HOLD_TIME = 20
    hold_start_time = None
    current_leg = 0
    posture_correct = False

    threading.Thread(target=create_tkinter_window, daemon=True).start()
    """countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Hamstring Stretch"
    )"""

    last_lower_sound_time = None 
    countdown_complete = False


    with mp_pose.Pose(min_detection_confidence=0.6, min_tracking_confidence=0.6) as pose:
        while cap.isOpened():
            if stop_exercise:
                status_dict["Hamstring Stretch"] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Default no-warning each frame
            warning_message = None
            knee_angle = None
            hip_angle = None

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    # Required landmarks based on current leg
                    #if current_leg == 0:  # Left leg exercise
                    required_landmarks = {
                            'Left Ankle': mp_pose.PoseLandmark.LEFT_ANKLE.value,
                            'Left Knee': mp_pose.PoseLandmark.LEFT_KNEE.value,
                            'Left Hip': mp_pose.PoseLandmark.LEFT_HIP.value,
                            'Left Shoulder': mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                            'Left Foot': mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
                        }
                    """else:  # Right leg exercise
                        required_landmarks = {
                            'Right Ankle': mp_pose.PoseLandmark.RIGHT_ANKLE.value,
                            'Right Knee': mp_pose.PoseLandmark.RIGHT_KNEE.value,
                            'Right Hip': mp_pose.PoseLandmark.RIGHT_HIP.value,
                            'Right Shoulder': mp_pose.PoseLandmark.RIGHT_SHOULDER.value,
                            'Right Foot': mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value
                        }"""

                    missing_landmarks = []
                    for name, idx in required_landmarks.items():
                        visibility = landmarks[idx].visibility
                        if visibility < 0.5:
                            missing_landmarks.append(name)

                    if missing_landmarks:
                        warning_message = f"Adjust Position: {', '.join(missing_landmarks)} not detected!"
                    else:
                        # Extract coordinates
                        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
                        left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                         landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

                        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
                        right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                          landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

                        # Compute angles for the current leg
                        if current_leg == 0:  # Left leg
                            knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
                            hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)
                        else:  # Right leg
                            knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
                            hip_angle = calculate_angle(right_shoulder, right_hip, right_knee)

                        STABILITY_BUFFER = 4  # Seconds to wait before resetting
                        last_valid_time = None

                        # Check posture
                        if (knee_angle>=150)  and (hip_angle<=110)  :
                            posture_correct = True
                            if hold_start_time is None:
                                hold_start_time = time.time()
                            posture_correct=True
                            last_valid_time=time.time()

                            elapsed = time.time() - hold_start_time
                            hold_remaining = HOLD_TIME - elapsed

                            if hold_remaining <=0:
                                # Completed hold
                                reps += 1
                                success_sound.play()
                                warning_message = "Great job! Switch legs."
                                #current_leg = 1 - current_leg
                                hold_start_time = None
                                
                        else:
                            current_time = time.time()
                            if last_valid_time and (current_time - last_valid_time) < STABILITY_BUFFER:
                                # Maintain the hold timer if within the stability buffer
                                warning_message = "Stay steady! Correct your posture."
                            else:
                                # Reset the hold timer if the buffer is exceeded
                                hold_start_time = None
                                posture_correct = False
                                hold_remaining = HOLD_TIME
                                warning_message = "Adjust your position (straighten leg & lean forward)."
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

            mp_drawing.draw_landmarks(
                image, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )

            try:
                # Ensure hold_remaining is initialized to avoid UnboundLocalError
                if hold_start_time is None or not posture_correct:
                    hold_remaining = HOLD_TIME  # Default hold time when posture is incorrect or not started
                else:
                    elapsed = time.time() - hold_start_time
                    hold_remaining = max(0, HOLD_TIME - elapsed)

                # Display warning_message or feedback overlay
                image = create_feedback_overlay(
                    image, 
                    warning_message=warning_message, 
                    counter=max(0,int(hold_remaining)), 
                    reps=reps
                )
            except Exception as e:
                print("Error in creating feedback overlay:", e)
            cv2.imshow('Hamstring Stretch', image)


            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Hamstring Stretch"] = True

if __name__ == "__main__":
    status_dict = {"Hamstring Stretch": False}
    run_exercise("Hamstring Stretch")
