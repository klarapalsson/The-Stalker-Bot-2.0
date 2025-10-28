import RPi.GPIO as GPIO
import time

# --- Pin setup ---
en_pin = 18

motor_a_in1 = 23
motor_a_in2 = 24
motor_b_in3 = 27
motor_b_in4 = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(en_pin, GPIO.OUT)
GPIO.setup(motor_a_in1, GPIO.OUT)
GPIO.setup(motor_a_in2, GPIO.OUT)
GPIO.setup(motor_b_in3, GPIO.OUT)
GPIO.setup(motor_b_in4, GPIO.OUT)

# Enable both motors
GPIO.output(en_pin, GPIO.HIGH)

def motor_a_forward():
    GPIO.output(motor_a_in1, GPIO.HIGH)
    GPIO.output(motor_a_in2, GPIO.LOW)

def motor_a_backward():
    GPIO.output(motor_a_in1, GPIO.LOW)
    GPIO.output(motor_a_in2, GPIO.HIGH)

def motor_b_forward():
    GPIO.output(motor_b_in3, GPIO.HIGH)
    GPIO.output(motor_b_in4, GPIO.LOW)

def motor_b_backward():
    GPIO.output(motor_b_in3, GPIO.LOW)
    GPIO.output(motor_b_in4, GPIO.HIGH)

def stop_all():
    GPIO.output(motor_a_in1, GPIO.LOW)
    GPIO.output(motor_a_in2, GPIO.LOW)
    GPIO.output(motor_b_in3, GPIO.LOW)
    GPIO.output(motor_b_in4, GPIO.LOW)

try:
    print("Motors forward...")
    motor_a_forward()
    motor_b_forward()
    time.sleep(2)

    print("Motors backward...")
    motor_a_backward()
    motor_b_backward()
    time.sleep(2)

    print("Turning left...")
    motor_a_backward()
    motor_b_forward()
    time.sleep(2)

    print("Turning right...")
    motor_a_forward()
    motor_b_backward()
    time.sleep(2)

    print("Stopping motors.")
    stop_all()

except KeyboardInterrupt:
    pass

finally:
    stop_all()
    GPIO.output(en_pin, GPIO.LOW)
    GPIO.cleanup()
