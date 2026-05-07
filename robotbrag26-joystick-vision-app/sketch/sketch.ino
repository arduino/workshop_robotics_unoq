#include <Arduino_RouterBridge.h>
#include <Arduino_HardwareServo.h>

#define L_WHEEL_PIN 9
#define R_WHEEL_PIN 10

HardwareServo servoL;
HardwareServo servoR;

/**
 * Function called by the RPC Bridge.
 * Receives motor values from the Python script.
 */
void drive_motors(int left_val, int right_val) {
    servoL.write(left_val);
    servoR.write(right_val);
}

void setup() {
    // Attach servos to Pin 9 (Left) and Pin 10 (Right)
    servoL.attach(L_WHEEL_PIN);
    servoR.attach(R_WHEEL_PIN);

    // Initialize in neutral position (stopped)
    servoL.write(90);
    servoR.write(90);

    // Initialize communication Bridge
    Bridge.begin();
    
    // Provide the "drive" function to the Bridge for remote calls
    Bridge.provide("drive", drive_motors);
}

void loop() {
    // Automatic management via Bridge - no code needed here
}