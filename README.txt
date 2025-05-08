Main code : activity_tracking_main.py 

	This Python script uses MediaPipe and OpenCV to monitor human activity (working vs idle) by tracking key body landmarks (wrists, knees, and ankles) from a video feed.
	
	Video Input: Reads the video path from a config.json file. 

	Pose Estimation: Uses MediaPipe to detect body landmarks in the frame.

	Region Cropping: Focuses on a central region of the frame for better accuracy.

	Movement Detection: Calculates the Euclidean distance between current and previous positions of:

	Wrists (left & right)

	Knees (left & right)

	Ankles (left & right)

	Activity Classification:

	If movement exceeds a threshold: "Working"

	If no movement for 10 minutes: "Idle"

	Logging: Records coordinates and timestamps in activity_log.csv.

	Display: Shows the status live on the video frame.

	Exit: Press 'q' to quit.
	
	
 restart.service : 
 
	 Service runs a Python script (restart_activity_tracking ) continuously in the background. The script monitors and controls application processes based on time conditions. 
	 it ensures the script starts at boot and restarts automatically if it crashes.