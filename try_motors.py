#!/usr/bin/env python3
"""
test_motors_right_inverted.py
Test script for two DC motors via L293D where the RIGHT motor is wired reversed.
This script always inverts the right motor in software so "forward" drives both
wheels forward (compensating for the wiring).
"""

import RPi.GPIO as GPIO
import time

# --- Pin setup (BCM) ---
EN_PIN = 18

# Left motor (Motor A) direction pins
MOTOR_A_IN1 = 23
MOTOR_A_IN2 = 24

# Right motor (Motor B) direction pins (wired reversed)
MOTOR_B_IN3 = 27
MOTOR_B_IN4 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_PIN, GPIO.OUT)
GPIO.setup(MOTOR_A_IN1, GPIO.OUT)
GPIO.setup(MOTOR_A_IN2, GPIO.OUT)
GPIO.setup(MOTOR_B_IN3, GPIO.OUT)
GPIO.setup(MOTOR_B_IN4, GPIO.OUT)

# Enable both motors
GPIO.output(EN_PIN, GPIO.HIGH)

# --- Motor helper functions ---

# Left motor (normal logic)
def motor_a_forward():
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)

def motor_a_backward():
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.HIGH)

# Right motor (ALWAYS inverted in software to compensate wiring)
def motor_b_forward():
    # Because the right motor is wired reversed, we drive the opposite hardware signals
    GPIO.output(MOTOR_B_IN3, GPIO.LOW)
    GPIO.output(MOTOR_B_IN4, GPIO.HIGH)

def motor_b_backward():
    GPIO.output(MOTOR_B_IN3, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN4, GPIO.LOW)

def stop_all():
    GPIO.output(MOTOR_A_IN1, GPIO.LOW)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)
    GPIO.output(MOTOR_B_IN3, GPIO.LOW)
    GPIO.output(MOTOR_B_IN4, GPIO.LOW)

# --- High level movements ---
def forward(duration=2):
    motor_a_forward()
    motor_b_forward()
    time.sleep(duration)
    stop_all()

def backward(duration=2):
    motor_a_backward()
    motor_b_backward()
    time.sleep(duration)
    stop_all()

def turn_left(duration=1):
    # left turn: left wheel backward, right wheel forward
    motor_a_backward()
    motor_b_forward()
    time.sleep(duration)
    stop_all()

def turn_right(duration=1):
    # right turn: left wheel forward, right wheel backward
    motor_a_forward()
    motor_b_backward()
    time.sleep(duration)
    stop_all()

# --- Main test sequence ---
if __name__ == "__main__":
    try:
        print("Motor direction test (right motor permanently inverted). Ctrl+C to stop.")
        time.sleep(1)

        print("Forward for 2s")
        forward(2)

        print("Backward for 2s")
        backward(2)

        print("Turn left for 1s")
        turn_left(1)

        print("Turn right for 1s")
        turn_right(1)

        print("Finished. Stopping motors.")
        stop_all()

    except KeyboardInterrupt:
        print("\nInterrupted — stopping motors.")
        stop_all()

    finally:
        # Disable motors and cleanup GPIO
        GPIO.output(EN_PIN, GPIO.LOW)
        GPIO.cleanup()
