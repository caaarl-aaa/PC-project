import cv2
import mediapipe as mp
import numpy as np
from Common import calculate_angle  # Assuming you have a function to calculate angles

def run_exercise(exercise_status):
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)  # Open webcam

    reps = 0
    stage = 'down'
    warning_message = None

    # Setup Mediapipe Pose with specified confidence levels
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB for Mediapipe
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert back to BGR for display

            warning_message = None  # Reset warning message for each frame

            # Extract pose landmarks
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    # Get key points
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

                    # Calculate the angle
                    angle = calculate_angle(hip, knee, ankle)

                    # Display the angle
                    cv2.putText(image, str(int(angle)),
                                tuple(np.multiply(knee, [640, 480]).astype(int)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                    # Exercise logic
                    if angle > 97:
                        warning_message = "Leg is too down. Raise your leg."
                        stage = 'too_low'

                    elif angle < 85:
                        warning_message = "Leg is too up. Lower your leg."
                        stage = 'too_high'

                    else:
                        if stage in ['down', 'too_high', 'too_low']:
                            stage = 'up'

                else:
                    warning_message = "Pose not detected. Make sure full body is visible."

            except Exception as e:
                warning_message = "Pose not detected. Make sure full body is visible."
                print("Error:", e)

            # Draw pose landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(67, 196, 42), thickness=2, circle_radius=2))

            # Yield the processed frame instead of showing it with OpenCV
            yield image

    cap.release()