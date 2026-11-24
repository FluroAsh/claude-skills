# Example descriptions

Fictional PRs for a made-up booking app, one per common PR type. Read the one closest to the PR you're describing, and take its shape, not its wording. Each shows the description section only. The repo's PR template is the base: its other headings (screenshots, dependencies, testing, checklist) still apply around these, and screenshots go in its screenshots section.

| File | PR type | What it shows |
| --- | --- | --- |
| `bug-fix.md` | Small fix | A two-line description is enough; no sections, but before/after screenshots |
| `feature-flagged.md` | User-facing feature behind a flag | Flag and rollout callout, behaviour bullets, Worth a close look, screenshots |
| `behaviour-change.md` | Change others rely on (analytics, events, permissions) | Callout up top, a visible before/after table, rationale collapsed |
| `refactor.md` | No intended behaviour change | Saying what stays the same and how that's proven |
| `dependency-upgrade.md` | Upgrade or security bump | The one behaviour difference, and what was held back |
| `ci-tooling.md` | CI, build or dev tooling | What changes for developers, how it was checked, how to roll back |
| `api-contract.md` | SDK, API client or contract, often stacked | Stack note, a contract table, written so a backend reviewer can follow |
| `cleanup.md` | Removing a flag, dead code or a legacy path | Why it's safe now, and what to check before merging |
