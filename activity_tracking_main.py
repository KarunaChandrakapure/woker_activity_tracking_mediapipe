import cv2
import mediapipe as mp
import numpy as np
import json
import os
import time
from datetime import datetime

# Function to read the video path from config file
def load_config(config_path="config.json"):
    with open(config_path, "r") as file:
        config = json.load(file)
    return config["video_path"]

# Function to calculate Euclidean distance (movement)
def calculate_movement(prev, curr):
    if prev is None or curr is None:
        return 0
    return np.linalg.norm(np.array(prev) - np.array(curr))

# Function to crop region of interest (ROI)
def crop_region(frame, x, y, w, h):
    return frame[y:y+h, x:x+w]

# Function to log coordinates to CSV
def log_coordinates(log_file, coordinates):
    with open(log_file, 'a') as f:
        f.write(f"{coordinates['timestamp']},{coordinates['left_wrist']},{coordinates['right_wrist']},"
                f"{coordinates['left_knee']},{coordinates['right_knee']},{coordinates['left_ankle']},"
                f"{coordinates['right_ankle']}\n")

# Function to display status on image 
def display_status(image, status, position=(30, 40)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Status: {status}"
    cv2.putText(image, text, position, font, 1, (255, 255, 255), 2, cv2.LINE_AA)

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Initialize log file
log_file = "activity_log.csv"
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write("timestamp,left_wrist_x,left_wrist_y,right_wrist_x,right_wrist_y,"
                "left_knee_x,left_knee_y,right_knee_x,right_knee_y,"
                "left_ankle_x,left_ankle_y,right_ankle_x,right_ankle_y\n")

# Load video path from config file
video_path = load_config()
cap = cv2.VideoCapture(video_path)

# Initialize previous positions of landmarks for movement comparison
prev_left_wrist = None
prev_right_wrist = None
prev_left_knee = None
prev_right_knee = None
prev_left_ankle = None
prev_right_ankle = None

# Idle timeout duration (in seconds)
idle_timeout = 600
last_move_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Crop region (for example, center of the frame)
    height, width, _ = frame.shape
    crop_x, crop_y, crop_w, crop_h = int(width * 0.2), int(height * 0.2), int(width * 0.6), int(height * 0.6)
    cropped_frame = crop_region(frame, crop_x, crop_y, crop_w, crop_h)

    # Convert the BGR image to RGB for MediaPipe
    image = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2RGB)

    # Process the image and get the pose landmarks
    results = pose.process(image)

    # Convert the image back to BGR for display
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    status = "Idle"  # Default status if no significant movement is detected

    # Draw the pose landmarks and check for movement
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extract wrist, knee, and ankle landmarks
        landmarks = results.pose_landmarks.landmark

        # Get positions of the wrists, knees, and ankles
        left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_WRIST].y]
        right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_WRIST].y]

        left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE].x,
                     landmarks[mp_pose.PoseLandmark.LEFT_KNEE].y]
        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].x,
                      landmarks[mp_pose.PoseLandmark.RIGHT_KNEE].y]

        left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].x,
                      landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].x,
                       landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y]

        # Calculate movement for wrists, knees, and ankles
        left_wrist_move = calculate_movement(prev_left_wrist, left_wrist)
        right_wrist_move = calculate_movement(prev_right_wrist, right_wrist)

        left_knee_move = calculate_movement(prev_left_knee, left_knee)
        right_knee_move = calculate_movement(prev_right_knee, right_knee)

        left_ankle_move = calculate_movement(prev_left_ankle, left_ankle)
        right_ankle_move = calculate_movement(prev_right_ankle, right_ankle)

        # Check for any significant movement (threshold 0.01 for wrist/ankle/knee)
        if (left_wrist_move > 0.01 or right_wrist_move > 0.01 or
            left_knee_move > 0.01 or right_knee_move > 0.01 or
            left_ankle_move > 0.01 or right_ankle_move > 0.01):
            status = "Working"
            last_move_time = time.time()  # Reset idle timer when movement is detected

        # Update the previous positions
        prev_left_wrist = left_wrist
        prev_right_wrist = right_wrist
        prev_left_knee = left_knee
        prev_right_knee = right_knee
        prev_left_ankle = left_ankle
        prev_right_ankle = right_ankle

        # Log coordinates to file
        coordinates = {
            "timestamp": datetime.now().strftime('%H:%M:%S'),
            "left_wrist": left_wrist,
            "right_wrist": right_wrist,
            "left_knee": left_knee,
            "right_knee": right_knee,
            "left_ankle": left_ankle,
            "right_ankle": right_ankle
        }
        log_coordinates(log_file, coordinates)

    # Check if idle time exceeded
    if time.time() - last_move_time > idle_timeout:
        status = "Idle"

    # Display status with black background and white text
    display_status(image, status)

    # Show the resulting image
    cv2.imshow('MediaPipe Pose Detection', image)

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
