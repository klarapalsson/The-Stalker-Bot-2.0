
# --- Imports ---

import RPi.GPIO as GPIO
from motor_controller import MOTOR_ENABLING_PIN_1, MOTOR_ENABLING_PIN_2, LEFT_MOTOR_INPUT_PIN_1, LEFT_MOTOR_INPUT_PIN_2, RIGHT_MOTOR_INPUT_PIN_3, RIGHT_MOTOR_INPUT_PIN_4, ALL_PINS
import time

# --- Pin definitions (BCM) ---
EN_LEFT  = 18   # L293D EN1
EN_RIGHT = 19   # L293D EN2
IN1 = 23        # Left motor direction A
IN2 = 24        # Left motor direction B
IN3 = 27        # Right motor direction A
IN4 = 22        # Right motor direction B

# --- Setup ---
GPIO.setmode(GPIO.BCM)
for pin in [IN1, IN2, IN3, IN4, EN_LEFT, EN_RIGHT]:
    GPIO.setup(pin, GPIO.OUT)

# PWM setup for both motors (frequency ~1000Hz)
pwm_left = GPIO.PWM(EN_LEFT, 1000)
pwm_right = GPIO.PWM(EN_RIGHT, 1000)
pwm_left.start(100)   # Full speed
pwm_right.start(100)  # Full speed

# --- Motor control functions ---
def left_forward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)

def left_backward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)

# Right motor is inverted
def right_forward():
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)

def right_backward():
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)

def stop_all():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# --- High-level movements ---
def forward(duration=2, speed=100):
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)
    left_forward()
    right_forward()
    time.sleep(duration)
    stop_all()

def backward(duration=2, speed=100):
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)
    left_backward()
    right_backward()
    time.sleep(duration)
    stop_all()

def turn_left(duration=1, speed=100):
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)
    left_backward()
    right_forward()
    time.sleep(duration)
    stop_all()

def turn_right(duration=1, speed=100):
    pwm_left.ChangeDutyCycle(speed)
    pwm_right.ChangeDutyCycle(speed)
    left_forward()
    right_backward()
    time.sleep(duration)
    stop_all()

# --- Main test ---
if __name__ == "__main__":
    try:
        print("Dual-motor test starting (right motor inverted).")
        time.sleep(1)

        print("Forward")
        forward(2)

        print("Backward")
        backward(2)

        print("Turn left")
        turn_left(1)

        print("Turn right")
        turn_right(1)

        print("Speed test 50% forward")
        pwm_left.ChangeDutyCycle(50)
        pwm_right.ChangeDutyCycle(50)
        left_forward()
        right_forward()
        time.sleep(2)
        stop_all()

    except KeyboardInterrupt:
        print("\nInterrupted — stopping motors.")
        stop_all()

    finally:
        pwm_left.stop()
        pwm_right.stop()
        GPIO.cleanup()
