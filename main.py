
# --- Imports ---

import time
import object_detection
import obstacle_avoidance
from ultrasonic_sensor import get_distance
from motor_controller import forward, backwards, tank_turn_counterclockwise, tank_turn_clockwise, stop, disable_motors
#import pyttsx3

# --- General definitions ---

target_minimum_area = 0.35
target_maximum_area = 0.5

safe_distance_in_cm = 50

follow_loop_update_time = 0.1

# --- Log initialization ---

log_file_path = "robot_log.txt"

with open(log_file_path, "w") as f:
    f.write("Robot session started")

# --- Text-to-speech engine initialization ---
"""
text_to_speech_engine = pyttsx3.init()
text_to_speech_engine.setProperty('rate', 170) # Adjust speaking speed
text_to_speech_engine.setProperty('volume', 1.0) # Max volume
"""
# --- Helper functions ---

def print_log_and_say(message):

    """
    Prints a message, writes it to a log file and says it aloud.

    Arguments:
        "message":

    Returns:
        None
    
    """

    print("\n" + message)

    with open(log_file_path, "a") as f:
        f.write("\n" + message)

    object_detection.video_status_text = message # Update the video status text in the AI detection module
    """
    try:
        text_to_speech_engine.say(message)
        text_to_speech_engine.runAndWait()

    except Exception as e:
        print(f"Speech error: {e}")
    """
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

        #distance_in_cm = get_distance() # Gets distance to closest obstacle/wall from ultrasonic sensor    

        if obstacle: #or distance_in_cm <= safe_distance_in_cm: # If either the AI camera or the ultrasonic sensor detects an obstacle:
            print_log_and_say("Trying to avoid an obstacle...")
            #obstacle_avoidance.avoid_obstacle()
            stop()
            continue
            
        if person_area is None:
            print_log_and_say("No person detected, waiting...")
            stop()
            continue
        
        print_log_and_say(f"Person takes up {person_area:.2f} of the total frame size")

        if person_area < target_minimum_area:
            
            print_log_and_say("Person is too far away, trying to move forward...")
            forward(direction, speed, bias)
            
        elif person_area > target_maximum_area:
            print_log_and_say("Person is too close, moving backwards...")
            backwards(direction, speed, bias)
        else:
            print_log_and_say("Distance is OK, stopping...")
        
            if direction == "right":
                tank_turn_clockwise()

            elif direction == "left":
                tank_turn_counterclockwise()

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
