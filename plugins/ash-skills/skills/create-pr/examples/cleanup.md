### [BOOK-490](https://example.atlassian.net/browse/BOOK-490)

Removes the `new_checkout` flag and the legacy checkout it switched off. The new checkout has been on for every user for six weeks.

> [!IMPORTANT]
> Check the flag is still on in production before merging. Merging with it off would switch everyone to a checkout that no longer exists.

### What changed

- **Checkout always uses the new flow.** The flag check and the legacy checkout pages are gone.
- **The legacy checkout routes redirect** to the new one, so old bookmarks and emails still land somewhere.

Nothing else references the flag: a search of the repo for its key finds only the changelog.

<!--
Why this shape: a removal's risk is in timing, so the precondition is the callout. Say why it's safe now and what still points at the removed path.
-->
