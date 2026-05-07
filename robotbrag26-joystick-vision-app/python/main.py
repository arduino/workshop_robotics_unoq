from arduino.app_utils import *
from arduino.app_bricks.web_ui import WebUI
from arduino.app_bricks.video_objectdetection import VideoObjectDetection
from datetime import datetime, UTC

# Initialize the Web UI brick
ui = WebUI()

# Initialize AI detection with fixed confidence at 0.6 (60%)
detection_stream = VideoObjectDetection(confidence=0.6, debounce_sec=0.5)

# JOYSTICK LOGIC 
def on_joystick_move(client, data):
    """
    Handle joystick movement data from the browser.
    Receives 'l' and 'r' values (0-180) and sends them to Arduino.
    """
    l = data.get("l", 90)
    r = data.get("r", 90)
    Bridge.call("drive", l, r)

ui.on_message("move_robot", on_joystick_move)

# AI VISION LOGIC
def send_detections_to_ui(detections: dict):
    """
    Callback triggered when objects are detected.
    Sends detection info to the frontend via Socket.io.
    """
    for key, values in detections.items():
        for value in values:
            entry = {
                "content": key,
                "confidence": value.get("confidence"),
                "timestamp": datetime.now(UTC).isoformat()
            }
            ui.send_message("detection", message=entry)

detection_stream.on_detect_all(send_detections_to_ui)

# Start the application
App.run()