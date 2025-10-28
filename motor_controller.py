
# --- Imports ---

import RPi.GPIO as GPIO

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

ALL_PINS = LEFT_MOTOR_ENABLING_PIN + RIGHT_MOTOR_ENABLING_PIN + MOTOR_INPUT_PINS

# --- Setup ---

GPIO.setmode(GPIO.BCM) # Sets pin numbering method to BCM

for pin in ALL_PINS:
    GPIO.setup(pin, GPIO.OUT) # Sets all pins to outputs

for pin in [LEFT_MOTOR_ENABLING_PIN, RIGHT_MOTOR_ENABLING_PIN]:
    GPIO.output(pin, GPIO.HIGH) # Enables the motors by setting their enabling pins HIGH

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

    GPIO.output(LEFT_MOTOR_INPUT_PIN_1, GPIO.HIGH)
    GPIO.output(LEFT_MOTOR_INPUT_PIN_2, GPIO.LOW)

def left_motor_backwards():

    """
    Makes the left motor go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    GPIO.output(LEFT_MOTOR_INPUT_PIN_1, GPIO.LOW)
    GPIO.output(LEFT_MOTOR_INPUT_PIN_2, GPIO.HIGH)

# Right motor (inverted)

def right_motor_forward():

    """
    Makes the right motor go forward.

    Arguments:
        None
    
    Returns:
        None

    """

    GPIO.output(RIGHT_MOTOR_INPUT_PIN_3, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_INPUT_PIN_4, GPIO.HIGH)

def right_motor_backwards():

    """
    Makes the right motor go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    GPIO.output(RIGHT_MOTOR_INPUT_PIN_3, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_INPUT_PIN_4, GPIO.LOW)

def stop():

    """
    Makes both motors stop.

    Arguments:
        None
    
    Returns:
        None
    
    """

    for pin in MOTOR_INPUT_PINS:
        GPIO.output(pin, GPIO.LOW)

# --- Movement functions ---

def forward():

    """
    Makes the robot go forward.

    Arguments:
        None
    
    Returns:
        None
    
    """

    left_motor_forward()
    right_motor_forward()

def backwards():

    """
    Makes the robot go backwards.

    Arguments:
        None
    
    Returns:
        None
    
    """

    left_motor_backwards()
    right_motor_backwards()

def tank_turn_counterclockwise():

    """
    Makes the robot tank turn counterclockwise.

    Arguments:
        None
    
    Returns:
        None
    
    """

    left_motor_backwards()
    right_motor_forward()

def tank_turn_clockwise():

    """
    Makes the robot tank turn clockwise.

    Arguments:
        None
    
    Returns:
        None
    
    """

    left_motor_forward()
    right_motor_backwards()

def disable_motors():

    """
    Disables the motors by setting their enabling pins LOW.

    Arguments:
        None
    
    Returns:
        None

    """

    for pin in [LEFT_MOTOR_ENABLING_PIN, RIGHT_MOTOR_ENABLING_PIN]:
        GPIO.output(pin, GPIO.LOW)