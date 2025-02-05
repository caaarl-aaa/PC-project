import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from Common import *
from exercise_state import stop_exercise_event


def run_exercise(exercise_status):
            mp_drawing = mp.solutions.drawing_utils
            mp_pose = mp.solutions.pose

            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            cv2.namedWindow('Standing Leg Front Lift', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Standing Leg Front Lift', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            reps = 0
            stage = 'down'
            warning_message = None
            last_lower_sound_time=None
            timer_remaining = None
            is_timer_active = False
            last_beep_time=None
            # Start the Tkinter window in a separate thread
            c=threading.Thread(target=create_tkinter_window, args=("Standing Leg Front Lift",), daemon=True).start()
        

            # Perform the countdown
            countdown_complete = perform_countdown(
                cap=cap,
                countdown_sound=countdown_sound,
                timer_duration=timer_duration,
                display_countdown=display_countdown,
                window_name="Standing Leg Front Lift"
            )

            # Set flag after countdown
            countdown_complete = True

            # Setup Mediapipe Pose with specified confidence levels
            with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
                while cap.isOpened():
                    if stop_exercise_event.is_set():
                        print("Stopping exercise...")
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

                            # Check if required landmarks are detected
                            required_landmarks = {
                                'Left Hip': mp_pose.PoseLandmark.LEFT_HIP.value,
                                'Left Knee': mp_pose.PoseLandmark.LEFT_KNEE.value,
                                'Left Ankle': mp_pose.PoseLandmark.LEFT_ANKLE.value
                            }
                            missing_landmarks = []
                            for name, idx in required_landmarks.items():
                                visibility = landmarks[idx].visibility
                                if visibility < 0.5 or np.isnan(landmarks[idx].x) or np.isnan(landmarks[idx].y):
                                    missing_landmarks.append(name)

                            if missing_landmarks:
                                warning_message = f"Adjust Position: {', '.join(missing_landmarks)} not detected!"

                            else:
                                # Get coordinates for hip, knee, and ankle
                                hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                                knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                                ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                                # Calculate the angle between hip, knee, and ankle
                                angle = calculate_angle(hip, knee, ankle)

                                # Visualize the angle
                                cv2.putText(image, str(int(angle)),
                                            tuple(np.multiply(knee, [640, 480]).astype(int)),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                                # Exercise logic with state machine

                                if angle > 97:
                                    warning_message = "Leg is too down. Raise your leg."
                                    current_time = time.time()
                                    overlay_image_alpha(image, resized_up_arrow, (50, 50), resized_up_arrow[:, :, 3])
                                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                                        upper_sound.play()
                                        last_lower_sound_time = current_time
                                    if stage in ['hold', 'up']:
                                        # Leg is too low; freeze timer
                                        is_timer_active = False
                                        stage = 'too_low'

                                elif angle < 85:
                                    warning_message = "Leg is too up. Lower your leg."
                                    current_time = time.time()
                                    overlay_image_alpha(image, down_arrow, (50, 50), down_arrow[:, :, 3])
                                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                                        golower_sound.play()
                                        last_lower_sound_time = current_time
                                    if stage in ['hold', 'up']:
                                        # Leg is too high; freeze timer
                                        is_timer_active = False
                                        stage = 'too_high'

                                else:
                                    # Angle is between 85 and 97 degrees
                                    if stage in ['down', 'too_high', 'too_low']:
                                        # Start or resume timer
                                        if not is_timer_active:
                                            timer_start = time.time() - (Hold_duration - timer_remaining if timer_remaining else 0)
                                        is_timer_active = True
                                        stage = 'up'
                                        last_lower_sound_time = None  # Reset lower sound timer
                                        if last_beep_time is None or timer_remaining < last_beep_time:
                                            great_sound.play()
                                            last_beep_time = timer_remaining

                                    if stage == 'up' and is_timer_active:
                                        # Continue timing
                                        elapsed_time = time.time() - timer_start
                                        timer_remaining = max(0, int(Hold_duration - elapsed_time))

                                        if last_beep_time is None or timer_remaining < last_beep_time:
                                            beep_sound.play()
                                            last_beep_time = timer_remaining

                                        if timer_remaining <= 0:
                                            # Rep completed
                                            success_sound.play()
                                            warning_message = "Great! Hold Completed!"
                                            reps += 1
                                            is_timer_active = False
                                            timer_remaining = Hold_duration
                                            stage = 'hold'
                                            last_beep_time = None
                                            last_lower_sound_time = None
                                                    

                                    elif stage == 'hold':
                                        warning_message = "Lower your leg"


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
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                            mp_drawing.DrawingSpec(color=(44,42,196) if (stage in ['too_high', 'too_low']) else (67,196,42), thickness=2, circle_radius=2))
                    current_timer = int(timer_remaining) if timer_remaining is not None else 0
                    
                    image = create_feedback_overlay(image, warning_message=warning_message, counter=current_timer, reps=reps)
                    cv2.imshow('Standing Left Leg Front Lift', image)

                    # Break the loop if 'q' key is pressed
                    if cv2.waitKey(10) & 0xFF == ord('q'):
                        break

            # Release resources
            cap.release()
            cv2.destroyAllWindows()
            pass
            exercise_status["Standing Leg Front Lift"] = True


if __name__ == "__main__":
    exercise_status = {"Standing Leg Front Lift": False}
    run_exercise(exercise_status)