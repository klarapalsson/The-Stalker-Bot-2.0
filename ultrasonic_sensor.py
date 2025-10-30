
# --- Imports ---

from gpiozero import DistanceSensor
import time

# --- Definitions ---

echo_pin = 27
trigger_pin = 25

max_distance_in_m = 2
max_distance_in_cm = max_distance_in_m * 100

distance_loop_update_time = 0.1
timeout = 0.3  # How long to trust the last valid reading

spike_threshold = 20  # Any sudden jump larger than this is ignored

# --- Sensor setup ---

ultrasonic_sensor = DistanceSensor(echo = echo_pin, trigger = trigger_pin, max_distance = max_distance_in_m)

print("\nUltrasonic sensor initialized.")

# --- Internal state ---

_last_valid = max_distance_in_cm
_last_time = time.time()

# --- Main function ---

def get_distance():

    """
    Gets the distance from the ultrasonic sensor.

    Arguments:
        None
    
    Returns:
        float: The filtered distance in cm.

    """

    global _last_valid, _last_time

    raw = ultrasonic_sensor.distance * 100
    now = time.time()

    # Accept if difference is reasonable
    if abs(raw - _last_valid) <= spike_threshold:
        _last_valid = raw
        _last_time = now
        return round(_last_valid, 1)

    # Otherwise check if last valid reading is recent enough
    if now - _last_time <= timeout:
        return round(_last_valid, 1)

    # If spike persists too long, accept new reading
    _last_valid = raw
    _last_time = now
    return round(_last_valid, 1)

# --- Test ---

if __name__ == "__main__":

    try:
        print("\nStarting ultrasonic sensor test.\n")

        while True:
            distance = get_distance()
            print(f"Filtered distance: {distance:.1f} cm", end = "\r")
            time.sleep(distance_loop_update_time)

    except KeyboardInterrupt:
        print("\nStopped.")
