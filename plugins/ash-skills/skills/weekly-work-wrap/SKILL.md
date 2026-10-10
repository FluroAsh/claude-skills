---
name: weekly-work-wrap
description: Review and wrap up the current week's work log — draft achievements, update statuses, collect reflections, and seed next week's goals.
---

End-of-week wrap-up for the weekly work log in the user's Obsidian vault.

Plugin config values below come from the user config; a blank value means "not configured".

## Configuration

- Vault: `${user_config.vault_name}`, rooted at `${user_config.vault_path}`
- Weekly logs: `${user_config.weekly_log_folder}/` (`{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}`, dated by the week's Monday
- Template note: `${user_config.weekly_log_template}`
- Tech Lead Review: company `${user_config.company_name}`, context notes `${user_config.review_context_files}` — no context notes means skip the review

## Environment

Resolved from the shell, not plugin config:

- Author: `git config user.name`, run inside the repo
- Jira: the `jira` CLI's config (`~/.config/.jira/.config.yml`) supplies `{JIRA_SERVER}` (`server`), `{PROJECT_KEY}` (`project.key`) and `{BOARD_ID}` (`board.id`); `jira me` is the signed-in user; REST calls use `$JIRA_API_TOKEN`
- Ticket status: read from Jira at runtime (`jira issue view {KEY} --raw`, `fields.status.statusCategory.key`: `new`, `indeterminate` or `done`). A ticket is _finished_ when its category is `done`, or its status says only release/deploy remains (e.g. "Pending Deploy", "Ready for Release")
- Repos: the repo in the current directory; for another repo, look beside it or ask where it lives
- GitHub: `gh`, signed in; skip PR lookups if it isn't available
- Sunsama: used only if its MCP tools are available

## Step 1 — Identify and read the current week's log

Calculate the Monday of the current week based on today's date.
Derive the file path from the weekly logs folder and file naming above.
Read the file using the Obsidian CLI. If the file does not exist, tell the user and stop — this skill requires an existing log with daily entries.

## Step 2 — Assess completeness

Scan the log and identify which sections are already filled in vs still containing placeholder/template text.
Report a brief status to the user:

- Which daily entries (Mon–Fri) have content
- Whether the ticket table exists
- Which wrap-up sections are incomplete (Achievements, Goals for Next Week, Brain Dump, AI-free Reflection)

If daily entries are mostly empty, warn the user that achievement drafts will be thin, and offer the gap-fill from Step 2a.

## Step 2a — Fill empty days from Sunsama and git (on request)

If any daily entries (Mon–Fri) are empty, placeholder-only, **or only partially filled**, ask the user whether they'd like to fill/cross-check them before continuing. If the Sunsama MCP isn't available, use git activity and the user's own input only, skipping the Sunsama pull in item 1.

Process days **one at a time, in order (Monday → Friday)** — do not batch-fetch the whole week and draft it all at once. For a day that already has manually-written content, still pull its Sunsama data and diff it against what's already in the log — don't skip the day outright just because it isn't empty. Only treat a day as "done" once its existing content has been checked against Sunsama for missed tickets/tasks. For each day (empty or partially filled):

1. If the Sunsama MCP is available, pull that day's calendar events and tasks from it (`sunsama://calendar/events/{date}` and `sunsama://tasks/{date}`).
2. Identify any ticket numbers referenced (Jira integration links on tasks, or ticket prefixes in titles).
3. For each ticket found, search the relevant repo's git log (the current repo, or one beside it) for commits on that date authored by the user (e.g. `git log --all --since="{date} 00:00" --until="{date+1} 00:00" --author="$(git config user.name)"`) to gather detail on what was actually built. PRs add outcome-level wording for what shipped: `gh pr list --author @me --state all --search "updated:>={date}"` (title and description summarise the work better than individual commits).
4. If a ticket/task has no matching commits, or its task/calendar entry has no notes and a generic title (e.g. just the ticket name with no further context), the source detail is too vague to draft from. Stop and ask the user to clarify what was actually done, rather than guessing or leaving a thin bullet — this also nudges them toward logging more detail in Sunsama going forward. Do this per-item, on the day it's found — don't collect questions across multiple days into one batch. This applies to non-ticket recurring support roles too (e.g. a release-support rotation) — if the entry doesn't say _why_ the user was involved (rostered duty vs. ad-hoc pull-in vs. something else), that's a context gap just like a vague ticket, and matters for Step 10's Tech Lead Review: a scheduled obligation reads very differently from an unplanned interruption. Ask rather than assume.
5. Check task/subtask completion state for milestones — e.g. a "Dev" subtask flipping to completed that day means dev work wrapped, not just "continued". Call out milestones like this explicitly rather than describing the day as ongoing/ambiguous progress.
6. Draft dot-point descriptions of what was completed/worked on for that day, grouped by ticket. Consolidate — don't transcribe every commit as its own bullet; group related commits/feature-branch changes into a small number of high-level bullets describing the overall outcome. **Aim for ~3 dot points per ticket/piece of work**, and don't bundle multiple distinct things into one bullet just to stay under that cap — split into separate bullets for each logical group of work, grouping only genuinely similar changes together.
7. Keep each bullet a high-level summary, not a change-list. Use commit messages to understand and group what happened, but write the bullet as a generic outcome statement (e.g. "Reworked auth session handling") rather than naming specific implementation details (e.g. which cookie, which header, which prop was removed). If a bullet reads like a parenthetical list of fixes, generalise it down to the underlying theme.
8. Exclude standing ceremonies — standup, planning, refinement, retro, and other recurring team ceremonies are too routine to log; only include notable one-off meetings (e.g. a specific stakeholder sync, an incident call, a workshop).
9. Write that day's entry into the log and show the user what was added before moving on to the next day.

## Step 3 — Update ticket statuses from Jira

For each ticket in the **This Weeks Tickets** table, check its current status in Jira using `jira issue view {KEY} --plain`.
If a ticket's status in the log differs from Jira, update the table to match Jira.
Report any status changes made.

## Step 4 — Update goal checkboxes

Cross-reference the **Goals for this week** and **Sprint Goals** checkboxes against:

1. The ticket statuses from Step 3 — mark a goal `[x]` if its ticket is in a finished status
2. The daily entries — if a non-ticket goal was clearly completed based on the notes, mark it `[x]`

Do not uncheck anything that is already checked.

## Step 5 — Draft Achievements

Analyse **all daily entries** (Monday through Friday) and draft three subsections:

### Delivery

- What was shipped, progressed, or unblocked this week
- Each bullet: `{what was done} — {why it mattered}`
- Group related work across days (e.g. if the same ticket appears Mon + Wed, combine into one bullet)
- Aim for 3–6 bullets

### Craft

- Technical decisions, root-cause analysis, patterns, tradeoffs — things that don't show up in ticket titles
- Focus on _how_ problems were solved, not _what_ was delivered
- Aim for 2–4 bullets

### Influence

- Cross-team coordination, alignment conversations, unblocking others, code review impact
- For code review impact, list the PRs the user reviewed this week: `gh search prs --reviewed-by @me --updated ">={week-start}"`. Name the author and what the review unblocked only if the PR or its comments say so — don't infer impact
- Name the people involved
- Aim for 2–5 bullets

Present the full draft to the user with options:

- **Looks good** — write as-is
- **Needs tweaks** — user provides corrections (accept their notes and revise before writing)

## Step 6 — Goals for Next Week

Identify carry-forward candidates (for seeding into next week's log — **do not write a "Goals for Next Week" section in the current week's log**):

1. Any unchecked items from **Goals for this week**
2. Any unchecked items from **Sprint Goals** that are still in scope
3. Any tickets in the table not yet in a finished status

Present these as suggested goals, allowing the user to confirm, remove, or add extras. Hold the final list for use in Step 9 only.

## Step 7 — Brain Dump

Ask the user:

> "Anything for the Brain Dump section? (observations, patterns, architectural thoughts — not a recap of achievements)"

Options:

- **Nothing this week** — remove the Brain Dump section entirely from the log
- **I'll type something** — accept their notes and write them in

## Step 8 — AI-free Reflection

Ask the user:

> "Anything for the AI-free Reflection? (What did you instinctively reach for AI on? What did you work through on your own?)"

Options:

- **Nothing this week** — remove the AI-free Reflection section entirely from the log
- **I'll type something** — accept their notes and write them in

## Step 9 — Seed next week's log

Calculate the Monday of **next** week. Derive the file path from the weekly logs folder and file naming above.

If the file **does not exist**, create it from the template note above.

Populate the following sections from this week's wrap-up — but **do not populate daily entries** (leave Mon–Fri blank so there's a clean starting point on Monday):

