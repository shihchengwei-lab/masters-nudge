import threading
import time


class RefreshController:
    def __init__(self, render, debounce_seconds=0.01):
        self._render = render
        self._debounce_seconds = debounce_seconds

    def refresh(self, fetch):
        def run():
            time.sleep(self._debounce_seconds)
            self._render(fetch())

        thread = threading.Thread(target=run)
        thread.start()
        return thread
