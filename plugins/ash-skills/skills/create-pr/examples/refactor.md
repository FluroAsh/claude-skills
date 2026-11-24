### [BOOK-430](https://example.atlassian.net/browse/BOOK-430)

The three booking forms (hotel, flight, car) each had their own copy of the guest details fields and validation. They now share one `GuestDetailsFields` component, so a change to guest details lands once. No behaviour change is intended.

### What changed

- **One guest details component** replaces the three copies. Each form passes the fields it needs; the car form still skips passport details.
- **One validation schema** for guest details, which the three forms extend with their own fields.

### 🔍 Worth a close look

- **The flight form's passport expiry rule,** which only that copy had: it must be valid for six months after the return date. It's now an option on the shared schema; check it's still on for flights and off elsewhere.

**How it's proven unchanged:** the three forms' existing specs pass without edits, and the shared component has its own spec for each form's field set.

<!--
Why this shape: a refactor's reviewer wants to know what stays the same and how that's shown, plus the one place where the copies had drifted apart. No impact table: there's no behaviour to compare.
-->
