# last_only_tts.py
import pyttsx3
import threading
import queue
import time

# --- Settings ---
speech_rate = 150
speech_volume = 1.0

# --- Internal queue and worker thread (queue holds at most one pending message) ---
_speech_queue = queue.Queue(maxsize=1)
_worker_thread = None
_worker_lock = threading.Lock()
_worker_shutdown = threading.Event()

def _tts_worker():
    """Dedicated TTS thread: single engine, consumes messages from _speech_queue."""
    engine = pyttsx3.init()
    engine.setProperty("rate", speech_rate)
    engine.setProperty("volume", speech_volume)

    while not _worker_shutdown.is_set():
        try:
            # wait for a message; timeout so we can check shutdown periodically
            message = _speech_queue.get(timeout=0.3)
        except queue.Empty:
            continue

        try:
            if message is None:
                # sentinel -> exit
                break
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            # optionally log e
            pass
        finally:
            # mark done for the message we processed
            try:
                _speech_queue.task_done()
            except Exception:
                pass

def _ensure_worker():
    global _worker_thread
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_shutdown.clear()
            _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
            _worker_thread.start()

# --- Public API ---
def say_async(message):
    """
    Queue a message for speaking asynchronously, but ensure only the latest pending
    message is kept. If a message is already waiting in the queue it will be replaced.
    Non-blocking for the caller.
    """
    _ensure_worker()

    try:
        _speech_queue.put_nowait(message)
    except queue.Full:
        # queue already has one pending message: drop it and insert the new one
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            # race: someone else consumed it — fine
            pass
        # now there's room
        _speech_queue.put_nowait(message)

def stop_tts(wait=True, timeout=None):
    """
    Stop the worker thread cleanly. If wait is True, will join the worker (optional timeout).
    """
    with _worker_lock:
        _worker_shutdown.set()
        # put a sentinel to unblock queue.get() if waiting
        try:
            _speech_queue.put_nowait(None)
        except queue.Full:
            # if full, replace existing pending with sentinel
            try:
                _speech_queue.get_nowait()
                _speech_queue.task_done()
            except queue.Empty:
                pass
            _speech_queue.put_nowait(None)

        global _worker_thread
        if wait and _worker_thread is not None:
            _worker_thread.join(timeout=timeout)
            _worker_thread = None

# --- Test ---
if __name__ == "__main__":
    print("Running last-only speaker test...")
    say_async("First message - should be replaced.")
    time.sleep(0.2)
    say_async("Second message - will replace first.")
    time.sleep(0.2)
    say_async("Third message - final, only this should be read next.")
    # keep alive long enough to hear the result
    time.sleep(5)
    stop_tts()
