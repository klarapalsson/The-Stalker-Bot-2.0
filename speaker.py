# fixed_tts.py
import pyttsx3
import threading
import queue
import time

# --- Settings ---
speech_rate = 150
speech_volume = 1.0

# --- Internal queue and worker thread ---
_speech_queue = queue.Queue()
_worker_thread = None

def _tts_worker():
    """Runs in a dedicated thread: single engine, reads messages from the queue."""
    engine = pyttsx3.init()
    engine.setProperty("rate", speech_rate)
    engine.setProperty("volume", speech_volume)

    while True:
        message = _speech_queue.get()
        try:
            if message is None:
                # Sentinel to shut down the worker
                break
            engine.say(message)
            engine.runAndWait()
        except Exception:
            # You can log the exception here if you want
            pass
        finally:
            _speech_queue.task_done()

def _ensure_worker():
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
        _worker_thread.start()

# --- Public API ---
def say_async(message):
    """
    Queue a message for speaking asynchronously.
    Non-blocking for the caller.
    """
    _ensure_worker()
    _speech_queue.put(message)

def stop_tts(wait=True, timeout=None):
    """
    Stop the worker thread cleanly.
    If wait is True, will join the worker (optional timeout).
    """
    # Put sentinel None to instruct worker to exit
    _speech_queue.put(None)
    if wait and _worker_thread is not None:
        _worker_thread.join(timeout=timeout)

# --- Test ---
if __name__ == "__main__":
    print("Running speaker test...")
    say_async("The speaker is working, twin.")
    # we keep the main thread alive long enough to hear it
    time.sleep(5)

    # optional: clean shutdown
    stop_tts(wait=False)
