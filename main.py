
# --- Imports ---

import time

import speaker
import object_detection
import obstacle_avoidance
from motor_controller import forward, backwards, tank_turn_counterclockwise, tank_turn_clockwise, stop, disable_motors

# --- General definitions ---

target_minimum_area = 0.35
target_maximum_area = 0.5

follow_loop_update_time = 0.1

# --- Helper functions ---

def print_and_say(message):

    """
    Prints a message, writes it to a log file and says it aloud.

    Arguments:
        "message":

    Returns:
        None
    
    """

    print("\n" + message)

    object_detection.video_status_text = message # Update the video status text in the AI detection module

    speaker.say_latest(message)
    
# --- Main program loop ---

def follow():

    """
    Runs the person-following loop.

    Arguments:
        None

    Returns:
        None
    
    """

    while True:

        direction, bias, speed, obstacle, person_area = object_detection.get_tracking_data() # Gets necessary data from the AI camera

        if obstacle:  #If the AI camera detects an obstacle:
            print_and_say("Trying to avoid an obstacle...")
            #obstacle_avoidance.avoid_obstacle()
            stop()
            continue
            
        if person_area is None:
            print_and_say("No person detected, waiting...")
            stop()
            continue
        
        print_and_say(f"Person takes up {person_area:.2f} of the total frame size")

        if person_area < target_minimum_area:
            
            print_and_say("Person is too far away, trying to move forward...")
            forward(direction, speed, bias)
            
        elif person_area > target_maximum_area:
            print_and_say("Person is too close, moving backwards...")
            backwards(direction, speed, bias)
        else:
            print_and_say("Distance is OK, stopping...")
        
            if direction == "right":
                tank_turn_clockwise(50, bias)

            elif direction == "left":
                tank_turn_counterclockwise(50, bias)

            else:
                stop()

        time.sleep(follow_loop_update_time)

# --- Execution ---

if __name__ == "__main__":

    try:
        follow()

    except KeyboardInterrupt:
        stop()
        
    finally:
        disable_motors()
