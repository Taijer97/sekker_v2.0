import os
import shutil
import threading
import time


DEFAULT_MAX_AGE_SECONDS = 3 * 24 * 60 * 60
TARGETS = ("dni_pdfs", "data_img")


def _delete_path(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    elif os.path.exists(path):
        os.remove(path)


def clean_old_generated_files(max_age_seconds: int = DEFAULT_MAX_AGE_SECONDS) -> dict:
    now = time.time()
    removed = []

    for target in TARGETS:
        if not os.path.exists(target):
            continue

        for name in os.listdir(target):
            path = os.path.join(target, name)
            try:
                modified_at = os.path.getmtime(path)
            except OSError:
                continue

            if now - modified_at >= max_age_seconds:
                _delete_path(path)
                removed.append(path)

    return {"removed": removed, "count": len(removed)}


def start_cleanup_scheduler(interval_seconds: int = DEFAULT_MAX_AGE_SECONDS) -> threading.Thread:
    def worker():
        while True:
            try:
                clean_old_generated_files(interval_seconds)
            except Exception as e:
                print(f"cleanup error: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread
