# speaker.py — Graceful, Fast, and Ctrl+C VIP Shutdown

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
_ctrlc_vip = threading.Event()  # <--- VIP pass for Ctrl+C

_engine_lock = threading.Lock()
_engine = None


def _tts_worker():
    """Background thread for speaking messages."""
    global _engine
    engine = None

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", speech_rate)
        engine.setProperty("volume", speech_volume)

        with _engine_lock:
            _engine = engine

        while not _worker_shutdown.is_set():
            # If VIP shutdown requested, stop taking new messages
            if _ctrlc_vip.is_set():
                break

            try:
                message = _speech_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if message is None:
                break  # normal graceful stop

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

            # After speaking a message, check again if Ctrl+C arrived
            if _ctrlc_vip.is_set():
                break

    finally:
        # cleanup engine
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
            _ctrlc_vip.clear()
            _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
            _worker_thread.start()


def say_async(message):
    """Queue message but keep only the most recent one."""
    if _ctrlc_vip.is_set():
        # Ctrl+C in progress → ignore new speech entirely
        return

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
    """Immediately stop current speech."""
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
    - graceful=True → finish current phrase, no new ones.
    - graceful=False → interrupt immediately.
    """
    if graceful:
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
    else:
        stop_engine()
        _worker_shutdown.set()
        _ctrlc_vip.set()

    global _worker_thread
    if _worker_thread is not None:
        _worker_thread.join(timeout=timeout)
        if not _worker_thread.is_alive():
            _worker_thread = None


def _sigint_handler(signum, frame):
    """VIP Ctrl+C handler — ensures shutdown can always queue."""
    print("\nSIGINT received: finishing current phrase, then shutting down...")

    # Give Ctrl+C a VIP bypass — no new messages after this
    _ctrlc_vip.set()
    _worker_shutdown.set()

    try:
        stop_tts(graceful=True, timeout=2.5)
    except Exception:
        pass

    print("Speech finished. Exiting cleanly.")
    sys.exit(0)


# --- Signal setup ---
signal.signal(signal.SIGINT, _sigint_handler)


# --- Example test ---
if __name__ == "__main__":
    print("TTS running. Press Ctrl+C to test graceful VIP shutdown.")
    try:
        i = 0
        while True:
            say_async(f"This is message number {i}")
            i += 1
            time.sleep(0.7)
    except KeyboardInterrupt:
        stop_tts(graceful=True)
        print("\nExited via KeyboardInterrupt fallback.")
