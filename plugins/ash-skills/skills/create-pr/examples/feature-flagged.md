### [BOOK-388](https://example.atlassian.net/browse/BOOK-388)

Guests can now split a booking's payment across two cards at checkout, behind the `split_payment` flag.

> [!NOTE]
> **Flag:** `split_payment`, off in production and on in the staging environments. With it off, checkout is unchanged.

### What changed

- **Checkout offers "Pay with two cards"** under the card form. The guest enters an amount for the first card, and the second card covers the rest.
- **The payment step charges both cards, or neither.** If the second charge fails, the first is refunded and the guest sees which card failed.
- **The receipt lists both cards** with the amount charged to each.

### 🔍 Worth a close look

- **The refund when the second charge fails,** in the payment step. Check it also runs when the guest closes the tab between the two charges; the server retries it from the pending-payment record.
- **Rounding.** The two amounts must add up to the total to the cent; the split uses the currency's minor units, not floats.

<details>
<summary>Decisions and follow-ups</summary>

| Decision | Why |
| --- | --- |
| Two cards at most | Covers the support requests we've had; more needs a different layout. |
| Charge the larger amount first | A failure on the larger charge is the likelier one, and refunds nothing. |

- [BOOK-401](https://example.atlassian.net/browse/BOOK-401): Saved cards in the split form.

</details>

<!--
Why this shape: the flag is the first thing a reviewer and QA need, so it's a callout. Screenshots go in the template's screenshots section, flag on and off. Decisions are collapsed because they're reasoning, not things to test.
-->
