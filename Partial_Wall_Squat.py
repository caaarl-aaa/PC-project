import cv2
import mediapipe as mp
import time
import threading
import numpy as np
from pygame import mixer
from Common import *

def run_exercise(status_dict):
    # Mediapipe setup
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Open video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Partial Wall Squat', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Partial Wall Squat', cv2.WINDOW_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    reps = 0
    stage = 'up'
    timer_duration = 6
    warning_message = None
    last_lower_sound_time = None
    timer_remaining = timer_duration
    is_timer_active = False
    last_beep_time = None
    stop_exercise = False
    hold_timer = 5  # New timer for holding the "good position"
    hold_start_time = None
    posture_correct = False

    # Start the "Done" button thread
    threading.Thread(target=stop_exercise_callback, daemon=True).start()

    # Perform countdown before starting
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Partial Wall Squat"
    )

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():

            if stop_exercise:  # Stop the exercise if "Done" button is clicked
                status_dict["Exercise stopped."] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            # Pre-process the frame
            frame = cv2.flip(frame, 1)  # Mirror the frame for user convenience
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            warning_message = None

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Get coordinates for hip, knee, and ankle
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    # Calculate angle
                    angle = calculate_angle(hip, knee, ankle)

                    # Display angle on the frame
                    cv2.putText(image, f"Angle: {int(angle)}",
                                tuple(np.multiply(knee, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Feedback and repetition logic
                    if 115 <= angle <= 135:  # Wall squat position (approximately 45 degrees)
                        posture_correct = True
                        if hold_start_time is None:
                            hold_start_time = time.time()
                        elapsed = time.time() - hold_start_time
                        hold_remaining = hold_timer - elapsed

                        if hold_remaining > 0:
                            warning_message = f"Hold: {int(hold_remaining)} seconds remaining"
                        else:
                            # Completed hold
                            if posture_correct:
                                reps += 1
                                success_sound.play()
                                warning_message = "Great job!"
                                hold_start_time = None
                                posture_correct = False

                    else:
                        posture_correct = False
                        hold_start_time = None

                else:
                    warning_message = "Pose not detected. Make sure full body is visible."
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time

            except Exception as e:
                print(f"Error processing frame: {e}")

            # Draw pose landmarks on the image
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(67, 196, 42), thickness=2, circle_radius=2))

            # Ensure hold_remaining is initialized to avoid UnboundLocalError
            try:
                if hold_start_time is None or not posture_correct:
                    hold_remaining = hold_timer  # Default hold time when posture is incorrect or not started
                else:
                    elapsed = time.time() - hold_start_time
                    hold_remaining = max(0, hold_timer - elapsed)

                image = create_feedback_overlay(image, warning_message=warning_message, counter=max(0, int(hold_remaining)), reps=reps)
                cv2.imshow('Partial Wall Squat', image)

            except Exception as e:
                print("Error in creating feedback overlay:", e)

            # Break loop on 'q' key press
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Partial Wall Squat"] = True

if __name__ == "__main__":
    status_dict = {"Partial Wall Squat": False}
    run_exercise(status_dict)