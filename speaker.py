import sys
import subprocess
import signal
import os
import time

# Determine platform-specific TTS command
if sys.platform == "darwin":
    TTS_CMD = ["say"]
elif sys.platform.startswith("linux"):
    if subprocess.call(["which", "espeak"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        TTS_CMD = ["espeak"]
    elif subprocess.call(["which", "spd-say"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        TTS_CMD = ["spd-say"]
    else:
        raise RuntimeError("No TTS backend found. Install espeak or spd-say.")
elif sys.platform.startswith("win"):
    TTS_CMD = ["powershell", "-NoProfile", "-Command",
               "Add-Type -AssemblyName System.speech;"
               "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
               "$s.Speak([Console]::In.ReadToEnd())"]
else:
    raise RuntimeError("Unsupported platform")

# Global reference to current speech process
current_proc = None

def say_latest(message: str):
    """
    Speak only the latest message:
    - Interrupt any currently speaking message
    - Start speaking the new message
    """
    global current_proc

    # Kill previous speech if running
    if current_proc is not None:
        try:
            current_proc.terminate()
        except Exception:
            pass
        current_proc = None

    if sys.platform.startswith("win"):
        # Windows: pass text via stdin to PowerShell
        current_proc = subprocess.Popen(
            TTS_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False
        )
        try:
            current_proc.stdin.write(message.encode("utf-8"))
            current_proc.stdin.close()
        except Exception:
            pass
    else:
        # macOS / Linux: pass text as argument
        current_proc = subprocess.Popen(
            TTS_CMD + [message],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

def stop_tts():
    """Stop any ongoing speech immediately"""
    global current_proc
    if current_proc is not None:
        try:
            current_proc.terminate()
        except Exception:
            pass
        current_proc = None

def _signal_handler(sig, frame):
    """Ctrl+C handler to stop TTS and exit immediately"""
    print("\nCtrl+C pressed: stopping TTS and exiting.")
    stop_tts()
    os._exit(0)  # force exit to ensure no hanging

# Install signal handler for Ctrl+C
signal.signal(signal.SIGINT, _signal_handler)

# --- Example usage ---
if __name__ == "__main__":
    print("Press Ctrl+C to stop. Speaking messages every second...")
    i = 0
    while True:
        say_latest(f"Message number {i}")
        i += 1
        time.sleep(1)
