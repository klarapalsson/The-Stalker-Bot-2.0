
# --- Imports ---

import RPi.GPIO as GPIO
import time
import ai_detection
from ultrasonic_sensor import get_distance
from motor_controller import EN_PIN1, EN_PIN2, forward, backward, turn_left, turn_right, stop_all as stop

# --- General definitions ---
target_minimum_area = 0.35
target_maximum_area = 0.5

safe_distance_in_cm = 50

follow_loop_update_time = 0.1

# --- Log initialization ---

log_file_path = "robot_log.txt"

with open(log_file_path, "w") as f:
    f.write("Robot session started")

# --- Helper functions ---

def print_and_log(message):

    """
    Prints a message and writes it to a log file.

    Arguments:
        "message":

    Returns:
        None
    
    """

    print("\n" + message)

    with open(log_file_path, "a") as f:
        f.write("\n" + message)

    ai_detection.video_status_text = message # Update the video status text in the AI detection module

def avoid_obstacle():

    """
    Avoids an obstacle by stopping.

    Arguments:
        None

    Returns:
        None
    
    """

    print_and_log("Stopping...")
    stop()

# --- Main program loop ---

def follow():

    global first_timer, second_timer, first_timer_off, second_timer_off

    """
    Runs the person-following loop.

    Arguments:
        None

    Returns:
        None
    
    """

    while True:

        angle, direction, obstacle, person_area = ai_detection.get_tracking_data() # Gets necessary data from the AI camera

        distance_in_cm = get_distance() # Gets distance to closest obstacle from ultrasonic sensor    

        if obstacle or distance_in_cm <= safe_distance_in_cm: # If either the AI camera or the ultrasonic sensor detects an obstacle:
            print_and_log("Trying to avoid an obstacle...")
            forward()
            avoid_obstacle()
            continue
            
        if person_area is None:
            print_and_log("No person detected, waiting...")
            forward()
            stop()
            continue
        
        print_and_log(f"Person takes up {person_area:.2f} of the total frame size")

        if person_area < target_minimum_area:

            print_and_log("Person is too far away, trying to move forward...")

            forward()

            if direction == "centered":

                if abs(angle - 90) > max_angle_offset:

                    if angle < 90:
                        turn_right(angle)
                    
                    else:
                        turn_left(angle)
                    
                    continue
                
                else:
                    forward()
            
            elif direction in ("limit reached (left)", "limit reached (right)"):

                if angle < 90:
                    turn_right(angle)
                    
                else:
                    turn_left(angle)

                continue

        elif person_area > target_maximum_area:
            print_and_log("Person is too close, moving backwards...")
            forward()
            backward()

        else:
            print_and_log("Distance is OK, stopping...")
            stop()

        time.sleep(follow_loop_update_time)

# --- Execution ---

if __name__ == "__main__":

    try:
        follow()

    except KeyboardInterrupt:
        stop()
    finally:
        # Disable motors and cleanup GPIO
        GPIO.output(EN_PIN1, GPIO.LOW)
        GPIO.output(EN_PIN2, GPIO.LOW)
        GPIO.cleanup()

