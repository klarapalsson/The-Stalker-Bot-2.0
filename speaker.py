
# --- Imports ---

import pyttsx3
import threading
import time

# --- Definitions ---

speech_rate = 150
speech_volume = 1.0

# ---- Speech function ---

def say_asynchronously(message):

    """
    Makes the robot say a message asynchronously.

    Arguments:
        None
    
    Returns:
        None
    
    """

    def _speak():

        """
        Makes the text-to-speech engine read out the message.

        Arguments:
            None
        
        Returns:
            None

        """

        engine = pyttsx3.init()
        engine.setProperty("rate", speech_rate)
        engine.setProperty("volume", speech_volume)
        engine.say(message)
        engine.runAndWait()

    threading.Thread(target = _speak, daemon = True).start()

# --- Test ---

if __name__ == "__main__":

    print("Running speaker test...")

    say_asynchronously("The speaker is working, twin.")

    time.sleep(5)