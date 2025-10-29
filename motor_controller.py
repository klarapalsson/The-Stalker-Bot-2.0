
# --- Imports ---

import lgpio
import time

# --- Definitions ---

# Left motor pins

LEFT_MOTOR_ENABLING_PIN = 18

LEFT_MOTOR_INPUT_PIN_1 = 23
LEFT_MOTOR_INPUT_PIN_2 = 24

# Right motor pins

RIGHT_MOTOR_ENABLING_PIN = 19

RIGHT_MOTOR_INPUT_PIN_3 = 27
RIGHT_MOTOR_INPUT_PIN_4 = 22

# Pin lists

MOTOR_INPUT_PINS = [LEFT_MOTOR_INPUT_PIN_1, LEFT_MOTOR_INPUT_PIN_2, RIGHT_MOTOR_INPUT_PIN_3, RIGHT_MOTOR_INPUT_PIN_4]

ALL_PINS = [LEFT_MOTOR_ENABLING_PIN, RIGHT_MOTOR_ENABLING_PIN] + MOTOR_INPUT_PINS

PWM_FREQUENCY = 1000 # Frequency for PWM instances (in Hz)

# --- Setup ---

CHIP_HANDLE = lgpio.gpiochip_open(0)

for pin in ALL_PINS:
    lgpio.gpio_claim_output(CHIP_HANDLE, pin, 0) # Sets all motor control pins as outputs and initializes them to LOW

for pin in [LEFT_MOTOR_ENABLING_PIN, RIGHT_MOTOR_ENABLING_PIN]:
    lgpio.gpio_write(CHIP_HANDLE, pin, 1) # Enables the motors by setting their enabling pins HIGH

PWM_LEFT_MOTOR = lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, 0) # Creates a PWM instance on the left motor enabling pin with the defined frequency and a duty cycle of 0 %
PWM_RIGHT_MOTOR = lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, 0) # Creates a PWM instance on the right motor enabling pin with the defined frequency and a duty cycle of 0 %

# --- Motor controlling functions ---

# Left motor

def left_motor_forward():

    """
    Makes the left motor go forward.

    Arguments:
        None
    
    Returns:
        None

    """

    lgpio.gpio_write(CHIP_HANDLE, LEFT_MOTOR_INPUT_PIN_1, 1)
    lgpio.gpio_write(CHIP_HANDLE, LEFT_MOTOR_INPUT_PIN_2, 0)

def left_motor_backwards():

    """
    Makes the left motor go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    lgpio.gpio_write(CHIP_HANDLE, LEFT_MOTOR_INPUT_PIN_1, 0)
    lgpio.gpio_write(CHIP_HANDLE, LEFT_MOTOR_INPUT_PIN_2, 1)

# Right motor (inverted)

def right_motor_forward():

    """
    Makes the right motor go forward.

    Arguments:
        None
    
    Returns:
        None

    """

    lgpio.gpio_write(CHIP_HANDLE, RIGHT_MOTOR_INPUT_PIN_3, 0)
    lgpio.gpio_write(CHIP_HANDLE, RIGHT_MOTOR_INPUT_PIN_4, 1)

def right_motor_backwards():

    """
    Makes the right motor go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    lgpio.gpio_write(CHIP_HANDLE, RIGHT_MOTOR_INPUT_PIN_3, 1)
    lgpio.gpio_write(CHIP_HANDLE, RIGHT_MOTOR_INPUT_PIN_4, 0)

def stop():

    """
    Makes both motors stop.

    Arguments:
        None
    
    Returns:
        None
    
    """

    for pin in MOTOR_INPUT_PINS:
        lgpio.gpio_write(CHIP_HANDLE, pin, 0)

# --- Movement functions ---

def forward(direction = "centered", speed = 100, bias = 0.5):

    """
    Makes the robot go forward.

    Arguments:
        None
    
    Returns:
        None
    
    """

    if direction == "right":
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed * bias)

    elif direction == "left":
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed * bias)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)

    else:
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)

    left_motor_forward()
    right_motor_forward()

def backwards(direction = "centered", speed = 100, bias = 0.5):

    """
    Makes the robot go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    if direction == "right":
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed * bias)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
    
    elif direction == "left":
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed * bias)

    else:
        lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
        lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)

    left_motor_backwards()
    right_motor_backwards()

def tank_turn_counterclockwise(speed = 100):

    """
    Makes the robot tank turn counterclockwise.

    Arguments:
        None
    
    Returns:
        None
    
    """

    lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
    lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)

    left_motor_backwards()
    right_motor_forward()

def tank_turn_clockwise(speed = 100):

    """
    Makes the robot tank turn clockwise.

    Arguments:
        None
    
    Returns:
        None
    
    """

    lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)
    lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, speed)

    left_motor_forward()
    right_motor_backwards()

# --- Miscellaneous functions ---

def disable_motors():

    """
    Disables the motors by setting their enabling pins LOW.

    Arguments:
        None
    
    Returns:
        None

    """

    for pin in [LEFT_MOTOR_ENABLING_PIN, RIGHT_MOTOR_ENABLING_PIN]:
        lgpio.gpio_write(CHIP_HANDLE, pin, 0)

def cleanup():

    """
    Cleans up by stopping the PWM instances and closing the GPIO chip handle.

    Arguments:
        None

    Returns:
        None

    """

    lgpio.tx_pwm(CHIP_HANDLE, LEFT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, 0)
    lgpio.tx_pwm(CHIP_HANDLE, RIGHT_MOTOR_ENABLING_PIN, PWM_FREQUENCY, 0)
    lgpio.gpiochip_close(CHIP_HANDLE)

# --- Test ---

if __name__ == "__main__":

    try:

        print("\nMotor controller test starting...")

        print("\nTrying to move forward...")

        forward("centered", 100, 1)
        time.sleep(0.5)
        stop()

        forward("centered", 75, 1)
        time.sleep(0.5)
        stop()

        forward("centered", 50, 1)
        time.sleep(0.5)
        stop()
        
        forward("centered", 25, 1)
        time.sleep(0.5)
        stop()

        print("\nTrying to move backwards...")
        
        backwards("centered", 100, 1)
        time.sleep(0.5)
        stop()

        backwards("centered", 75, 1)
        time.sleep(0.5)
        stop()

        backwards("centered", 50, 1)
        time.sleep(0.5)
        stop()

        backwards("centered", 25, 1)
        time.sleep(0.5)
        stop()

        print("\nTrying to tank turn counterclockwise...")

        tank_turn_counterclockwise(100)
        time.sleep(0.5)
        stop()

        print("\nTrying to tank turn clockwise...")

        tank_turn_clockwise(100)
        time.sleep(0.5)
        stop()

    except KeyboardInterrupt:
        print("\nInterrupted — stopping motors...")
        stop()

    finally:
        stop()
        disable_motors()
        cleanup()
        print("\nMotor controller test finished.\n")
