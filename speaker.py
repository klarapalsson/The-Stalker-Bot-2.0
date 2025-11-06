# tts_subprocess_latest.py
import sys
import subprocess
import threading
import time
import signal
import shutil
import os

# choose backends per platform
def _select_backend():
    plat = sys.platform
    if plat == "darwin":
        return ("say",)  # macOS built-in
    elif plat.startswith("linux"):
        # prefer espeak (fast), else spd-say (PulseAudio), else None
        if shutil.which("espeak"):
            return ("espeak",)
        if shutil.which("spd-say"):
            return ("spd-say",)
        return (None,)
    elif plat.startswith("win"):
        # we'll call PowerShell to use .NET System.Speech
        return ("powershell",)
    else:
        return (None,)

_BACKEND = _select_backend()[0]

if _BACKEND is None:
    raise RuntimeError("No TTS backend found on this system (need 'espeak' or 'spd-say' on Linux, 'say' on macOS, or PowerShell on Windows).")

class LatestTTS:
    def __init__(self):
        self._lock = threading.Lock()
        self._proc = None  # currently running subprocess.Popen
        self._stopping = False

        # install SIGINT handler so Ctrl+C triggers cleanup
        signal.signal(signal.SIGINT, self._sigint_handler)

    def _start_process(self, message: str):
        """Start platform-specific subprocess to speak message. Returns Popen."""
        if sys.platform == "darwin":
            # macOS 'say' speaks and exits
            return subprocess.Popen(["say", message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("linux"):
            # either espeak or spd-say
            if shutil.which("espeak"):
                # espeak: keep it simple, pass text via -s for speed if you want
                return subprocess.Popen(["espeak", message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                return subprocess.Popen(["spd-say", message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform.startswith("win"):
            # PowerShell invocation: use System.Speech.Synthesis.SpeechSynthesizer
            # -NoProfile to avoid profile delays; -Command with a single expression
            ps_script = (f"Add-Type -AssemblyName System.speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                         f"$s.Speak([Console]::In.ReadToEnd())")
            # We'll pass the message on stdin to avoid quoting issues
            return subprocess.Popen(
                ["powershell", "-NoProfile", "-Command", ps_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )
        else:
            raise RuntimeError("Unsupported platform for subprocess TTS")

    def say_latest(self, message: str):
        """Speak only the latest message: kill previous process (if any) and start this one."""
        with self._lock:
            if self._stopping:
                return
            # kill existing process if running
            if self._proc is not None:
                try:
                    # try graceful terminate then kill if still alive after timeout
                    self._proc.terminate()
                    # small wait
                    try:
                        self._proc.wait(timeout=0.25)
                    except subprocess.TimeoutExpired:
                        self._proc.kill()
                except Exception:
                    pass
                finally:
                    self._proc = None

            # start new process
            proc = self._start_process(message)
            # if on Windows we need to send message via stdin
            if sys.platform.startswith("win"):
                try:
                    # encode to utf-8 and close stdin so powershell receives EOF and speaks
                    proc.stdin.write(message.encode("utf-8"))
                    proc.stdin.close()
                except Exception:
                    pass
            self._proc = proc

    def stop(self):
        """Stop any running speech and prevent new ones."""
        with self._lock:
            self._stopping = True
            if self._proc is not None:
                try:
                    self._proc.terminate()
                    try:
                        self._proc.wait(timeout=0.25)
                    except subprocess.TimeoutExpired:
                        self._proc.kill()
                except Exception:
                    pass
                finally:
                    self._proc = None

    def _sigint_handler(self, signum, frame):
        # called on Ctrl+C
        print("\nSIGINT received: stopping TTS and exiting.")
        self.stop()
        # give short time then exit
        time.sleep(0.05)
        # use os._exit to ensure termination if something else blocks
        os._exit(0)

# --- Example usage ---
if __name__ == "__main__":
    tts = LatestTTS()
    print(f"Using backend: {_BACKEND}. Press Ctrl+C to stop.")
    try:
        i = 0
        while True:
            # demonstrate only-latest: new messages arrive frequently
            tts.say_latest(f"Message number {i}")
            i += 1
            time.sleep(0.7)
    except KeyboardInterrupt:
        print("KeyboardInterrupt: shutting down...")
        tts.stop()
        sys.exit(0)