1. **Goals for this week** — carry forward the goals from Step 6 as `[ ]` checkbox items
2. **Sprint Goals** — carry forward the ticket-linked Sprint Goal header from the current week, and re-derive the goal list (see Terminology in Guidelines) for the new week, excluding anything now `Done`
3. **This Weeks Tickets** — carry forward any tickets from this week's table that are not `Done`, preserving their current Jira status from Step 3
4. **Action Items** — carry forward any unresolved action items

If the file **already exists**, only populate sections that still contain placeholder/template text. Do not overwrite existing content.

## Step 10 — Final verification and summary

Read back the updated current week's log and confirm:

- Achievements are written (not placeholder text)
- Brain Dump is either filled in or removed
- AI-free Reflection is either filled in or removed
- Ticket statuses match Jira
- Every ticket reference in the file (Goals, Sprint Goals, Action Items, the ticket table, and every daily entry) is a markdown link per the Ticket links guideline — grep for bare ticket keys (`[A-Z][A-Z0-9]+-\d+`) not already inside `[...]( ... )` and fix any found before presenting the final summary

Then render a terminal ASCII summary dashboard. Use box-drawing characters and block elements. The summary must include all of the following sections:

### Header

```
╭───────────────────────────────────────╮
│  Weekly Wrap-Up — {week-start date}          │
╰───────────────────────────────────────╯
```

