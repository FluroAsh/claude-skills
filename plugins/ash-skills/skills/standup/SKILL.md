---
name: standup
description: Quick standup prep — pulls today's tasks (Sunsama, if available), today's weekly log entry, git, GitHub reviews, Slack and Jira to produce a Today + Blockers summary in chat. With `--after`, compacts pasted meeting notes into that day's standup note.
argument-hint: "[--after [date] [--keep-transcript]]"
---

Pre-standup summary. Read-only unless `--after` — it reports what's already there. `--after` writes only the day's standup note and never writes to Jira or git.

With no flag, run Steps 1–8. With `--after`, skip them and follow `## --after` at the end.

## Configuration

Read `${CLAUDE_PLUGIN_ROOT}/reference/config.md` once at the start of the run: it gives the resolution order (stored value, else convention, else ask once and suggest `/ash-skills:setup`). Paths are vault-relative.

- Vault: `${user_config.vault_path}` (`vault_path`; else Obsidian's vault registry). `{VAULT_NAME}` is its last path segment
- Weekly logs: `${user_config.weekly_log_folder}/` (`weekly_log_folder`; else `10 - Meetings/Weekly Work Logs/{YEAR}/`, `{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}` (`log_filename_format`; else inferred from existing logs, `MM-DD-YY.md` if none), dated by the week's Monday
Used only by `--after`:

- Standups: `${user_config.standup_folder}/` (`standup_folder`; else `10 - Meetings/<anything> Standup/` or `10 - Meetings/Standup/`), files `MM-DD-YY.md`
- Standup template: `${user_config.standup_template}` (`standup_template`; else `Standup Template` in the templates folder)
- Team context: `${user_config.team_context_file}` (`team_context_file`; else a vault-root note ending in `Team` or `Squad`, else the Jira roster per config.md)

## Environment

Resolved at runtime, not plugin config:

- Author: `git config user.name`, run inside the repo
- Jira: the Atlassian MCP (see config.md), for get issue (e.g. `getJiraIssue`) and JQL search. `{JIRA_SERVER}` is `https://` plus `${user_config.jira_site}` and `{PROJECT_KEY}` is `${user_config.jira_project}`; if unset, take them from the MCP. If the MCP isn't connected, say so in Step 8 and skip the Jira steps
- Ticket status: read from Jira at runtime (get issue, `fields.status.statusCategory.key`: `new`, `indeterminate` or `done`). A ticket is *finished* when its category is `done`, or its status says only release/deploy remains (e.g. "Pending Deploy", "Ready for Release")
- Repos: the repo in the current directory; for another repo, look beside it or ask where it lives
- GitHub: `gh`, signed in; skip PR and review lookups if it isn't available. The login is `gh api user --jq .login`
- Slack: used only if its MCP tools are available (`slack_search_public_and_private`); the user's own ID comes from that tool's description
- Timezone: the user's local timezone (`date +%Z`). GitHub and Slack return UTC, so convert every timestamp before deciding which day it falls on
- Window: `{prev}` is the previous working day (Friday when today is Monday); review and Slack lookups cover `{prev}` through now, since that's what the team hasn't heard yet
- Sunsama: used only if its MCP tools are available

## Step 1 — Gather today's signal

1. If the Sunsama MCP is available (otherwise skip Sunsama everywhere below), pull today's tasks and calendar events from it (`sunsama://tasks/{date}`, `sunsama://calendar/events/{date}`).
2. Read today's entry from the current week's Obsidian log via the Obsidian CLI, if the file exists. If it doesn't exist yet, or today's section is still placeholder-only, that's fine — just note there's no vault signal and continue with Sunsama/git.
3. From both sources, extract ticket numbers (Jira links on Sunsama tasks, ticket prefixes in task/log titles).

## Step 1a — Walk the board for active assigned tickets

Query the current sprint directly for every ticket assigned to the user that isn't done, so nothing falls through the cracks that Sunsama/the vault log didn't happen to mention:

JQL search: `sprint in openSprints() AND assignee = currentUser() AND project = {PROJECT_KEY}`

- Filter to tickets whose status category isn't `done` (this also excludes closed statuses such as `Discarded`).
- Union this set with the tickets found in Step 1 — a ticket found only here (not in Sunsama/the log) still gets its own entry in the standup; note in Step 8 that it came from the board, not from tracked work.
- This is the source of truth for "what's actively assigned to me" — Sunsama/the log tell you what was _worked on_, this tells you what _should_ be walked even if untouched.

## Step 2 — Check git activity

For each ticket found:

1. Search the repo's git log for commits authored by the user today: `git -C {repo} log --all --since="{date} 00:00" --until="{date+1} 00:00" --author="$(git config user.name)"`.
2. If a task/ticket mentions another repo by name or context, search that repo's git log the same way. Don't scan repos speculatively — only follow an explicit signal in the task/ticket text.

## Step 2a — Check PRs raised recently

From the repo (or another repo if git activity pointed there), list PRs the user has raised since yesterday: `cd {repo} && gh pr list --author @me --state all --search "created:>={yesterday}"`.

- If a PR is tied to a ticket already in scope (via its description/title referencing the ticket key, e.g. "Driven by work on PROJ-101"), fold it into that ticket's entry in Step 5 rather than giving it a separate line — e.g. a fix PR raised off the back of a ticket, with known test failures blocking progress, becomes part of _why_ that ticket is blocked.
- Don't assume the PR's check status reflects live reality — the last recorded CI run can be stale (e.g. shows "passed" even though the user knows there are unresolved test failures from working on it today). If the user states something that contradicts what CI shows, trust the user and flag the discrepancy in the Step 8 reference note, not the spoken body.

## Step 2b — Reviews and PR state

1. **Reviews of other people's PRs** (no commits or authored PRs, so otherwise missed):
   `gh api graphql -f query='query{search(query:"is:pr reviewed-by:{login} -author:{login} updated:>={prev-1}",type:ISSUE,first:30){nodes{... on PullRequest{number title url state author{login} reviews(first:50,author:"{login}"){nodes{state submittedAt}}}}}}'`
   Keep reviews whose `submittedAt`, in local time, falls in the window. Use `APPROVED`, `CHANGES_REQUESTED` and `COMMENTED`; never use `DISMISSED` (note it in Step 8). The search is org-wide, so no per-repo loop.
2. **The user's own open PRs** (from Step 2a, plus any still open from earlier): `gh pr view {n} --json reviewDecision,reviews` — an approval, requested changes or a PR still waiting on review is news the team needs ("approved by X", "waiting on a reviewer").

## Step 2c — Slack

Search `from:<@{slack_user_id}> after:{prev-1}` (sorted by timestamp), keep messages in the window, and skim for work outcomes the team should know: decisions, issues raised with other teams, unblocking someone, waiting on someone. Skip chatter, reactions and social messages. Attach each outcome to its ticket where the thread names one. Ambiguous DMs (implied decision, unclear outcome) aren't used; note them in Step 8.

## Step 3 — Fold in continuity from yesterday, only where relevant

Do not build a separate "yesterday" section. For a ticket that's continuing from yesterday (visible via Sunsama task history, or the log's prior-day entry, or a ticket status that implies it's mid-flight), fold a short clause into today's line for that ticket — e.g. "continuing the cart validation fix started yesterday" — only when it materially explains today's status. Skip this for tickets that are simply new today.

## Step 4 — Determine blockers

Check in this priority order, stopping at the first that gives a clear answer per ticket:

1. Obsidian notes (today's/this week's log) for an explicit blocker mention
2. Sunsama task notes for an explicit blocker mention (unlikely, but check)
3. Slack threads from Step 2c, or a PR from Step 2b waiting on review / with changes requested
4. Jira: get issue (e.g. `getJiraIssue`) — check status (e.g. `Blocked`) or a flagged indicator
5. Infer from whatever else is available (e.g. a task sitting untouched for days with no progress signal)
6. If none of the above give a signal, default to **not blocked** — do not assume a blocker exists without evidence

Track which of these ticks fired for each ticket — this feeds the assumptions footnote in Step 8.

For any ticket that's `Blocked` (whether it's getting a full entry in Step 5 or landing in the Step 5a "Nothing to update" list), don't stop at the status flag — pull the actual reason: get the issue with its comments and read the most recent comment(s) for what it's waiting on (e.g. "waiting on multi-site testing", "dependency on multisite code targeting 23 July"). Prefer the latest comment over the ticket description, since the description is often stale relative to why it's blocked _now_.

## Step 5 — Draft the standup update

Output has two sections: **Standup Update** (what the user is actually giving an update on) and, only if something qualifies, **Nothing to update** (tickets that exist and are assigned, but have no real news). Keep them visually separate: the first is read out, the second is a reference list.

### Standup Update

This is the user reporting to their manager and team, out loud. It should give them the context to understand what the user is working on: what the work is in plain terms, where it's at, what happens next, and anything the user needs from someone. Write it as the user talking, first person, in natural sentences. Ticket keys and PR numbers are fine inline; status fields, metadata tags and shorthand are not.

- A ticket belongs here if there's genuine news: it was worked on today, its status changed, its PR was reviewed/approved, a Slack thread moved it, or there's a new/updated blocker worth surfacing.
- **Keep it compact.** Keep what the team needs: status/outcome, PR state, blockers and who it's waiting on, handoffs or asks of others. Cut process narration ("spent the morning", which subtasks are open) unless it explains a blocker.
- **Plain meaning, not Jira status.** Say what a status means ("ready to go out with the next release"), not the field value ("at Ready For Release").
- **What's next**, only when a source shows it: a stacked PR, a ticket comment, the log, a Slack thread. Never guess a next step or a date.
- Fold continuity from yesterday (Step 3), blockers and any related PR (Step 2a) into the ticket's own update. No "no blockers" filler when there is none.
- Don't fabricate detail beyond what the sources support — if a ticket has nothing beyond a generic title, say so plainly (e.g. "not much to report yet here, still early").
- No ceremony entries (standup, planning, refinement, retro).
- Slack outcomes fold into their ticket. One not tied to a ticket but relevant to the team goes in a `◆ OTHER` group as one short line; never a transcript.

#### Grouping

- **Epic:** the ticket's parent epic (get issue, `fields.parent`; one call per ticket, reusing data already fetched). Group heading: `**◆ {EPIC NAME IN CAPS}** · [{EPIC-KEY}]({JIRA_SERVER}/browse/{EPIC-KEY})`.
- **Sub-groups:** within an epic, group by the current weekly log's Sprint Goals when a goal clearly names the ticket or its area. No match: no sub-group, tickets sit directly under the epic.
- **No epic:** group under a short topic heading (e.g. `◆ SERVICES PAGE POLISH`) with no key. Never invent an epic or present a topic as one.
- **Follow-ups:** a ticket split out of another, or whose PR is stacked on another's, nests under its parent ticket.
- **Combined updates:** when tickets in the same group share one story (one depends on the other, or they're in the same state for the same reason) and a sentence naturally covers them, give them one update under the group heading instead of a header each. Unrelated tickets that only share an epic keep their own headers; a forced paragraph reads worse than a list.
- **Code reviews** of others' PRs: a final `◆ CODE REVIEWS` group, one line per PR author or one combined line. Omit when there were none.
- Order groups by the epic with the most news first; order tickets within a group by how they'd be talked through (dependencies before dependents).

#### Tree format

The tree is plain markdown, not a code block, so links stay clickable. Markdown renderers strip leading spaces, collapse runs of spaces, and turn a line indented 4+ spaces after a blank line into a code block. So:

- **Indent with non-breaking spaces (U+00A0), never ordinary spaces.** This applies to every leading or alignment space in the tree.
- **End every tree line with two trailing spaces** so its line break survives.
- **No empty or space-only line anywhere inside a tree.** Either one starts a new paragraph, and renderers (the Claude Code terminal among them) strip the indent from a paragraph's start. Every line, separators included, has a visible connector after its indent.
- Heavy connectors: `┃` guide, `┣━` for a child with siblings below, `┗━` for the last child (`┣━━`/`┗━━` for sub-groups).
- **Ticket as header:** `┣━ **[KEY]({JIRA_SERVER}/browse/KEY) — Title**`, with the spoken update on the lines below behind a `┃` bar in the header's text column.
- **Combined update header:** the group heading carries the keys instead, `┣━━ **Checkout** · [KEY-1](…) · [KEY-2](…)`, with the update behind a `┃` bar the same way.
- **One thought per point**, one or two connected sentences; wrap long sentences across lines under the same guide. Separate distinct thoughts (where it's at, a handoff, an open question) with a separator line: the same guides and bar as the text lines, no text. Never split one thought across points.
- **Blocked:** append ` ⛔` to the ticket or combined-group header. It is the only emoji in the output; status otherwise lives in the words.
- Keep each update line under ~80 characters so wrapping doesn't break the guide.

### Step 5a — "Nothing to update" section

Once a ticket has been reported as blocked or untouched, it's unlikely to have changed by the next standup unless something explicitly moved. List these separately and briefly:

- Candidates: Step 1a board tickets with no Step 1–2c signal in the window, and any ticket with genuinely nothing new (untouched backlog items, blocked tickets sitting where they were).
- Place it below a heavy divider line (`━` × 40), headed `## ◇ Nothing to update`, then the italic line *Assigned to me but no news. Not for reading out.*
- Hollow connectors (`◇` group, `┊` guide, `└┄` ticket). Each ticket sits under its group path, e.g. `◇ Payments revamp › Labels`, using the same groups as Step 5.
- Ticket line: `└┄ [KEY](link) — Title · *status context*` (e.g. *backlog, untouched*). **For a `Blocked` ticket, the status context is the reason** from Step 4 (latest Jira comment) — never just "blocked" when a reason was findable.
- Same tree format rules as Step 5 (non-breaking spaces, trailing two spaces).
- **Omit the whole section, divider included, if nothing qualifies.**

## Step 6 — Context (optional)

Only include this if something genuinely adds useful colour to the standup — sprint goal linkage, an approaching sprint/deadline date, a related ticket/epic another team is waiting on, or something notable from Jira/Confluence that explains _why_ today's work matters. Sources: the current week's log's Sprint Goals section, Jira ticket epic/links, sprint end date if visible.

Keep it to 1–3 sentences, written in the same natural spoken tone as Step 5 — not a data table or bullet list. If nothing surfaces that's genuinely worth saying out loud, omit this section entirely. Don't manufacture context just to fill the section.

## Step 7 — Example output shape

`␣` marks a non-breaking space (U+00A0) and `⏎` two trailing spaces; emit the real characters, not these markers.

```markdown
## Standup Update

**◆ PAYMENTS REVAMP** · [PROJ-100]({JIRA_SERVER}/browse/PROJ-100)⏎
┃⏎
┣━━ **Checkout** · [PROJ-101]({JIRA_SERVER}/browse/PROJ-101) · [PROJ-102]({JIRA_SERVER}/browse/PROJ-102)⏎
┃␣␣␣┃␣␣Provider details on the order confirmation are approved and through QA,⏎
┃␣␣␣┃␣␣so they're ready to go out with the next release.⏎
┃␣␣␣┃⏎
┃␣␣␣┃␣␣The analytics follow-up (#125) is stacked on that PR, so it lands⏎
┃␣␣␣┃␣␣straight after it merges.⏎
┃⏎
┗━━ **Labels**⏎
␣␣␣␣┃⏎
␣␣␣␣┗━ **[PROJ-103]({JIRA_SERVER}/browse/PROJ-103) — Update status labels in the app** ⛔⏎
␣␣␣␣␣␣␣┃␣␣The mocks are done, but I can't finish the labels until my test-setup⏎
␣␣␣␣␣␣␣┃␣␣fix (#123) is merged.⏎
␣␣␣␣␣␣␣┃⏎
␣␣␣␣␣␣␣┃␣␣I'm still working through the failing tests there.⏎

**◆ CODE REVIEWS**⏎
┃⏎
┗━ Approved Sam's #412 (PROJ-210) and left comments on Alex's #398.⏎

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ◇ Nothing to update

*Assigned to me but no news. Not for reading out.*

◇ Payments revamp › Labels⏎
┊⏎
└┄ [PROJ-104]({JIRA_SERVER}/browse/PROJ-104) — Hide deprecated options · *blocked on the API change landing in staging*⏎

---

**Reference note:** epic confirmed from Jira for PROJ-101–104; Checkout and Labels are sprint-goal groups from the weekly log, and PROJ-101/102 share one update. PR #123's last CI run passed, so the test failures came from you, not CI.
```

This is a shape reference, not literal content to reuse — ticket keys, groups, statuses, and blocker text must always come from that day's actual Sunsama/git/Jira/GitHub/Slack lookups.

## Step 8 — Assumptions / reference footnote

One short, plain line (or a couple, if genuinely distinct) for the user's eyes only — an inline comment _from the agent_, never something they'd say out loud, and never blended into the spoken body above. Use it to flag standout discrepancies: how the grouping was decided (which epics came from Jira, which groups are inferred topics or sprint goals — never present an inferred group as fact), assumptions made, sources skipped (no `gh`/Slack), dismissed reviews and ambiguous DMs left out, data that contradicts what the user said, tickets sourced only from the board rather than tracked work, stale pipeline statuses, etc. Separate it clearly from everything above with a horizontal rule (`---`) and a small `Reference note:` label, so it visually reads as a distinct footer:

```
---
**Reference note:** no commits found for any ticket today; PROJ-106's progress is based on this session's own work, not git/Sunsama.
```

If nothing was inferred, omit this section entirely — including the `---` separator.

## Guidelines

- **Chat output only** (no flag) — never write to the Obsidian vault, never update Jira, never touch git or GitHub (read-only `gh`/`git log`/Slack search only). This is strictly a read/report skill.
- **Do not fabricate** — if a ticket has no commits and no notes beyond a generic title, say so plainly rather than inventing detail.
- **No ceremony bullets** — don't list standup/planning/refinement/retro as "today" items.
- **Natural first, links second** — the spoken update should read like a person talking; a markdown link on first mention of a ticket is fine, but don't let formatting override the natural flow of the sentence.

## --after

Compacts pasted meeting notes into the day's standup note. Writes only that note; never Jira or git.

- `[date]`: `MM-DD-YY` (e.g. `11-12-26`); default today. `{date}` below means this date
- `--keep-transcript`: keep the paste under `## Original notes` at the bottom (compact-notes' `--keep-original`)

### Step A1 — Find the day's note

`{standup_folder}/{date}.md`. If it doesn't exist, create it from the standup template via the Obsidian CLI (Write if the CLI fails). The template is frontmatter plus a paste hint; this mode writes the sections.

### Step A2 — Find the source

1. Meeting notes or a file path given in the message.
2. Else the notes pasted into the day's note, from its only H1 (per compact-notes' Finding the source).
3. Else ask the user to paste the notes into the day's note, and stop. Write nothing (beyond a note created in Step A1).

Never read a transcription tool's local cache.

### Step A3 — Compact

Load the `compact-notes` skill with the Skill tool and apply it to the source, with the standup shape below as its instructions (`--keep-original` if `--keep-transcript`). Its draft comes back into this run: compact-notes asks nothing and writes nothing.

### Step A4 — Confirm and write

Show the draft in the terminal with line counts before and after. Ask once to write, saying the paste will be removed (or kept under `## Original notes` with `--keep-transcript`). Write only on a yes, then apply compact-notes' write rules (frontmatter `updated` and `compacted`, paste hint removed). This is the only confirmation the user sees.

### Step A5 — Verify and report

Check the written note: one H1, no paste hint, a blank line after every heading, no double blank lines. Fix and re-check if any fail. Report the path and `obsidian://open?vault={VAULT_NAME}&file={path, URL-encoded, no .md}`.

### Standup shape

- **First section: the user's own team or discipline**, one bullet per person, by name.
  - Team note present: name the section after the user's group there, in the order the note sets.
  - No team note: name it after the user's ticket-summary prefix (e.g. `FE`) when one is found, else `Me`. No fixed order; never claim one the data doesn't support.
- **Then everything else** under `###` headings by topic, ending with a team-process group (board counts, scheduling).
- **Actions and blockers stay inline** under their person or topic, each with an owner or `(?)`. No separate Actions or Blockers sections.
- Names come from team context (config.md); speech-to-text mangles are fixed from it, unknown names keep `(?)`.

```markdown
# Standup

## FE

- **Alex** — PROJ-123 in review, waiting on a second approver
- **Sam** — Picking up PROJ-124 next; blocked on API docs (owner: Jordan)

### Release timing

- Release moved to Thursday; Jordan to confirm with QA (?)

### Team process

- Board: 4 in progress, 2 in review
- Retro moved to Friday
```
