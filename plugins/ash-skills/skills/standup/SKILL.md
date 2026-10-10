---
name: standup
description: Quick standup prep — pulls today's tasks (Sunsama, if available), today's weekly log entry, and git activity to produce a Today + Blockers summary. Chat output only, nothing written to the vault.
---

Pre-standup summary. Read-only — this skill never writes to Obsidian, Jira, or git. It reports what's already there.

Plugin config values below come from the user config; a blank value means "not configured".

## Configuration

- Vault: `${user_config.vault_name}`, rooted at `${user_config.vault_path}`
- Weekly logs: `${user_config.weekly_log_folder}/` (`{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}`, dated by the week's Monday

## Environment

Resolved from the shell, not plugin config:

- Author: `git config user.name`, run inside the repo
- Jira: the `jira` CLI's config (`~/.config/.jira/.config.yml`) supplies `{JIRA_SERVER}` (`server`), `{PROJECT_KEY}` (`project.key`) and `{BOARD_ID}` (`board.id`); `jira me` is the signed-in user; REST calls use `$JIRA_API_TOKEN`
- Ticket status: read from Jira at runtime (`jira issue view {KEY} --raw`, `fields.status.statusCategory.key`: `new`, `indeterminate` or `done`). A ticket is *finished* when its category is `done`, or its status says only release/deploy remains (e.g. "Pending Deploy", "Ready for Release")
- Repos: the repo in the current directory; for another repo, look beside it or ask where it lives
- GitHub: `gh`, signed in; skip PR lookups if it isn't available
- Sunsama: used only if its MCP tools are available

## Step 1 — Gather today's signal

1. If the Sunsama MCP is available (otherwise skip Sunsama everywhere below), pull today's tasks and calendar events from it (`sunsama://tasks/{date}`, `sunsama://calendar/events/{date}`).
2. Read today's entry from the current week's Obsidian log via the Obsidian CLI, if the file exists. If it doesn't exist yet, or today's section is still placeholder-only, that's fine — just note there's no vault signal and continue with Sunsama/git.
3. From both sources, extract ticket numbers (Jira links on Sunsama tasks, ticket prefixes in task/log titles).

## Step 1a — Walk the board for active assigned tickets

Query the current sprint directly for every ticket assigned to the user that isn't done, so nothing falls through the cracks that Sunsama/the vault log didn't happen to mention:

`jira sprint list --current --plain --columns KEY,SUMMARY,STATUS,ASSIGNEE --paginate 100`

- Filter to rows where assignee is the user and status category isn't `done` (this also excludes closed statuses such as `Discarded`).
- Union this set with the tickets found in Step 1 — a ticket found only here (not in Sunsama/the log) still gets its own entry in the standup; note in Step 7 that it came from the board, not from tracked work.
- This is the source of truth for "what's actively assigned to me" — Sunsama/the log tell you what was _worked on_, this tells you what _should_ be walked even if untouched.

## Step 2 — Check git activity

For each ticket found:

1. Search the repo's git log for commits authored by the user today: `git -C {repo} log --all --since="{date} 00:00" --until="{date+1} 00:00" --author="$(git config user.name)"`.
2. If a task/ticket mentions another repo by name or context, search that repo's git log the same way. Don't scan repos speculatively — only follow an explicit signal in the task/ticket text.

## Step 2a — Check PRs raised recently

From the repo (or another repo if git activity pointed there), list PRs the user has raised since yesterday: `cd {repo} && gh pr list --author @me --state all --search "created:>={yesterday}"`.

- If a PR is tied to a ticket already in scope (via its description/title referencing the ticket key, e.g. "Driven by work on PROJ-101"), fold it into that ticket's entry in Step 5 rather than giving it a separate line — e.g. a fix PR raised off the back of a ticket, with known test failures blocking progress, becomes part of _why_ that ticket is blocked.
- Don't assume the PR's check status reflects live reality — the last recorded CI run can be stale (e.g. shows "passed" even though the user knows there are unresolved test failures from working on it today). If the user states something that contradicts what CI shows, trust the user and flag the discrepancy in the Step 8 reference note, not the spoken body.

## Step 3 — Fold in continuity from yesterday, only where relevant

Do not build a separate "yesterday" section. For a ticket that's continuing from yesterday (visible via Sunsama task history, or the log's prior-day entry, or a ticket status that implies it's mid-flight), fold a short clause into today's line for that ticket — e.g. "continuing the cart validation fix started yesterday" — only when it materially explains today's status. Skip this for tickets that are simply new today.

## Step 4 — Determine blockers

Check in this priority order, stopping at the first that gives a clear answer per ticket:

1. Obsidian notes (today's/this week's log) for an explicit blocker mention
2. Sunsama task notes for an explicit blocker mention (unlikely, but check)
3. Jira: `jira issue view {KEY} --plain` — check status (e.g. `Blocked`) or a flagged indicator
4. Infer from whatever else is available (e.g. a task sitting untouched for days with no progress signal)
5. If none of the above give a signal, default to **not blocked** — do not assume a blocker exists without evidence

Track which of these ticks fired for each ticket — this feeds the assumptions footnote in Step 8.

For any ticket that's `Blocked` (whether it's getting a full entry in Step 5 or landing in the Step 5a "Nothing to update" list), don't stop at the status flag — pull the actual reason: `jira issue view {KEY} --plain --comments 5` and read the most recent comment(s) for what it's waiting on (e.g. "waiting on multi-site testing", "dependency on multisite code targeting 23 July"). Prefer the latest comment over the ticket description, since the description is often stale relative to why it's blocked _now_.

## Step 5 — Draft the standup update

