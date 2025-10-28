
# --- Imports ---

import lgpio
import RPi.GPIO as GPIO

from main import print_and_log

# --- Definitions ---



# --- Setup ---

handle = lgpio.gpiochip_open(0) # Opens GPIO controller 0 and returns a handle

# --- Pin setup (BCM) ---
EN_PIN1 = 18
EN_PIN2 = 19

# Left motor (Motor L) direction pins
MOTOR_L_IN1 = 23
MOTOR_L_IN2 = 24

# Right motor (Motor R) direction pins (wired reversed)
MOTOR_R_IN3 = 27
MOTOR_R_IN4 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(EN_PIN1, GPIO.OUT)
GPIO.setup(EN_PIN2, GPIO.OUT)
GPIO.setup(MOTOR_L_IN1, GPIO.OUT)
GPIO.setup(MOTOR_L_IN2, GPIO.OUT)
GPIO.setup(MOTOR_R_IN3, GPIO.OUT)
GPIO.setup(MOTOR_R_IN4, GPIO.OUT)

# Enable both motors
GPIO.output(EN_PIN1, GPIO.HIGH)
GPIO.output(EN_PIN2, GPIO.HIGH)

# --- Functions ---

# Left motor (normal logic)
def motor_l_forward():
    GPIO.output(MOTOR_L_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_L_IN2, GPIO.LOW)

def motor_l_backward():
    GPIO.output(MOTOR_L_IN1, GPIO.LOW)
    GPIO.output(MOTOR_L_IN2, GPIO.HIGH)

# Right motor (ALWAYS inverted in software to compensate wiring)
def motor_r_forward():
    # Because the right motor is wired reversed, we drive the opposite hardware signals
    GPIO.output(MOTOR_R_IN3, GPIO.LOW)
    GPIO.output(MOTOR_R_IN4, GPIO.HIGH)

def motor_r_backward():
    GPIO.output(MOTOR_R_IN3, GPIO.HIGH)
    GPIO.output(MOTOR_R_IN4, GPIO.LOW)

def stop_all():
    GPIO.output(MOTOR_L_IN1, GPIO.LOW)
    GPIO.output(MOTOR_L_IN2, GPIO.LOW)
    GPIO.output(MOTOR_R_IN3, GPIO.LOW)
    GPIO.output(MOTOR_R_IN4, GPIO.LOW)

# --- High level movements ---
def forward():
    motor_l_forward()
    motor_r_forward()

def backward():
    motor_l_backward()
    motor_r_backward()

def turn_left():
    # left turn: left wheel backward, right wheel forward
    motor_l_backward()
    motor_r_forward()

    print_and_log(f"Turning left!")

def turn_right():
    # right turn: left wheel forward, right wheel backward
    motor_l_forward()
    motor_r_backward()

    print_and_log(f"Turning right!")

