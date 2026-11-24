### [BOOK-470](https://example.atlassian.net/browse/BOOK-470)

Upgrades the date library from v3 to v4 across the app, for its time zone fixes. One behaviour changes; everything else is a version bump.

> [!NOTE]
> **One visible difference:** times shown in a hotel's local zone now follow daylight saving changes on the day itself. v3 applied the change from the next day.

### What changed

- **Date library v3 → v4** in the web app and the shared UI package.
- **`formatRange` takes an options object** instead of positional arguments; its four call sites are updated.

**Held back:** the date picker stays on its own v3 copy until its maintainers ship v4 support ([BOOK-471](https://example.atlassian.net/browse/BOOK-471)).

<!--
Why this shape: a reviewer needs the behaviour differences and what was held back, not the changelog. A pure security bump is even shorter: the version, the advisories it fixes, and "no API changes".
-->
