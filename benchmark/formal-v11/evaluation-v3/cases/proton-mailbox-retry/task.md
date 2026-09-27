## Title: Mailbox element list reloads at the wrong time and keeps showing stale content


### Description
The mailbox list starts a new fetch of its elements while operations that modify those items are still running, so it refreshes against a state the backend has not finished applying and placeholders or pre-change content stay on screen. When a fetch of the list fails, no further attempt follows and the list is left without data. When the server answers with a response it marks as stale, that response is accepted and its outdated items are displayed. In each of these cases the list also stops presenting itself as loading, so an incomplete or outdated view reads as a settled result.

## Requirements

- When an operation that modifies items in the list is in progress, the mailbox list must not issue a new fetch of its elements.

- A refresh that becomes due while such an operation is in progress must be held back and carried out once no such operation remains, rather than dropped.

- An operation must be counted as in progress from the moment its request is issued until that request settles.

- When several such operations overlap, the mailbox list must issue exactly one fetch once the last of them settles, rather than one fetch per operation.

- When a fetch of the element list fails, a retry becomes due `2 seconds` later. If an item-modifying operation is still in progress when the retry becomes due, hold it until all such operations settle.

- When an element list response carries a `Stale` value of `1`, the mailbox must not commit that response to the list.

- When an element list response carries a `Stale` value of `1`, a retry becomes due `1 second` later. The same rule for holding requests during item-modifying operations applies.

- While a fetch of the element list is owed but has not yet been issued, the list must present itself as loading and must keep showing its placeholders.

- The list must display its real contents only once a response arrives that neither failed nor carries a `Stale` value of `1`.

- The failure and Stale retry delays are fixed at 2000 ms and 1000 ms respectively, measured from detection, without backoff or jitter. A due retry may be issued by the normal React update/effect cycle. Do not add another retry delay after it becomes eligible, and do not bypass an operation that is still in progress.

- Before a Stale retry becomes due, do not issue an extra fetch or display the stale response. The public retryStale reducer clears the in-flight state when dispatched; it may be dispatched after the delay. The list must remain loading while a usable response is still owed.

- Moving elements to a folder (including move to trash through `useMoveToFolder`) counts as an operation that modifies items: dispatch `backendActionStarted` when its request is issued and `backendActionFinished` when it settles.

- Once the last in-progress operation settles, a held refresh whose retry delay has already elapsed (or which has no retry delay) must resume automatically in the normal UI update cycle. Issuing its request synchronously inside backendActionFinished is not required. Keep the loading state and placeholder rows until a usable response is committed.

## Interfaces

- Path: `applications/mail/src/app/logic/elements/elementsActions.ts`
- Name: `retryStale`
- Type: function
- Input: `payload: { queryParameters: any }`
- Output: `PayloadAction<{ queryParameters: any }>`
- Description: Action creator that reports a stale element list response, carrying the query parameters the next fetch is issued with.

- Path: `applications/mail/src/app/logic/elements/elementsActions.ts`
- Name: `backendActionStarted`
- Type: function
- Input: NA
- Output: `PayloadAction<void>`
- Description: Action creator that reports that an operation modifying items in the list has started, so list refreshes are held back while it runs.

- Path: `applications/mail/src/app/logic/elements/elementsActions.ts`
- Name: `backendActionFinished`
- Type: function
- Input: NA
- Output: `PayloadAction<void>`
- Description: Action creator that reports that an operation modifying items in the list has settled, so a held-back refresh may be carried out once none remains.

- Path: `applications/mail/src/app/logic/elements/elementsReducers.ts`
- Name: `retryStale`
- Type: function
- Input: `state: Draft<ElementsState>, action: PayloadAction<{ queryParameters: any }>`
- Output: `void`
- Description: Reducer that records a stale response as a fetch that is still owed, so the list stops treating the request as in flight and keeps showing its placeholders until a further fetch returns a usable result.

- Path: `applications/mail/src/app/logic/elements/elementsReducers.ts`
- Name: `backendActionStarted`
- Type: function
- Input: `state: Draft<ElementsState>`
- Output: `void`
- Description: Reducer that records one more operation modifying items in the list as in progress.

- Path: `applications/mail/src/app/logic/elements/elementsReducers.ts`
- Name: `backendActionFinished`
- Type: function
- Input: `state: Draft<ElementsState>`
- Output: `void`
- Description: Reducer that records one fewer operation modifying items in the list as in progress.

- Path: `applications/mail/src/app/logic/elements/elementsSelectors.ts`
- Name: `pendingActions`
- Type: function
- Input: `state: RootState`
- Output: `number`
- Description: Selector that reports how many operations modifying items in the list are still in progress.
