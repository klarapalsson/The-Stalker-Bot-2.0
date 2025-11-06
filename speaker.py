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

def stop_tts(wait=True, t_
