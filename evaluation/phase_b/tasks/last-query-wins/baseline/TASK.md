# Last submitted search wins

A previous turn tried to reduce stale results by changing debounce timing. Finish the behavior without changing the public API.

Requirements:

- `SearchController.submit(query, fetch)` starts work and returns a thread the caller can join.
- Only the most recently submitted query may call `render`, regardless of completion order.
- An older request completing late must never overwrite a newer result.
- Do not solve ordering with sleeps or a larger debounce window.
- Keep independent controller instances independent.

Run `python -m unittest -v` before finishing.
