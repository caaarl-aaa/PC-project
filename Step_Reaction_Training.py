import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from Common import *
import random

def run_exercise(status_dict):
    
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Step Reaction Training', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Step Reaction Training', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    reps = 0
    max_reps=10
    timer_duration = 6  
    is_timer_active = False
    timer_remaining = timer_duration
    warning_message = None 
    stop_exercise=False
    counter=None
    last_lower_sound_time=None
    left_foot_color = (255, 0, 0)  # Blue for left foot
    right_foot_color = (128, 0, 128)  # Purple for right foot

    # Start the Tkinter window in a separate thread
    threading.Thread(target=create_tkinter_window, daemon=True).start()

    countdown_complete = perform_countdown(
            cap=cap,
            countdown_sound=countdown_sound,
            timer_duration=timer_duration,
            display_countdown=display_countdown,
            window_name="Step Reaction Training"
        )
    countdown_complete = True

    dynamic_spots={}

    def calibrate_spots(landmarks):
        """Calibrate spot positions based on the patient's ankle positions."""
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

        # Midpoint of ankles for central reference
        mid_x = (left_ankle.x + right_ankle.x) / 2
        floor_y = max(left_ankle.y, right_ankle.y) + 0.05  # Offset slightly below the ankles

        # Use the ankle distance to calculate horizontal scaling
        ankle_width = abs(left_ankle.x - right_ankle.x)

        # Define spots relative to the ankle midpoint
        dynamic_spots["extreme_left"] = (mid_x - 1.5 * ankle_width, floor_y)
        dynamic_spots["left_center"] = (mid_x - 0.8 * ankle_width, floor_y)
        dynamic_spots["right_center"] = (mid_x + 0.8 * ankle_width, floor_y)
        dynamic_spots["extreme_right"] = (mid_x + 1.5 * ankle_width, floor_y)
    def adjust_spot_distance(landmarks):
        """Adjust spot distance dynamically based on leg reach."""
        left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
        leg_reach = abs(left_ankle.y - left_hip.y)

        # Scale spots proportionally to leg reach
        scale_factor = leg_reach * 0.5  # Adjust scaling factor as needed
        for key, (x, y) in dynamic_spots.items():
            dynamic_spots[key] = (x, max(left_ankle.y, right_ankle.y) + scale_factor)
    #Spot to foot mapping
    foot_mapping = {
        "extreme_left": "left_foot",
        "left_center": "left_foot",
        "right_center": "right_foot",
        "extreme_right": "right_foot"
    }

    current_spot=None
    current_spot_color=(0,255,0)#green spot

    def select_next_spot():
        return random.choice(list(dynamic_spots.keys()))
    
                    
    # Setup Mediapipe Pose with specified confidence levels
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        calibrated=False

        while cap.isOpened() and reps<max_reps:
            
            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Step Reaction Training"] = True
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
            
             # If calibration hasn't been done yet, calibrate
            if not calibrated and results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                calibrate_spots(landmarks)
                adjust_spot_distance(landmarks)  # Adjust spot positions
                calibrated = True
                print("Calibration complete. Dynamic spots initialized.")
                continue

             # Draw the current spot on the screen
            if not current_spot and calibrated:
                current_spot = select_next_spot()

            
            if calibrated and current_spot:
                spot_x, spot_y=dynamic_spots[current_spot]
                height, width, _ = image.shape
                spot_coords = (int(spot_x * width), int(spot_y * height))

                required_foot = foot_mapping[current_spot]
                spot_color = left_foot_color if required_foot == "left_foot" else right_foot_color


                # Ensure spot coordinates are within the screen boundaries
                if 0 <= spot_coords[0] < width and 0 <= spot_coords[1] < height:
                    cv2.circle(image, spot_coords, 30, spot_color, -1)
                    warning_message="Left leg" if spot_color==left_foot_color else "Right Leg" 
                else:
                    print(f"Spot {current_spot} is out of bounds: {spot_coords}")    
                
                try:
                    if results.pose_landmarks:
                        landmarks = results.pose_landmarks.landmark

                        # Check if required landmarks are detected
                        required_landmarks = {
                            'Right Foot': mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value,
                            'Left Foot': mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value
                        }
                        missing_landmarks = []
                        for name, idx in required_landmarks.items():
                            visibility = landmarks[idx].visibility
                            if visibility < 0.5 or np.isnan(landmarks[idx].x) or np.isnan(landmarks[idx].y):
                                missing_landmarks.append(name)

                        if missing_landmarks:
                            warning_message = f"Adjust Position: {', '.join(missing_landmarks)} not detected!"

                        else:
                            
                            # Get pixel coordinates for left and right foot indices
                            left_foot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
                            right_foot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]

                            left_foot_coords = (int(left_foot.x * width), int(left_foot.y * height))
                            right_foot_coords = (int(right_foot.x * width), int(right_foot.y * height))

                            # Draw left foot index (blue, larger)
                            cv2.circle(image, left_foot_coords, 15, left_foot_color, -1)

                            # Draw right foot index (purple, larger)
                            cv2.circle(image, right_foot_coords, 15, right_foot_color, -1)


                            # Get coordinates for hip, knee, and ankle
                            left_foot_index = [landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value].y]
                            right_foot_index = [landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                                    landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value].y]


                            # Exercise logic with state machine
                            required_foot=foot_mapping[current_spot]
                            foot_coords=left_foot_index if required_foot=="left_foot" else right_foot_index
                            foot_x, foot_y=foot_coords
                            distance = ((foot_x - spot_x)**2 + (foot_y - spot_y)**2)**0.5

                            # If distance is within a threshold, count as a successful tap
                            if distance < 0.05:  # Adjust threshold as needed
                                reps += 1
                                current_spot = None  # Select the next spot
                                beep_sound.play()

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

            image = create_feedback_overlay(image, warning_message=warning_message, counter=reps, reps=reps)
            # Draw pose landmarks on the image
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                      mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

            cv2.imshow('Step Reaction Training', image)

            # Break the loop if 'q' key is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()
    status_dict["Step Reaction Training"]= True

if __name__ == "__main__":
    status_dict={"Step Reaction Training": False}
    run_exercise(status_dict)
