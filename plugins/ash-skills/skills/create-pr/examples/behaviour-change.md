### [BOOK-455](https://example.atlassian.net/browse/BOOK-455)

The search page sent `search_performed` once per keystroke, so a single search counted several times. It now sends one event when results load, with the final query's filters.

> [!IMPORTANT]
> Search counts will drop from the day this ships, by roughly the average query length. Dashboards comparing across that date need a note.

### What changed

- **`search_performed` is sent once per results load,** not per keystroke. A refined search (new filters on the same page) sends another.
- **The event carries `result_count`,** so zero-result searches can be counted without a second event.

### 🔍 Worth a close look

- **When a load counts as a new search.** The search page debounces input and cancels stale requests; check a cancelled request sends nothing, and that the back button restoring cached results doesn't send a duplicate.

### 📊 Event impact

| Scenario | Before | After |
| --- | --- | --- |
| Type "paris" and wait | 5 events, one per letter | 1 event, `query_length: 5` |
| Change a filter on the results page | 1 event | 1 event |
| Search with no results | 1 event per keystroke, no way to tell | 1 event, `result_count: 0` |
| Back button to cached results | 1 event | No event |

<details>
<summary>Decisions and edge cases</summary>

| Decision | Why |
| --- | --- |
| Keep the event name | A rename would split every saved chart at this date anyway, with more work. |

- A search abandoned before results load sends nothing; that's now measured by the existing `search_started`.

</details>

<!--
Why this shape: other people rely on the data, so the callout states the effect on them in one sentence, straight after the summary. The table stays visible because QA tests from it.
-->
