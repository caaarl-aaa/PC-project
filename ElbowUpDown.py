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

   
    # Set up camera feed
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cv2.namedWindow('Elbow Up Down Exercise', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Elbow Up Down Exercise', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    # Curl counter variables
    counter = 0
    tot_count=5
    reps=0
    warning_message=None
    last_lower_sound_time=None
    stage=None
    
    threading.Thread(target=create_tkinter_window, daemon=True).start()
    
    # Perform the countdown
    countdown_complete = perform_countdown(
        cap=cap,
        countdown_sound=countdown_sound,
        timer_duration=timer_duration,
        display_countdown=display_countdown,
        window_name="Elbow Up Down Exercise"
    )

    # Set flag after countdown
    countdown_complete = True   

    # Setup Mediapipe Pose with specified confidence levels
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            if stop_exercise:  # Check if "Done" button was pressed
                status_dict["Elbow Up Down"] = True
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
            warning_message=None

            # Extract pose landmarks
            try:
                if results.pose_landmarks:
                    landmarks = results.pose_landmarks.landmark

                    #Check if required ones are detected
                    required_landmarks={
                        'Left Shoulder': mp_pose.PoseLandmark.LEFT_SHOULDER.value,
                        'Left Elbow': mp_pose.PoseLandmark.LEFT_ELBOW.value,
                        'Left Wrist': mp_pose.PoseLandmark.LEFT_WRIST.value

                    }
                    missing_landmarks=[]
                    for name,idx in required_landmarks.items():
                        visibility=landmarks[idx].visibility
                        if visibility<0.5 or np.isnan(landmarks[idx].x) or np.isnan(landmarks[idx].y):
                            missing_landmarks.append(name)
                    
                    if missing_landmarks:
                        warning_message=f"Adjust Position: {', '.join(missing_landmarks)} not detected!"
                        current_time = time.time()
                        if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                            visible_sound.play()
                            last_lower_sound_time = current_time

                    else:

                        # Get coordinates for shoulder, elbow, and wrist
                        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                        # Calculate the angle between shoulder, elbow, and wrist
                        angle = calculate_angle(shoulder, elbow, wrist)

                        # Visualize the angle at the elbow
                        cv2.putText(image, str(int(angle)),
                                    tuple(np.multiply(elbow, [640, 480]).astype(int)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                        # Curl counter logic
                        if angle > 160:
                            stage = "down"
                        if angle < 30 and stage == 'down':
                            stage = "up"
                            counter += 1
                            beep_sound.play()
                            warning_message="Good Job! Keep Going"
                            if counter==tot_count:
                                reps+=1
                                warning_message="Good Job! Keep Going"
                                good_job_message_time=time.time()
                                
                else:
                    warning_message="Pose not detected. Make sure full body is visible."
                    current_time = time.time()
                    if last_lower_sound_time is None or (current_time - last_lower_sound_time) >= 5:
                        visible_sound.play()
                        last_lower_sound_time = current_time

            except Exception as e:
                warning_message="Pose not detected. Make sure full body is visible."
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
            cv2.imshow('Elbow Up Down Exercise', image)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    status_dict["Elbow Up Down"]=True

if __name__ == "__main__":
    status_dict = {"Elbow Up Down": False}
    run_exercise(status_dict)