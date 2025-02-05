import cv2
import mediapipe as mp
import numpy as np
import time
import threading
import pygame
from collections import deque  # To track recent angles for smoothing
import tkinter as tk
from Common import *


# Global variable to control the exercise loop
stop_exercise = False

def smooth_data(data, max_length=5):
    """Smooth recent data using a moving average."""
    if len(data) > max_length:
        data.popleft()  # Remove the oldest value
    return np.mean(data)


def run_exercise(status_dict):
    global stop_exercise

    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Single-Leg Squat Exercise', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Single-Leg Squat Exercise', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    counter = 0
    reps = 0
    Max_counter = 3
    Max_reps = 2
    stage = 'start'
    warning_message = None
    last_lower_sound_time = None
    raised_leg_angles = deque()
    stability_score = None

    # Start the Tkinter window in a separate thread
    threading.Thread(target=create_tkinter_window, daemon=True).start()

    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Single-Leg Squat Exercise"
    )

    # Set flag after countdown
    countdown_complete = True

    # Load or create placeholder images for arrows
    down_arrow = np.zeros((100, 100, 4), dtype=np.uint8)  # Placeholder transparent image
    resized_up_arrow = np.zeros((100, 100, 4), dtype=np.uint8)  # Placeholder transparent image

    # Setup Mediapipe Pose with specified confidence levels
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():

            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Single Leg Squat"] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB and make it non-writable to improve performance
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
                    filtered_landmarks = {
                        idx: lm for idx, lm in enumerate(landmarks)
                        if lm.visibility > visibility_threshold
                    }

                    # Ensure key landmarks are detected
                    if len(filtered_landmarks) < 6:
                        warning_message = "Ensure full body visibility!"
                        current_time = time.time()
                        if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                            visible_sound.play()
                            last_lower_sound_time = current_time
                    else:
                        # Coordinates for the left (raised) leg
                        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                        # Coordinates for the right (squatting) leg
                        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                                     landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                       landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                        # Calculate angles
                        raised_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
                        squat_angle = calculate_angle(right_hip, right_knee, right_ankle)
                        
                        # Smooth raised leg angle for stability
                        raised_leg_angles.append(raised_leg_angle)
                        smoothed_raised_angle = smooth_data(raised_leg_angles)

                        # Stability Score: Difference between smoothed and actual angle
                        stability_score = abs(smoothed_raised_angle - raised_leg_angle)

                        # Exercise logic with state machine
                        # Ensure left leg is raised
                        if smoothed_raised_angle < 80:
                            warning_message = "Lower your left leg!"
                        elif smoothed_raised_angle > 100:
                            warning_message = "Raise your left leg!"
                        elif stability_score > 10:
                            warning_message = "Reduce movement in the raised leg!"
                        else:
                            # Check squat depth and progression
                            if stage == 'start' and squat_angle > 155:
                                stage = 'down'
                                warning_message = "Squat down!"
                                overlay_image_alpha(image, down_arrow, (50, 50), down_arrow[:, :, 3])

                            elif stage == 'down' and 140 <= squat_angle <= 155:
                                stage = 'up'
                                counter += 1
                                beep_sound.play()
                                warning_message = "Good depth! Stand back up."
                                overlay_image_alpha(image, resized_up_arrow, (50, 50), resized_up_arrow[:, :, 3])
                                if counter >= Max_counter:
                                    reps += 1
                                    counter = 0
                                    success_sound.play()
                                    if reps >= Max_reps:
                                        break
                            elif stage == 'up' and squat_angle > 165:
                                stage = 'start'

                            else:
                                warning_message = "Maintain proper form!"
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
            image = create_feedback_overlay(image, warning_message=warning_message, counter=counter, reps=reps)
            cv2.imshow('Single-Leg Squat Exercise', image)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    status_dict["Single Leg Squat"] = True

if __name__ == "__main__":
    status_dict = {"Single Leg Squat": False}
    run_exercise(status_dict)
