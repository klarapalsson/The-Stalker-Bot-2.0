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

_engine_lock = threading.Lock()
_engine = None


def _tts_worker():
    global _engine
    engine = pyttsx3.init()
    engine.setProperty("rate", speech_rate)
    engine.setProperty("volume", speech_volume)

    with _engine_lock:
        _engine = engine

    try:
        while not _worker_shutdown.is_set():
            try:
                message = _speech_queue.get(timeout=0.3)
            except queue.Empty:
                continue

            if message is None:
                break

            if _worker_shutdown.is_set():
                break

            try:
                engine.say(message)
                engine.runAndWait()
            except Exception:
                pass
            finally:
                _speech_queue.task_done()

    finally:
        try:
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
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            pass
        _speech_queue.put_nowait(message)


def stop_engine():
    """Immediately stop pyttsx3 engine."""
    with _engine_lock:
        eng = _engine
    if eng is not None:
        try:
            eng.stop()
        except Exception:
            pass


def stop_tts(wait=True, timeout=1.0):
    """Signal the worker to exit and wait for it."""
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

    global _worker_thread
    if wait and _worker_thread is not None:
        _worker_thread.join(timeout=timeout)
        if not _worker_thread.is_alive():
            _worker_thread = None


def _sigint_handler(sig, frame):
    """Gracefully handle Ctrl+C."""
    print("\nSIGINT received: stopping TTS...")
    stop_engine()
    stop_tts(wait=True, timeout=1.0)
    print("TTS stopped. Exiting cleanly.")
    sys.exit(0)


# Install signal handler (only once)
signal.signal(signal.SIGINT, _sigint_handler)
