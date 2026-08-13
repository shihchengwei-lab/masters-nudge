import threading


class RefreshController:
    def __init__(self, render, debounce_seconds=0.08):
        self._render = render
        self._lock = threading.Lock()
        self._generation = 0

    def refresh(self, fetch):
        with self._lock:
            self._generation += 1
            generation = self._generation

        def run():
            result = fetch()
            with self._lock:
                if generation == self._generation:
                    self._render(result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