### Ticket Progress

For each ticket in the table, render a progress bar inferred from its status at runtime: category `new` is about 10%, `done` is 100%, and `indeterminate` statuses sit between about 35% and 95%, ordered by how far along the status name suggests (building < review < QA < awaiting release). A `Blocked` status keeps the progress of the state it was blocked from, with a ⛔ indicator.

Use `█` for filled and `░` for empty. Bar width = 20 chars. After the status label, append the ticket name (from the table's Name column) for easy identification.

```
📊 Ticket Progress
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJ-101  ████████████████████  Done            Add export button to reports page
PROJ-102  ██████████████░░░░░░  In Review       Cache user preferences on login
PROJ-103  ███████░░░░░░░░░░░░░  In Progress     Fix timezone in billing summary
PROJ-104  ███████░░░░░░░░░░░░░  ⛔ Blocked       Waiting on upstream API change
```

### Goals & Achievements

Show goal completion as a progress bar with fraction and percentage, plus achievement counts per category.

```
🎯 Goals      [4/6] ▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 67%
📝 Achievements     5 delivery · 3 craft · 5 influence
```

### Status Changes

If any ticket statuses were updated from Jira in Step 3, list them:

```
🔄 Status Updates
   PROJ-102  In Progress → In Review
   PROJ-103  Open → In Progress
```

If no changes, show: `🔄 Status Updates   none`

### Carry Forward

Show what was seeded into the next week's log:

```
➡️  Carry Forward → {next-week-filename}
   · 3 goals
   · 2 tickets
   · 0 action items
```

If next week's log was not seeded, show: `➡️  Carry Forward   n/a`

### Week Summary

A short plain-text summary (3–5 sentences) synthesising the week — key themes, progress highlights, notable blockers or decisions. Write in past tense, first-person implied. Place it after the Sections Completed block.

```
📋 Week Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Focused primarily on the reports UI work, introducing a shared store to clean up
prop drilling across the list and detail views. Cleared the feature flag clean-up
(PROJ-102) through review. The export tickets all moved to Done once the privacy
review completed. PROJ-105 was scoped and deliberately cut after determining the
value was too low; changes folded into the main feature branch.
```

### Sections Completed

A checklist of what the skill filled in:

```
✅ Sections
   ✓ Achievements (Delivery / Craft / Influence)
   ✓ Brain Dump
   ✓ AI-free Reflection
   ✓ Ticket statuses synced
   ✓ Next week seeded
```

Use `✗` for any section that was skipped or left empty. Brain Dump and AI-free Reflection each show `✓ removed` if the user chose to remove the section, `✓ filled` if content was written, or `✗ skipped` if neither happened.

### Tech Lead Review

Skip this section entirely if no review context notes are configured. A short, genuinely-invested reflection on the week — written in the voice of a tech lead at `${user_config.company_name}` reviewing the user's week. The bar for what counts as impressive or as a gap should be calibrated to a senior IC at a strong product company. Place this last, after Sections Completed.

Ground it in the context notes listed in the configuration above (operating principles, focus areas, standing growth themes). Don't re-read whole folders every time — those notes are the steady-state context; only go deeper if the week's work or conversation surfaced something more specific.

Connect 1–3 _specific_ things from this week's actual work to those goals/bar — don't force a connection that isn't genuinely there. Good signal to look for: deep technical work that's a strong interview/portfolio story (e.g. an architectural migration, a perf fix, a gnarly root-cause), or evidence of the growth themes in the context notes.

**Be genuinely critical, not just complimentary.** A real tech lead at this calibre of company would name what's actually missing or weak, not soften everything into praise. Look for real gaps every week, even in a good one — e.g. a decision made without considering an alternative, a fix that addressed the symptom but not the root cause, a missed chance to write the work up or share it, scope/tradeoffs that weren't made explicit, time lost to a process gap. If the week was genuinely strong, it's fine to say so plainly — but don't manufacture praise to avoid criticism, and don't manufacture criticism to seem balanced either. Tone: direct and specific, not corporate, not sycophantic, still supportive — a tech lead who rates you and wants you to level up, not one being harsh for its own sake.

**Don't inflate the severity of what actually happened.** The criticism must be anchored to what the log/reflection actually says — if an issue was caught in dev/testing, say that; don't imply it reached Prod, caused a customer-facing incident, or was worse than documented just to make the critique land harder. Inventing or exaggerating impact is a fabrication, same as inventing a delivery bullet that isn't supported — it undermines trust in the review. If the log doesn't say where/when something was caught, don't assume the worst case.

**Most weeks are BAU/feature work — that's the normal baseline, not a gap in itself.** Architectural/systems-level work happens occasionally, not every week. Don't flag "this week was mostly BAU" as a problem on its own — but do still hold BAU work to the target company's bar (e.g. was a root cause actually found, or just patched; was a tradeoff made consciously or by default).

**End with one concrete, actionable suggestion the user can actually try next week** — not a vague nudge. Make it small and specific enough to act on (e.g. "next time you hit an API integration question, write the assumption down and check the doc before building on it" rather than "be more careful"; or "worth carving 30 min this week to write up the store migration as a note while it's fresh" rather than "keep building your track record").

**Optional: critique time/effort allocation across the week.** Look at how the daily entries actually split — deep-focus work vs. reactive/BAU vs. context-switching across tickets/meetings — and whether that split served the week well or fought against it. This is about _how_ the week was run, not what got delivered. Only include this if there's a genuine, specific observation (e.g. a day fragmented across 3+ unrelated things, a deep-work block that kept getting interrupted by release support, or conversely a day that protected focus well and it showed in the output) — skip it for an unremarkable week rather than forcing a take. Calibrate against how a senior IC at the target company would be expected to manage their week (protecting deep work, batching context switches, not letting reactive work silently eat the focus time), not against a generic productivity standard.

Do not penalize time spent on something that was a scheduled obligation, roster duty, or otherwise outside the user's control (e.g. a rostered release-support slot) — that's not a time-management failure, it's an externally-imposed constraint, and conflating the two is an unfair critique. This is exactly why Step 2a's context-gap check matters: if a day's entry doesn't make clear whether something was planned/rostered vs. an unplanned pull-in, that ambiguity should have been resolved when drafting the entry (ask, don't assume) rather than guessed at here. If it's still ambiguous at this step, don't speculate — either ask, or simply describe the time split factually without assigning blame for it.

```
🧑‍🏫 Tech Lead Review
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Review
{2-3 sentences of warm, specific reflection on the week, written directly to the user
in second person}

Time & focus (optional — only if there's a genuine observation)
{1-2 sentences on how the week's time was actually spent and whether that served
the work, or omit this block entirely}

Try next week
{1 concrete, actionable suggestion}
```

## Guidelines

- **Obsidian CLI first** for all vault reads/writes (`obsidian vault="${user_config.vault_name}" ...`) — fall back to Read/Edit only if CLI fails
- **Do not fabricate detail** — if daily entries don't support a bullet, don't invent one
- **No ceremony bullets** — standup, planning, refinement, retro and similar recurring ceremonies are too standard to justify a line in the daily entries or Achievements; only call out a meeting if it was a notable one-off
- **Consolidate, don't transcribe** — whether drafting daily entries from git/Sunsama or Achievements in Step 5, group related commits/feature-branch changes into a small number of high-level bullets describing the outcome, not a line per commit. Aim for ~3 dot points per ticket/piece of work
- **Achievements ≠ Brain Dump** — these sections must not overlap; achievements = factual delivery, brain dump = reflective/analytical
- **One question per section** — don't batch all reflective prompts into a single question
- **Formatting** — follow vault formatting rules: no blank lines between list items, no blank lines after headings, `---` only between genuinely distinct sections, and no trailing `-` after a ticket/section subheading (e.g. `- **PROJ-106**`, not `- **PROJ-106** -`)
- **Ticket links** — every ticket reference anywhere in the log (Goals, Sprint Goals, Action Items, This Weeks Tickets table, daily entries) should be a markdown link to Jira, not a bare or backtick-wrapped ticket number. Never put the ticket reference in trailing brackets after the description (it reads as noise), e.g. not `Show provisioning state on service status ([PROJ-107](...))`. **Link text differs by section**: Goals, Sprint Goals, Action Items, and the This Weeks Tickets table use the ticket ID as link text (`[{PROJECT_KEY}-XXXX]({JIRA_SERVER}/browse/{PROJECT_KEY}-XXXX)` — see the Goals / Sprint Goals link format guideline for why). Daily entries (Mon–Fri) instead use a short human-readable name derived from the ticket title, trimmed to ~3–4 words (`[Port status labels]({JIRA_SERVER}/browse/PROJ-108)`, not `[PROJ-108](...)`) — daily bullets are meant to be scannable without following the link.
- **Goals / Sprint Goals link format** — keep the link scoped to just the ticket ID, followed by `—` and the title as plain text: `[PROJ-107]({JIRA_SERVER}/browse/PROJ-107) — Show provisioning state on service status`. Don't fold the title into the link text itself — once the whole "ID + title" string is link-styled, the ID and title lose visual contrast and the line gets harder to scan. Do not automatically append a trailing status in parens (e.g. `(Code Review)`) — this is a manual addition the user makes themselves, not something the skill should write.
- **Other project keys** — tickets from other Jira projects (e.g. `OTHER`) are on the same instance (`{JIRA_SERVER}`) — link them the same way: `[OTHER-16]({JIRA_SERVER}/browse/OTHER-16)`. Do not link to a vault note or use wikilink/alias syntax. In Goals and Sprint Goals, follow the same `— ticket name` suffix (see the Goals / Sprint Goals link format guideline).
- **Fold vs nest for ticket entries in daily logs** — when a ticket's day only has one dot point of substance, fold it onto a single inline line: `- **[Ticket Name](...)** - description`. When it has more than one dot point, nest it as a header with indented sub-bullets: `- **[Ticket Name](...)**` followed by indented `- ` lines. Don't mix — pick fold or nest per ticket per day based on this count, so the same ticket isn't represented inconsistently across days for no reason. Link text here follows the daily-entry convention (short name, not ID) per the Ticket links guideline above.
- **Action Items formatting** — write a human-readable description, not a repeated mechanical phrase like "Follow through Code Review to Done" per ticket. When multiple tickets share the same action (e.g. several tickets all just need to move through to Done), group them on one bullet separated by `⋅`, with the shared description as an indented sub-bullet:
  ```
  - [PROJ-106]({JIRA_SERVER}/browse/PROJ-106) ⋅ [PROJ-109]({JIRA_SERVER}/browse/PROJ-109)
  	- Move through to Done
  ```
- **Group similar tickets under a shared header** — when a section contains multiple tickets that are variants of the same piece of work (e.g. several label-update tickets across different pages, or several tickets blocked for the same reason), don't list them flat — group them under a bold sub-header with the individual tickets indented underneath, the same pattern already used for the `**Labels**` group in the This Weeks Tickets table. Apply this consistently across **Goals for this week**, **Action Items**, the **This Weeks Tickets** table, and daily entries (Monday–Friday) — if a day's work spans multiple related tickets under one theme, group them under a header there too rather than listing each as a separate top-level bullet. Don't force a grouping for tickets that aren't actually related — this is for genuine thematic clusters, not an arbitrary split.
- **Exclude pure-toggle tickets** — when pulling candidate tickets for Sprint Goals/Goals/the ticket table, drop any ticket whose Jira issue type is "Toggle" (it only tracks a feature-toggle on/off state, not delivery work) unless the user explicitly asks for it
- **Terminology — Goals vs Sprint Goals vs Action Items (do not conflate these)**:
  - **Goals for this week** = the north-star priority for the week — where most focus should go. Usually 1–2 items, not a sprint-wide list.
  - **Sprint Goals** = the goal lines from the active sprint's Jira goal field (board `{BOARD_ID}`) that involve the user's work, each linked to the relevant ticket(s), excluding anything already `Done`. The goal field is themed free text, not a ticket list — confirm which lines apply via the sprint tickets assigned to the user, and ask if a line is ambiguous. Don't assume a squad-wide goal is the user's individual work.
  - **Action Items** = near-term, operational things to close out or progress this week (e.g. "follow {PROJECT_KEY}-XXXX through to Done"). These are not the same as Goals or Sprint Goals, and should not include items that are someone else's responsibility to surface (e.g. a ticket that will come back to the user once a PO/another party resolves something — ask before adding this kind of item).
