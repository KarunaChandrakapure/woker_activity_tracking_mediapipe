

import os
import time
import psutil
import datetime

# Time boundaries
start_time = datetime.time(0, 0, 0)
end_time = datetime.time(23, 59, 0)

# Commands
script_name = "activity_tracking_main.py"
start_command = "sh activity_tracking_main.sh"


def is_process_running():
    """Check if the target process is running."""
    for proc in psutil.process_iter(['cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and "python3" in cmdline and script_name in cmdline:
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def run_script():
    print("[INFO] Starting Application...")
    os.system(start_command)

def stop_process(pid):
    print(f"[INFO] Stopping Application (PID: {pid})...")
    os.system(f"sudo kill -15 {pid}")

def within_time_window(current, start, end):
    return start <= current <= end

if __name__ == "__main__":
    while True:
        try:
            current_time = datetime.datetime.now().time()
            pid = is_process_running()

            if within_time_window(current_time, start_time, end_time):
                if not pid:
                    run_script()
            else:
                if pid:
                    stop_process(pid)

            time.sleep(5)  # Check every 5 seconds
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(5)

