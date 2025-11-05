
# --- Imports ---

import object_detection
import time
from motor_controller import forward, backwards, tank_turn_counterclockwise, tank_turn_clockwise, stop

# --- Helper functions ---

def check_left():

    """
    Turns slightly left to check that direction, then returns to original orientation.

    Arguments:
        None

    Returns:
        bool: True if there is an obstacle on the left, False if path is clear.
    
    """

    tank_turn_counterclockwise()
    time.sleep(0.4)  # adjust rotation
    stop()
    time.sleep(0.2)
    obstacle_left = object_detection.get_tracking_data()[3]
    tank_turn_clockwise()  # turn back
    time.sleep(0.4)
    stop()
    time.sleep(0.2)
    return obstacle_left

def check_right():

    """
    Turns slightly right to check that direction, then returns to original orientation.
    
    Arguments:
        None

    Returns:
        bool: True if there is an obstacle on the right, False if path is clear.
    
    """

    tank_turn_clockwise()
    time.sleep(0.4)
    stop()
    time.sleep(0.2)
    obstacle_right = object_detection.get_tracking_data()[3]
    tank_turn_counterclockwise()  # turn back
    time.sleep(0.4)
    stop()
    time.sleep(0.2)
    return obstacle_right


def go_around_left():

    """
    Turns left and moves forward around the obstacle.
    
    Arguments:
        None

    Returns:
        None
    
    """

    tank_turn_counterclockwise()
    time.sleep(0.6)
    stop()
    forward()
    time.sleep(1.2)
    stop()

def go_around_right():

    """
    Turns right and moves forward around the obstacle.
    
    Arguments:
        None

    Returns:
        None

    """

    tank_turn_clockwise()
    time.sleep(0.6)
    stop()
    forward()
    time.sleep(1.2)
    stop()

# --- Main function ---

def avoid_obstacle():

    """
    Avoids an obstacle by stopping, turning the robot slightly left/right,
    checking with the camera, and going around.

    Arguments:
        None

    Returns:
        None

    """

    print("Stopping...")
    stop()
    time.sleep(0.3)

    # --- Check left ---
    print("Checking left...")
    obstacle_left = check_left()
    
    # --- Check right ---
    print("Checking right...")
    obstacle_right = check_right()

    # --- Decide what to do ---
    if not obstacle_left:
        print("Path clear on left, turning left...")
        go_around_left()

    elif not obstacle_right:
        print("Path clear on right, turning right...")
        go_around_right()

    else:
        print("Obstacles both sides, moving backwards...")
        backwards()
        time.sleep(1)
        avoid_obstacle()

# --- Execution ---

if __name__ == "__main__":

    check_left()
    time.sleep(3)

    check_right()
    time.sleep(3)