import cv2
import mediapipe as mp
import numpy as np
import time
from Common import *
import threading

# Global variable to control the exercise loop
stop_exercise = False

def run_exercise(exercise_status):
    global stop_exercise
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Calf-Stretch Exercise', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Calf-Stretch Exercise', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    counter = 0
    stage = None
    warning_message=None
    sets = 0
    last_lower_sound_time=None
     # Start the Tkinter window in a separate thread
    threading.Thread(target=create_tkinter_window, daemon=True).start()

    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Calf-Stretch Exercise"
    )
    # Set flag after countdown
    countdown_complete=True

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Calf Stretch"] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            warning_message=None
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark
                    # Filter out landmarks with low visibility
                    visibility_threshold = 0.6
                    required_landmarks = {
                        mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value,
                        mp_pose.PoseLandmark.LEFT_KNEE.value,
                        mp_pose.PoseLandmark.LEFT_HIP.value,
                        mp_pose.PoseLandmark.LEFT_ANKLE.value
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
                        # Get relevant landmarks
                        left_foot_index = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
                        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                        left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                        # Calculate the angle at the left knee using ankle, knee, and hip
                        angle = calculate_angle(left_ankle, left_knee, left_hip)

                        # Set a threshold angle (for example, if the knee is bent enough to count)
                        if angle > 160:  # Change this threshold as needed
                            stage = "start"
                        else:
                            if stage != "down":
                                stage = "down"
                                counter += 1
                                warning_message = "Keep going!"
                                if counter == 6:
                                    sets += 1
                                    counter = 0

                        # Ensure that the landmarks exist before calculating the line
                        if landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value] and \
                                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value] and \
                                landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]:
                            # Vertical line from the left foot index to the middle of the left thigh
                            # Left foot index (point 31) and middle of left thigh (average of left knee and left hip)
                            foot_x, foot_y = left_foot_index
                            knee_x, knee_y = left_knee
                            hip_x, hip_y = left_hip

                            # Middle of left thigh is the midpoint between the knee and hip
                            middle_thigh_x = (knee_x + hip_x) / 2
                            middle_thigh_y = (knee_y + hip_y) / 2

                            # Convert the normalized coordinates to pixel values
                            foot_pixel = np.multiply(left_foot_index, [640, 480])
                            middle_thigh_pixel = np.multiply([foot_x, middle_thigh_y], [640, 480])
                            knee_pixel = np.multiply(left_knee, [640, 480])

                            foot_pixel = tuple(foot_pixel.astype(int))
                            middle_thigh_pixel = tuple(middle_thigh_pixel.astype(int))
                            knee_pixel = tuple(knee_pixel.astype(int))
                            cv2.line(image, foot_pixel, middle_thigh_pixel, (0, 255, 255), 2)

                            # Check if the left knee has crossed the vertical line
                            if knee_pixel[0] > foot_pixel[0]:
                                warning_message = "GOOD"
                            else:
                                warning_message = "Down"
                else:
                    warning_message = "Pose not detected. Make sure full body is visible."
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time
            except Exception as e:
                warning_message = "Get Ready"
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
            cv2.imshow('Calf-Stretch Exercise', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Calf Stretch"]=True

if __name__ == "__main__":
    status_dict = {"Calf Stretch": False}
    run_exercise(status_dict)