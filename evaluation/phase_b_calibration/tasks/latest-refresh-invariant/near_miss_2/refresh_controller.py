import threading


class RefreshController:
    def __init__(self, render, debounce_seconds=0.08):
        self._render = render
        self._lock = threading.Lock()

    def refresh(self, fetch):
        def run():
            result = fetch()
            with self._lock:
                self._render(result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
