"""
So the left ankle is right ankle ..we need to flip the logic cuz im tired..Ill fix later
"""

import cv2
import mediapipe as mp
import threading
from Common import *

def run_exercise(status_dict):
    # Mediapipe setup
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    # Open video capture
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    # Fullscreen setup
    cv2.namedWindow('Side Box Step Up', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Side Box Step Up', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    counter = 0  # Counter for repetitions
    sets = 0  # Sets counter
    stage = None
    feedback = "Get Ready"
    # Start the Tkinter window in a separate thread
    threading.Thread(target=create_tkinter_window, daemon=True).start()

    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Side Box Step Up"
    )

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Side Box Step Up"] = True
                break

            ret, frame = cap.read()
            if not ret:
                break

            ret, frame = cap.read()
            if not ret:
                print("Unable to read frame from the camera.")
                break

            # Pre-process the frame
            frame = cv2.flip(frame, 1)  # Mirror the frame for user convenience
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            frame_height, frame_width, _ = image.shape
           
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                 # Get coordinates for hip, knee, and ankle
                    hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
                    knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                                landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
                    ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                                 landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

                        # Calculate the angle between hip, knee, and ankle
                    angle = calculate_angle(hip, knee, ankle)


                    # Get the user's hip position
                    right_hip_x = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x
                    right_hip_y = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y
                    # Define box dimensions and offsets
                    box_width = 0.15  # Box width as a fraction of frame width
                    box_height = 0.1  # Box height as a fraction of frame height
                    x_offset = -0.13    # Horizontal offset to shift the box to the right
                    y_offset = 0.4  # Vertical offset to raise the box

                    # Convert normalized hip position to pixel coordinates
                    hip_x = int(right_hip_x * frame_width)
                    hip_y = int(right_hip_y * frame_height)

                    # Adjust the box position relative to the hip
                    box_x_min = max(0, hip_x - int(box_width * frame_width / 2) + int(x_offset * frame_width))
                    box_x_max = min(frame_width, hip_x + int(box_width * frame_width / 2) + int(x_offset * frame_width))
                    box_y_min = max(0, hip_y - int(box_height * frame_height / 2) + int(y_offset * frame_height))
                    box_y_max = min(frame_height, hip_y + int(box_height * frame_height / 2) + int(y_offset * frame_height))

                    # Update box coordinates for drawing
                    box_coords = (box_x_min, box_y_min, box_x_max, box_y_max)

                    # Draw the box
                    cv2.rectangle(image, box_coords[:2], box_coords[2:], (0, 255, 0), 2)
                    
                    # Get left ankle position in pixel coordinates
                    left_heel_x = int(landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].x * frame_width)
                    left_heel_y = int(landmarks[mp_pose.PoseLandmark.RIGHT_HEEL.value].y * frame_height)
                    # Draw LEFT ankle
                    cv2.circle(image, (left_heel_x, left_heel_y), 10, (0, 0, 255), -1)
                    # Check if the left foot is on the box
                    if box_x_min < left_heel_x < box_x_max and box_y_min < left_heel_y < box_y_max:
                        # Check if the user has stepped onto the box
                        if stage is None or stage == "off_box":
                            if angle<160:
                                feedback = "Step-Up Completed! Step down"
                                stage = "on_box"
                                counter+=1
                                beep_sound.play()
                                print("on box:")
                                print(angle)
                    elif stage == "on_box" and angle>173:
                                feedback = "Step Up"
                                stage = "off_box"
                                print('off box:')
                                print(angle)



                else:
                    feedback = "Pose Not Detected. Ensure Full Body is Visible."

            except Exception as e:
                print(f"Error processing frame: {e}")
                feedback = "Error in Pose Detection"

            # Overlay feedback and counters on the image
            image = create_feedback_overlay(image, warning_message=feedback, counter=counter, reps=sets)

            # Draw pose landmarks
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=( 67,196,42) if (feedback=="Error in Pose Detection" or feedback=="Pose Not Detected. Ensure Full Fody is Visible.") else (44,42,196), thickness=2, circle_radius=2)
            )

            # Display the frame
            cv2.imshow('Side Box Step Up', image)

            # Break loop on 'q' key press
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Side Box Step Up"] = True


if __name__ == "__main__":
    status_dict = {"Side Box Step Up": False}
    run_exercise(status_dict)
