
# --- Imports ---

import pyttsx3
import threading
import subprocess

# --- Definitions ---

audio_output_device = "alsa_output.usb-AudioQuest_DragonFly_Red-00.analog-stereo"
speech_rate = 170
speech_volume = 1.0

# --- Audio routing setup ---

def set_audio_output():

    """
    Sets the system default audio sink to the configured DragonFly Red DAC. If it fails, prints a warning and continues with system default.

    Arguments:
        None
    
    Returns:
        None

    """

    try:
        subprocess.run(["pactl", "set-default-sink", audio_output_device], check = True)
        print(f"Audio output set to: {audio_output_device}")

    except subprocess.CalledProcessError:
        print(f"Warning: Could not set audio output to {audio_output_device}. Using system default.")

    except FileNotFoundError:
        print("pactl command not found. Install pulseaudio or pipewire-pulse.")

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

# --- Speaker test ---

if __name__ == "__main__":

    print("Running speaker test...")

    set_audio_output()

    subprocess.run(["speaker-test", "-c2", "-t", "sine", "-l", "1"], timeout = 3)

    say_asynchronously("The speaker is working, twin.")