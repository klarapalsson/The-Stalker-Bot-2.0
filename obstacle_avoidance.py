
# --- Imports ---

#import object_detection
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

    tank_turn_counterclockwise(100, 0.45)
    time.sleep(0.5)  # adjust rotation
    stop()
    #obstacle_left = object_detection.get_tracking_data()[3]
    time.sleep(0.5)
    tank_turn_clockwise(100, 0.45)  # turn back
    time.sleep(0.55)
    stop()
    time.sleep(0.5)
    #return obstacle_left

def check_right():

    """
    Turns slightly right to check that direction, then returns to original orientation.
    
    Arguments:
        None

    Returns:
        bool: True if there is an obstacle on the right, False if path is clear.
    
    """

    tank_turn_clockwise(100, 0.45)
    time.sleep(0.55)
    stop()
    #obstacle_right = object_detection.get_tracking_data()[3]
    time.sleep(0.5)
    tank_turn_counterclockwise(100, 0.45)  # turn back
    time.sleep(0.5)
    stop()
    time.sleep(0.5)
    #return obstacle_right


def go_around_left():

    """
    Turns left and moves forward around the obstacle.
    
    Arguments:
        None

    Returns:
        None
    
    """

    tank_turn_counterclockwise(100, 0.45)
    time.sleep(0.5)
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

    tank_turn_clockwise(100, 0.45)
    time.sleep(0.55)
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

# --- Obstacle Test ---

if __name__ == "__main__":
    time.sleep(20)
    go_around_left() 
    time.sleep(5)
    go_around_right()
    