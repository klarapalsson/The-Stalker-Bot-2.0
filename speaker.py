# tts_ctrlc_fixed.py
import pyttsx3
import threading
import queue
import time
import signal
import sys
import os

# --- Settings ---
speech_rate = 150
speech_volume = 1.0

# --- Internal state ---
_speech_queue = queue.Queue(maxsize=1)  # only keep last pending message
_worker_thread = None
_worker_lock = threading.Lock()
_worker_shutdown = threading.Event()

# Expose engine so main thread / signal handler can stop it
_engine_lock = threading.Lock()
_engine = None

def _tts_worker():
    global _engine
    engine = None
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", speech_rate)
        engine.setProperty("volume", speech_volume)

        # publish engine to main thread (protected)
        with _engine_lock:
            _engine = engine

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
                # swallow errors but keep running
                pass
            finally:
                try:
                    _speech_queue.task_done()
                except Exception:
                    pass

    finally:
        # cleanup: make sure engine is not referenced after stopping
        try:
            if engine is not None:
                engine.stop()
        except Exception:
            pass
        with _engine_lock:
            _engine = None

def _ensure_worker():
    global _worker_thread
    with _worker_lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_shutdown.clear()
            _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
            _worker_thread.start()

def say_async(message):
    """Queue message but keep only the latest pending one."""
    _ensure_worker()
    try:
        _speech_queue.put_nowait(message)
    except queue.Full:
        # drop previous pending and insert the new one
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        _speech_queue.put_nowait(message)

def stop_engine():
    """Call engine.stop() from main thread if worker's engine exists."""
    with _engine_lock:
        eng = _engine
    if eng is not None:
        try:
            # engine.stop() is thread-safe in practice for pyttsx3 and will break runAndWait()
            eng.stop()
        except Exception:
            pass

def stop_tts(wait=True, timeout=1.0):
    """Signal the worker to exit and try to join it."""
    _worker_shutdown.set()
    # put sentinel to wake worker
    try:
        _speech_queue.put_nowait(None)
    except queue.Full:
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        try:
            _speech_queue.put_nowait(None)
        except Exception:
            pass

    global _worker_thread
    if wait and _worker_thread is not None:
        _worker_thread.join(timeout=timeout)
        # clear thread ref if not alive
        if not _worker_thread.is_alive():
            _worker_thread = None

def _sigint_handler(signum, frame):
    """Handle Ctrl+C (SIGINT) — attempt graceful shutdown, then force exit if needed."""
    print("\nSIGINT received: stopping TTS...")
    try:
        # First try to interrupt any ongoing speech immediately
        stop_engine()
    except Exception:
        pass

    try:
        # Then tell worker to stop and wait briefly
        stop_tts(wait=True, timeout=1.0)
    except Exception:
        pass

    # If the worker is still alive after join attempt, force-exit
    with _worker_lock:
        still_alive = _worker_thread is not None and _worker_thread.is_alive()
    if still_alive:
        print("Worker did not exit quickly; forcing process exit.")
        # os._exit bypasses cleanup but ensures process ends
        os._exit(1)

    print("TTS stopped. Exiting.")
    sys.exit(0)

# Install SIGINT handler so Ctrl+C goes through our shutdown logic
signal.signal(signal.SIGINT, _sigint_handler)

# --- Example usage ---
if __name__ == "__main__":
    print("Running Ctrl+C-friendly TTS. Press Ctrl+C to stop.")
    try:
        i = 0
        while True:
            say_async(f"Message number {i}")
            i += 1
            # short sleep so Ctrl+C is responsive
            time.sleep(0.75)
    except KeyboardInterrupt:
        # Fallback in case signal handler didn't run for some reason
        print("\nKeyboardInterrupt caught in main loop; performing shutdown.")
        stop_engine()
        stop_tts()
        sys.exit(0)
