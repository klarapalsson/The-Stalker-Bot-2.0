# speaker.py — Graceful but Fast Shutdown TTS Controller

import pyttsx3
import threading
import queue
import time
import signal
import sys

# --- Settings ---
speech_rate = 150
speech_volume = 1.0

# --- Internal state ---
_speech_queue = queue.Queue(maxsize=1)  # only keep latest message
_worker_thread = None
_worker_lock = threading.Lock()
_worker_shutdown = threading.Event()

# Expose engine so signal handler can stop it
_engine_lock = threading.Lock()
_engine = None


def _tts_worker():
    """Background thread that handles speaking messages."""
    global _engine
    engine = None

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", speech_rate)
        engine.setProperty("volume", speech_volume)

        with _engine_lock:
            _engine = engine

        while not _worker_shutdown.is_set():
            try:
                message = _speech_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if message is None:
                # graceful shutdown signal
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

    finally:
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
    """Queue message but keep only the most recent one."""
    _ensure_worker()
    try:
        _speech_queue.put_nowait(message)
    except queue.Full:
        # drop the old pending one and replace it
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        _speech_queue.put_nowait(message)


def stop_engine():
    """Stop any currently playing speech immediately."""
    with _engine_lock:
        eng = _engine
    if eng is not None:
        try:
            eng.stop()
        except Exception:
            pass


def stop_tts(graceful=True, timeout=2.0):
    """
    Stop the TTS worker.
    If graceful=True → finish current speech but don't start new ones.
    If graceful=False → interrupt immediately.
    """
    if graceful:
        _worker_shutdown.set()
        try:
            _speech_queue.put_nowait(None)  # sentinel for clean stop
        except queue.Full:
            try:
                _speech_queue.get_nowait()
                _speech_queue.task_done()
            except queue.Empty:
                pass
            _speech_queue.put_nowait(None)
    else:
        stop_engine()
        _worker_shutdown.set()
        try:
            _speech_queue.queue.clear()
        except Exception:
            pass

    global _worker_thread
    if _worker_thread is not None:
        _worker_thread.join(timeout=timeout)
        if not _worker_thread.is_alive():
            _worker_thread = None


def _sigint_handler(signum, frame):
    """Handle Ctrl+C (SIGINT) with graceful speech finish."""
    print("\nSIGINT received: finishing current phrase, then exiting...")

    try:
        stop_tts(graceful=True, timeout=2.5)
    except Exception:
        pass

    print("Speech finished. Shutting down cleanly.")
    sys.exit(0)


# --- Signal Setup ---
signal.signal(signal.SIGINT, _sigint_handler)


# --- Example (manual testing) ---
if __name__ == "__main__":
    print("TTS started. Press Ctrl+C to exit gracefully.")
    try:
        i = 0
        while True:
            say_async(f"Message number {i}")
            i += 1
            time.sleep(0.7)
    except KeyboardInterrupt:
        # backup safety if handler didn't fire
        stop_tts(graceful=True)
        print("\nExited via KeyboardInterrupt.")