Output has two sections: **Standup Update** (what the user is actually giving an update on) and, only if something qualifies, **Nothing to update** (tickets that exist and are assigned, but have no real news). Keep these visually and structurally separate — the first is what gets said out loud, the second is a reference list, not spoken material.

### Standup Update

This is spoken out loud in a standup, not read as a report — write it like the user is actually talking, first person, flowing sentences. Not a bullet-per-ticket dump with metadata tags, but not one giant merged paragraph either.

- A ticket belongs here if there's genuine news: it was worked on today, its status changed, or there's a new/updated blocker worth surfacing.
- **One entry per ticket, led by the ticket link plus its title, with a natural-sounding sentence or two underneath** — e.g. `**[PROJ-102](...) — Status shows UP while provisioning** — Dev and code review are both done here, the only thing blocking me is waiting on test data from the backend team.` The ticket key/link is how the user visually tracks which update is which, the title gives it a name they can scan without opening Jira, and the sentence after it is what they'd actually say.
- Only merge two tickets into one entry/paragraph when they're genuinely the same piece of work or directly related — don't merge just because they happened on the same day. Default to one ticket, one entry.
- Fold in continuity from yesterday within that ticket's own entry where relevant (per Step 3) — not as a separate section
- Fold blockers (and any related PR from Step 2a) into the relevant ticket's entry rather than a separate hard-headed section — a blocker is just part of what the user would say about that ticket ("...the only thing blocking me is..."). If a ticket has no blocker, don't force a mention of "no blockers" — just don't say anything about it
- Don't fabricate detail beyond what git/Sunsama/the log actually support — if a ticket has nothing beyond a generic title, say that plainly and briefly, in the same conversational tone (e.g. "not much to report yet here, still early")
- No ceremony entries (standup, planning, refinement, retro) in the update itself

### Step 5a — "Nothing to update" section

Once a ticket has been reported as blocked or untouched in a prior standup, its status is unlikely to have meaningfully changed by the next one unless something explicitly moved. Rather than forcing a spoken line for these every time, list them separately and briefly:

- Candidates: Step 1a board tickets with no Step 1–3 signal today, and any ticket that's genuinely got nothing new to say (untouched backlog items, blocked tickets sitting exactly where they were).
- Format as a flat bullet list, one line per ticket: `[KEY](link) — title (status context, e.g. "blocked, untouched" or "backlog, untouched")`.
- **If a ticket is `Blocked`, append the reason** found in Step 4 (latest Jira comment) — e.g. `blocked on the API change landing in staging`. Don't just say "blocked" with no reason if a reason was findable.
- **Omit this entire section (including its heading) if nothing qualifies** — don't force it to appear empty or with a "nothing here" placeholder. A standup with every ticket having real news needs no such section at all.

## Step 6 — Context (optional)

Only include this if something genuinely adds useful colour to the standup — sprint goal linkage, an approaching sprint/deadline date, a related ticket/epic another team is waiting on, or something notable from Jira/Confluence that explains _why_ today's work matters. Sources: the current week's log's Sprint Goals section, Jira ticket epic/links, sprint end date if visible.

Keep it to 1–3 sentences, written in the same natural spoken tone as Step 5 — not a data table or bullet list. If nothing surfaces that's genuinely worth saying out loud, omit this section entirely. Don't manufacture context just to fill the section.

## Step 7 — Example output shape

```markdown
## Standup Update

**[PROJ-101]({JIRA_SERVER}/browse/PROJ-101) — Show provider details on order confirmation** — This one's wrapped up today, dev and code review both done, handed over to QA and tested, so it's sitting at Ready For Release now.

**[PROJ-103]({JIRA_SERVER}/browse/PROJ-103) — Update status labels in the app** — Spent the morning on this, mocks are done but investigation, dev and code review are all still open. This one's actually tied up with the test-setup fix PR (#123) I raised yesterday off the back of this work — there are some test failures in there I'm still working through, and until that's merged I can't really finalise the label changes, so that's the real blocker on this ticket right now.

## Nothing to update

- [PROJ-104]({JIRA_SERVER}/browse/PROJ-104) — Hide deprecated options — blocked on the API change landing in staging
- [PROJ-105]({JIRA_SERVER}/browse/PROJ-105) — Billing date displays in the wrong timezone (backlog, untouched)

---

**Reference note:** PR #123 (test-setup fix) was raised on {date} and is still open — its last recorded CI run passed, so the test failures aren't reflected there yet; that detail came from you, not from CI/PR data.
```

This is a shape reference, not literal content to reuse — ticket keys, statuses, and blocker text must always come from that day's actual Sunsama/git/Jira/GitHub lookups.

## Step 8 — Assumptions / reference footnote

One short, plain line (or a couple, if genuinely distinct) for the user's eyes only — an inline comment _from the agent_, never something they'd say out loud, and never blended into the spoken body above. Use it to flag standout discrepancies: assumptions made, data that contradicts what the user said, tickets sourced only from the board rather than tracked work, stale pipeline statuses, etc. Separate it clearly from everything above with a horizontal rule (`---`) and a small `Reference note:` label, so it visually reads as a distinct footer:

```
---
**Reference note:** no commits found for any ticket today; PROJ-106's progress is based on this session's own work, not git/Sunsama.
```

If nothing was inferred, omit this section entirely — including the `---` separator.

## Guidelines

- **Chat output only** — never write to the Obsidian vault, never update Jira, never touch git or GitHub (read-only `gh`/`git log` lookups only). This is strictly a read/report skill.
- **Do not fabricate** — if a ticket has no commits and no notes beyond a generic title, say so plainly rather than inventing detail.
- **No ceremony bullets** — don't list standup/planning/refinement/retro as "today" items.
- **Natural first, links second** — the spoken update should read like a person talking; a markdown link on first mention of a ticket is fine, but don't let formatting override the natural flow of the sentence.
