import threading


class RefreshController:
    def __init__(self, render, debounce_seconds=0.08):
        self._render = render
        self._lock = threading.Lock()
        self._previous_cancel = None

    def refresh(self, fetch):
        cancel = threading.Event()
        with self._lock:
            if self._previous_cancel is not None:
                self._previous_cancel.set()
            self._previous_cancel = cancel

        def run():
            result = fetch()
            if not cancel.is_set():
                self._render(result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
