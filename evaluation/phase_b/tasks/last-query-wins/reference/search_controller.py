import threading


class SearchController:
    def __init__(self, render, debounce_seconds=0.01):
        self._render = render
        self._lock = threading.Lock()
        self._generation = 0

    def submit(self, query, fetch):
        with self._lock:
            self._generation += 1
            generation = self._generation

        def run():
            result = fetch(query)
            with self._lock:
                is_latest = generation == self._generation
            if is_latest:
                self._render(query, result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
