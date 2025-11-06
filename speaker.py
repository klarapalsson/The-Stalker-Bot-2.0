# tts_last_only_interruptible.py
import pyttsx3
import threading
import queue
import time
import sys

speech_rate = 150
speech_volume = 1.0

_speech_queue = queue.Queue(maxsize=1)
_worker_thread = None
_worker_lock = threading.Lock()
_worker_shutdown = threading.Event()

def _tts_worker():
    engine = pyttsx3.init()
    engine.setProperty("rate", speech_rate)
    engine.setProperty("volume", speech_volume)

    while not _worker_shutdown.is_set():
        try:
            message = _speech_queue.get(timeout=0.3)
        except queue.Empty:
            continue

        if message is None:
            break
        try:
            engine.say(message)
            engine.runAndWait()
        except Exception:
            pass
        finally:
            try:
                _speech_queue.task_done()
            except Exception:
                pass

    try:
        engine.stop()
    except Exception:
        pass

def _ensure_worker():
    global _worker_thread
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_shutdown.clear()
            _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
            _worker_thread.start()

def say_async(message):
    _ensure_worker()
    try:
        _speech_queue.put_nowait(message)
    except queue.Full:
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        _speech_queue.put_nowait(message)

def stop_tts():
    """Signal worker to exit and stop any ongoing speech."""
    _worker_shutdown.set()
    try:
        _speech_queue.put_nowait(None)
    except queue.Full:
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        _speech_queue.put_nowait(None)

# --- Test ---
if __name__ == "__main__":
    print("Running Ctrl+C-friendly speaker test...")
    try:
        i = 0
        while True:
            say_async(f"This is message number {i}.")
            time.sleep(2)
            i += 1
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected. Stopping TTS...")
        stop_tts()
        # Give a brief moment to allow background cleanup
        time.sleep(0.5)
        print("TTS stopped. Exiting.")
        sys.exit(0)
