
# --- Imports ---

import RPi.GPIO as GPIO
from motor_controller import ALL_PINS, PWM_LEFT_MOTOR, PWM_RIGHT_MOTOR, forward, backwards, tank_turn_counterclockwise, tank_turn_clockwise, stop

# --- Setup ---

GPIO.setmode(GPIO.BCM)

for pin in ALL_PINS:
    GPIO.setup(pin, GPIO.OUT)

PWM_LEFT_MOTOR.start(100)
PWM_RIGHT_MOTOR.start(100)

# --- Main testing program ---

if __name__ == "__main__":

    try:

        print("\nMotor controller test starting...")

        print("\nTrying to move forward...")
        forward(0.5, 100)
        forward(0.5, 75)
        forward(0.5, 50)
        forward(0.5, 25)

        print("\nTrying to move backwards...")
        backwards(0.5, 100)
        backwards(0.5, 75)
        backwards(0.5, 50)
        backwards(0.5, 25)

        print("\nTrying to tank turn counterclockwise...")
        tank_turn_counterclockwise(1, 100)

        print("\nTrying to tank turn clockwise...")
        tank_turn_clockwise(1, 100)

    except KeyboardInterrupt:
        print("\nInterrupted — stopping motors...")
        stop()

    finally:
        PWM_LEFT_MOTOR.stop()
        PWM_RIGHT_MOTOR.stop()
        GPIO.cleanup()
