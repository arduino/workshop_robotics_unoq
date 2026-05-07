# 🟢 ROBOTBRAG26 - AI Vision & Joystick Controlled Robot with Arduino UNO Q

This project combines manual remote control with real-time Computer Vision.
The robot can be driven via a virtual joystick on a web dashboard while an AI model (Object Detection) identifies objects in the camera stream and displays bounding boxes in real-time.

## HW Setup
- Arduino UNO Q
- 2x Continuous Rotation Servos (Connected to Pin 9 and Pin 10)
- USB Webcam

## How It Works 
- **Manual Robot Control**: The web dashboard features a virtual joystick. When moved, it calculates differential drive values (Left and Right motor speeds) and sends them to Python via Socket.io. Python then forwards these commands to the Arduino sketch using the RPC Bridge.
- **AI Vision**: The Python application runs an Object Detection brick that processes the webcam feed. It identifies objects (like bottles, cups, or people) and overlays bounding boxes directly onto the video stream displayed on the web page.

## Bricks
Bricks are pre-built, modular components that you can add to your Arduino App to quickly introduce complex features.

The bricks used are:

- **Video Object Detection**: An AI-powered brick that captures video frames and runs a detection model to identify and locate multiple objects in real-time.
- **WebUI HTML**: A lightweight web server that hosts the interactive dashboard, providing the interface for the joystick and the video stream.

## Project Structure

- `sketch/`: Contains the Arduino code to drive the servos.
- `python/`: Contains the main logic for the AI engine and Bridge communication.
- `assets/`: Contains the web interface files (HTML, CSS, JS).

## Authors

- Leonardo Cavagnis
- Giovanni Bruno