---
name: daily-work-wrap
description: Quick daily catch-up for the Obsidian weekly log — drafts today's entry from git, GitHub, Slack, Jira (and Sunsama, if available) when you forgot to track during the day.
---

End-of-day catch-up for the weekly work log in the user's Obsidian vault. This is the lightweight, single-day version of the `weekly-work-wrap` skill — use it any day you forgot to log as you went, not just Friday.

Plugin config values below come from the user config; a blank value means "not configured".

## Configuration

- Vault: `${user_config.vault_name}`, rooted at `${user_config.vault_path}`
- Weekly logs: `${user_config.weekly_log_folder}/` (`{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}`, dated by the week's Monday

## Environment

Resolved from the shell, not plugin config:

- Author: `git config user.name`, run inside the repo
- Jira: the `jira` CLI's config (`~/.config/.jira/.config.yml`) supplies `{JIRA_SERVER}` (`server`), `{PROJECT_KEY}` (`project.key`) and `{BOARD_ID}` (`board.id`); `jira me` is the signed-in user; REST calls use `$JIRA_API_TOKEN`
- Repos: the repo in the current directory; for another repo, look beside it or ask where it lives
- GitHub: `gh`, signed in; skip PR and review lookups if it isn't available. The login is `gh api user --jq .login`
- Slack: used only if its MCP tools are available (`slack_search_public_and_private`); the user's own ID comes from that tool's description
- Jira search: `jira issue list` or the Atlassian MCP's JQL search, whichever is available
- Timezone: the user's local timezone (`date +%Z`). GitHub and Slack return UTC, so convert every timestamp before deciding what falls on "today"
- Sunsama: used only if its MCP tools are available

## Step 1 — Locate today's entry

Calculate the Monday of the current week based on today's date, derive the log file path from the weekly logs folder and file naming above, and read it via the Obsidian CLI.

If the file doesn't exist, tell the user and stop — this skill assumes the week's log was already seeded (by the `weekly-work-wrap` skill the prior week).

Identify today's day name (Mon–Fri) and look at its section. If it already has real content (not just a placeholder `- `), show the user what's there and ask whether to leave it alone, append to it, or replace it — don't silently overwrite existing notes.

## Step 2 — Gather today's signal

1. If the Sunsama MCP is available, pull today's calendar events and tasks from it (`sunsama://calendar/events/{date}` and `sunsama://tasks/{date}`).
2. Identify ticket numbers referenced (Jira links on tasks, or ticket prefixes in titles).
3. For each ticket found, search the relevant repo's git log (the current repo, or one beside it) for today's commits authored by the user: `git log --all --since="{date} 00:00" --until="{date+1} 00:00" --author="$(git config user.name)"`.
4. PRs add outcome-level wording for what shipped: `gh pr list --author @me --state all --search "updated:>={date}"` (title and description summarise the work better than individual commits).
5. **Reviews of other people's PRs.** These leave no commits or authored PRs, so they are otherwise missed:
   `gh api graphql -f query='query{search(query:"is:pr reviewed-by:{login} -author:{login} updated:>={date-1}",type:ISSUE,first:30){nodes{... on PullRequest{number title url state author{login} reviews(first:50,author:"{login}"){nodes{state submittedAt}}}}}}'`
   Keep only reviews whose `submittedAt`, converted to local time, falls on today (the `date-1` in the query covers the UTC offset). Log `APPROVED` and `COMMENTED`/`CHANGES_REQUESTED` reviews. Do not log `DISMISSED` ones, list them in Step 5 instead. Cover repos other than the current one (e.g. a sibling e2e repo); the search is org-wide, so no per-repo loop is needed.
6. **State of the user's own PRs** (from the `gh pr list` in item 4): note review decision and approvals (`gh pr view {n} --json reviewDecision,reviews`) so the bullet can say "approved by X" or "moved to QA" rather than just "worked on".
7. **Slack.** Search `from:<@{slack_user_id}> on:{date}` (sorted by timestamp) and skim for work outcomes: decisions, issues raised with other teams, unblocking someone, cross-team coordination. Skip chatter, reactions and social messages. Ambiguous DMs (a decision is implied but the outcome isn't clear) are not drafted, list them in Step 5.
8. **Jira.** Search `assignee = currentUser() AND updated >= "{date}"` plus the keys from item 2, to catch tickets that moved today even if there were no commits.
9. Also check the **This Weeks Tickets** table in the log for tickets already in flight this week, in case today's work touched one without a Sunsama task logged.

If a ticket/task has no matching commits, no PR or review activity, no relevant Slack thread, and no notes/detail beyond a generic title, the source is too vague to draft from — stop and ask the user what was actually done rather than guessing. Same applies to non-ticket support roles (e.g. a release-support rotation) — ask whether it was rostered/scheduled vs. an ad-hoc pull-in if that's not already clear, since it matters for how the day reads later.

## Step 3 — Draft today's entry

Draft dot-point bullets grouped by ticket, following the same conventions as the weekly skill:

- Consolidate — group related commits into a small number of high-level outcome bullets, not one per commit. Aim for ~3 per ticket.
- Write generic outcome statements, not implementation blow-by-blow (e.g. "Reworked auth session handling", not which header/prop changed).
- Exclude standing ceremonies (standup, planning, refinement, retro) — only call out notable one-off meetings.
- **Fold vs nest**: one bullet of substance → fold inline (`- **[{PROJECT_KEY}-XXXX](...)** - description`); more than one → nest as a header with indented sub-bullets.
- Every ticket reference must be a markdown link: `[{PROJECT_KEY}-XXXX]({JIRA_SERVER}/browse/{PROJECT_KEY}-XXXX)`.
- **Code reviews** go in one plain `Code reviews` bullet with a nested line per PR: `Approved {author}'s [#N](url) (**KEY**, short outcome)`. A review is not a commit, so don't fold it under a ticket heading unless it is the user's own ticket.
- **Slack** items become a single short outcome bullet (e.g. "Raised X with the team in #channel"), never a transcript.

Write the drafted bullets into today's section (respecting the Step 1 append/replace choice) and show the user what was added.

## Step 4 — Quick ticket status sync (today's tickets only)

For only the tickets touched today (not the whole table), check current status via `jira issue view {KEY} --plain`. If it differs from the **This Weeks Tickets** table, update the table and mention the change. Skip tickets not touched today — full sync is the weekly skill's job.

## Step 5 — Summary

Briefly confirm to the user:

- What was written into today's entry
- Any ticket status changes made
- Reviews logged, and anything skipped: dismissed reviews, ambiguous Slack/DM threads, so the user can confirm or add them
- Any items left unresolved because they were too vague to draft (so they know what to clarify before Friday's wrap-up)

## Guidelines

- **Obsidian CLI first** for vault reads/writes (`obsidian vault="${user_config.vault_name}" ...`) — fall back to Read/Edit only if CLI fails
- **Do not fabricate detail** — if there's no commit/note to support a bullet, ask rather than invent one
- **Don't touch other sections** — this skill only writes today's daily entry (and, narrowly, today's ticket statuses). Leave Achievements, Goals, Brain Dump, AI-free Reflection, and next week's seeding alone; that's the `weekly-work-wrap` skill's job
- **Formatting** — no blank lines between list items, no trailing `-` after a ticket subheading
