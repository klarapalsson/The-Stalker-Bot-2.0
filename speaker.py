import sys
import subprocess
import signal
import threading

# --- Platform-specific setup ---
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
    TTS_CMD = [
        "powershell", "-NoProfile", "-Command",
        "Add-Type -AssemblyName System.speech;"
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$s.Speak([Console]::In.ReadToEnd())"
    ]
else:
    raise RuntimeError("Unsupported platform")

# --- Globals ---
current_proc = None
stop_event = threading.Event()
lock = threading.Lock()

# --- Core functions ---
def say_latest(message: str):
    """Speak the latest message, cancelling any in progress."""
    global current_proc

    with lock:
        # Stop any ongoing speech
        if current_proc is not None:
            try:
                current_proc.terminate()
            except Exception:
                pass
            current_proc = None

        # Don’t start if shutting down
        if stop_event.is_set():
            return

        if sys.platform.startswith("win"):
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
            current_proc = subprocess.Popen(
                TTS_CMD + [message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

def stop_tts():
    """Stop any ongoing speech immediately."""
    global current_proc
    with lock:
        if current_proc is not None:
            try:
                current_proc.terminate()
            except Exception:
                pass
            current_proc = None

def _signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\nCtrl+C pressed: stopping TTS and exiting cleanly.")
    stop_event.set()
    stop_tts()

# Install signal handler only if running as main (not when imported)
signal.signal(signal.SIGINT, _signal_handler)
