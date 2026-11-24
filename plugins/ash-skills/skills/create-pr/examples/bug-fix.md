### [BOOK-412](https://example.atlassian.net/browse/BOOK-412)

The cancellation banner on the booking summary said "Fees may apply" even when the booking was free to cancel. It now shows only when a cancellation fee applies, matching the confirmation email.

- **The banner reads the booking's fee, not the room type's default.** That's the whole change, in the summary page's banner component.

<!--
Why this shape: a fix this small needs a sentence of problem and a sentence of result. No Worth a close look, no tables, no Decisions. Testing goes in the template's testing section in one line.
-->
