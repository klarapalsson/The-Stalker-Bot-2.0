#!/usr/bin/env python3
"""
test_motors_inverted_right.py
Same test as before but inverts the right motor in software so that
"forward" moves both wheels forward (although the right motor is wired reversed).
"""

import RPi.GPIO as GPIO
import time

# --- Pin setup (BCM) ---
en_pin = 18

motor_a_in1 = 23   # Left motor dir pin 1 (IN1)
motor_a_in2 = 24   # Left motor dir pin 2 (IN2)

motor_b_in3 = 27   # Right motor dir pin 1 (IN3)
motor_b_in4 = 22   # Right motor dir pin 2 (IN4)

# If True, motor B outputs are logically inverted (wired reversed)
INVERT_MOTOR_B = True

GPIO.setmode(GPIO.BCM)
GPIO.setup(en_pin, GPIO.OUT)
GPIO.setup(motor_a_in1, GPIO.OUT)
GPIO.setup(motor_a_in2, GPIO.OUT)
GPIO.setup(motor_b_in3, GPIO.OUT)
GPIO.setup(motor_b_in4, GPIO.OUT)

# Enable both motors
GPIO.output(en_pin, GPIO.HIGH)

# --- Motor helpers ---
def motor_a_forward():
    GPIO.output(motor_a_in1, GPIO.HIGH)
    GPIO.output(motor_a_in2, GPIO.LOW)

def motor_a_backward():
    GPIO.output(motor_a_in1, GPIO.LOW)
    GPIO.output(motor_a_in2, GPIO.HIGH)

def motor_b_forward():
    """Logical forward for Motor B (compensates if inverted)."""
    if INVERT_MOTOR_B:
        # wired reversed, so to go logical-forward we must drive hardware-backward
        GPIO.output(motor_b_in3, GPIO.LOW)
        GPIO.output(motor_b_in4, GPIO.HIGH)
    else:
        GPIO.output(motor_b_in3, GPIO.HIGH)
        GPIO.output(motor_b_in4, GPIO.LOW)

def motor_b_backward():
    """Logical backward for Motor B (compensates if inverted)."""
    if INVERT_MOTOR_B:
        GPIO.output(motor_b_in3, GPIO.HIGH)
        GPIO.output(motor_b_in4, GPIO.LOW)
    else:
        GPIO.output(motor_b_in3, GPIO.LOW)
        GPIO.output(motor_b_in4, GPIO.HIGH)

def stop_all():
    GPIO.output(motor_a_in1, GPIO.LOW)
    GPIO.output(motor_a_in2, GPIO.LOW)
    GPIO.output(motor_b_in3, GPIO.LOW)
    GPIO.output(motor_b_in4, GPIO.LOW)

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

# --- Test sequence ---
if __name__ == "__main__":
    try:
        print("Motor direction test (right motor inverted in software). Ctrl+C to stop.")
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
        GPIO.output(en_pin, GPIO.LOW)
        GPIO.cleanup()
