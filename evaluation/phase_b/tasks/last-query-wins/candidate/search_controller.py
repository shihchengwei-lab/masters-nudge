import threading
import time


class SearchController:
    def __init__(self, render, debounce_seconds=0.08):
        self._render = render
        self._debounce_seconds = debounce_seconds

    def submit(self, query, fetch):
        def run():
            time.sleep(self._debounce_seconds)
            result = fetch(query)
            self._render(query, result)

        thread = threading.Thread(target=run)
        thread.start()
        return thread
