> [!NOTE]
> **Stack:** part 1 of 3 for [BOOK-500](https://example.atlassian.net/browse/BOOK-500). Next: #612 (use it in the bookings list), then #613 (filters).

### [BOOK-500](https://example.atlassian.net/browse/BOOK-500)

Adds the paged bookings query to the API client, for the bookings list's new filters. Nothing calls it yet, so this PR changes no behaviour.

### What changed

- **`listBookings` takes `page`, `pageSize` and `status`,** and returns the page with a total. It replaces the unpaged `getAllBookings`, which stays until #613 removes its last caller.
- **The response is validated** against the schema below, so an unexpected shape fails loudly in development instead of rendering blanks.

### 🔌 Contract

`GET /v2/bookings`

| Param | Type | Notes |
| --- | --- | --- |
| `page` | integer, from 1 | Defaults to 1 |
| `pageSize` | integer, 1–100 | Defaults to 25 |
| `status` | `upcoming` \| `past` \| `cancelled` | Optional; all when omitted |

The response is `{ items, total, page }`. The endpoint shipped in the bookings service last sprint ([BOOK-221](https://example.atlassian.net/browse/BOOK-221)); this PR doesn't change it.

<!--
Why this shape: the stack note goes first so a reviewer knows where this sits. The contract table lets a backend engineer check it against the service without reading the client code.
-->
