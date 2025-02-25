import cv2
import mediapipe as mp
import numpy as np
import time
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
    warning_message = None
    stop_exercise = False
    HOLD_TIME = 20
    hold_elapsed_time = 0  # Track total hold time
    hold_start_time = None
    last_beep_time=None
    last_displayed_second = HOLD_TIME
    timer_remaining = HOLD_TIME

    threading.Thread(target=create_tkinter_window, daemon=True).start()
    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Hamstring Stretch"
    )
    last_lower_sound_time = None

    # Initialize MediaPipe Pose
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

            # Reset warning message for each frame
            warning_message = None
            knee_angle = None
            hip_angle = None

            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Define required landmarks for the current leg
                    required_landmarks = {
                        'Left Ankle': mp_pose.PoseLandmark.LEFT_ANKLE.value,
                        'Left Knee': mp_pose.PoseLandmark.LEFT_KNEE.value,
                        'Left Hip': mp_pose.PoseLandmark.LEFT_HIP.value,
                        'Left Shoulder': mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                        'Left Foot': mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
                    }

                    # Check for visibility of landmarks
                    missing_landmarks = [
                        name for name, idx in required_landmarks.items()
                        if landmarks[idx].visibility < 0.5
                    ]

                    if missing_landmarks:
                        warning_message = f"Adjust Position: {', '.join(missing_landmarks)} not detected!"
                        current_time = time.time()
                        if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                            visible_sound.play()
                            last_lower_sound_time = current_time
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

                        # Calculate angles
                        knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
                        hip_angle = calculate_angle(left_shoulder, left_hip, left_knee)
                        cv2.putText(image, f"Knee: {int(knee_angle)}s", (10, 110), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, f"Hip: {int(hip_angle)}s", (10, 125), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
                        # Check posture
                        if 140 <= knee_angle and hip_angle <= 120:
                            posture_correct = True
                            if hold_start_time is None:
                                hold_start_time = time.time()

                            # Update elapsed hold time
                            hold_elapsed_time += time.time() - hold_start_time
                            hold_start_time = time.time()  # Reset for the next iteration
                            

                            if hold_elapsed_time >= HOLD_TIME:
                                reps += 1
                                success_sound.play()
                                warning_message = "Great job! Switch legs."
                                hold_elapsed_time = 0  # Reset for the next rep
                                posture_correct = False
                                last_displayed_second=HOLD_TIME
                        else:
                            if hip_angle>120:
                                current_time = time.time()
                                if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                                    bend_hip_sound.play()
                                    last_lower_sound_time = current_time
                            elif knee_angle<140:
                                current_time=time.time()
                                if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                                    ext_leg_sound.play()
                                    last_lower_sound_time = current_time
                            
                            posture_correct = False
                            hold_start_time = None  # Pause hold time
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

            # Draw landmarks and connections
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=( 67,196,42) if (warning_message=="Adjust your position (straighten leg & lean forward)" or warning_message=="Pose not detected. Make sure full body is visible.") else (44,42,196), thickness=2, circle_radius=2)
            )

            # Feedback overlay
            hold_remaining = max(0, int(HOLD_TIME - hold_elapsed_time))
            if hold_remaining < last_displayed_second:
                beep_sound.play()
                last_displayed_second = hold_remaining 

            image = create_feedback_overlay(
                image,
                warning_message=warning_message,
                counter=max(0, int(hold_remaining)),
                reps=reps
            )

            cv2.imshow('Hamstring Stretch', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Hamstring Stretch"] = True

if __name__ == "__main__":
    status_dict = {"Hamstring Stretch": False}
    run_exercise(status_dict)
