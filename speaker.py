# speaker.py
import sys
import subprocess
import signal
import os

current_proc = None

# Detect platform TTS command
if sys.platform == "darwin":
    TTS_CMD = ["say"]
elif sys.platform.startswith("linux"):
    if subprocess.call(["which", "espeak"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        TTS_CMD = ["espeak"]
    elif subprocess.call(["which", "spd-say"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        TTS_CMD = ["spd-say"]
    else:
        raise RuntimeError("No TTS backend found")
elif sys.platform.startswith("win"):
    TTS_CMD = ["powershell", "-NoProfile", "-Command",
               "Add-Type -AssemblyName System.speech;"
               "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;"
               "$s.Speak([Console]::In.ReadToEnd())"]
else:
    raise RuntimeError("Unsupported platform")

def say_async(message):
    """Speak message asynchronously, always cancelling previous speech"""
    global current_proc

    # Kill previous speech if any
    if current_proc is not None:
        try:
            current_proc.terminate()
        except Exception:
            pass
        current_proc = None

    # Start new speech
    if sys.platform.startswith("win"):
        current_proc = subprocess.Popen(TTS_CMD, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            current_proc.stdin.write(message.encode("utf-8"))
            current_proc.stdin.close()
        except Exception:
            pass
    else:
        current_proc = subprocess.Popen(TTS_CMD + [message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop():
    """Stop any ongoing speech immediately"""
    global current_proc
    if current_proc is not None:
        try:
            current_proc.terminate()
        except Exception:
            pass
        current_proc = None

# Ctrl+C handler to ensure TTS stops
def _signal_handler(sig, frame):
    stop()
    os._exit(0)

signal.signal(signal.SIGINT, _signal_handler)
