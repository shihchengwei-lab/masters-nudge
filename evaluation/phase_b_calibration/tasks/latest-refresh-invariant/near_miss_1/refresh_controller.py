import threading


_LOCK = threading.Lock()
_GENERATION = 0


class RefreshController:
    def __init__(self, render, debounce_seconds=0.08):
        self._render = render

    def refresh(self, fetch):
        global _GENERATION
        with _LOCK:
            _GENERATION += 1
            generation = _GENERATION

        def run():
            result = fetch()
            with _LOCK:
                if generation == _GENERATION:
                    self._render(result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
