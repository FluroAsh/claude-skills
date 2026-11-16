---
name: weekly-work-log
description: Set up or update the weekly work log in the user's Obsidian vault.
---

Set up or update the weekly work log in the user's Obsidian vault.

## Configuration

Read `${CLAUDE_PLUGIN_ROOT}/reference/config.md` once at the start of the run: it gives the resolution order (stored value, else convention, else ask once and suggest `/ash-skills:setup`). Paths are vault-relative.

- Vault: `${user_config.vault_path}` (`vault_path`; else Obsidian's vault registry). `{VAULT_NAME}` is its last path segment
- Weekly logs: `${user_config.weekly_log_folder}/` (`weekly_log_folder`; else `10 - Meetings/Weekly Work Logs/{YEAR}/`, `{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}` (`log_filename_format`; else inferred from existing logs, `MM-DD-YY.md` if none), dated by the week's Monday
- Template note: `${user_config.weekly_log_template}` (`weekly_log_template`; else `Weekly Work Log` in the templates folder)

## Environment

Resolved at runtime, not plugin config:

- Jira: the Atlassian MCP (see config.md). `{JIRA_SERVER}` is `https://` plus `${user_config.jira_site}` and `{PROJECT_KEY}` is `${user_config.jira_project}`; if unset, take them from the MCP. If the MCP isn't connected, say so and skip the Jira steps
- Ticket status: read from Jira at runtime (get issue, e.g. `getJiraIssue`, `fields.status.statusCategory.key`: `new`, `indeterminate` or `done`). A ticket is *finished* when its category is `done`, or its status says only release/deploy remains (e.g. "Pending Deploy", "Ready for Release")

## Step 1 — Identify the relevant files

Calculate the Monday of the current week and the Monday of the previous week based on today's date.
Derive the file paths for both weeks from the weekly logs folder and file naming above.
Read both files. If the current week's file does not exist, you will create it in Step 4.

## Step 2 — Audit and complete the previous week's log

Open the previous week's file and check each of the following. Fix anything that is incomplete before moving on:

- **Daily entries** — Monday through Friday must each have at least one bullet point of content. If a day is blank or only contains `-`, fill it in using context from other days, ticket notes, or standup notes. If no context exists, write `[no data]`.
- **Achievements → Delivery** — must have at least one bullet describing what was shipped or progressed and why it mattered.
- **Achievements → Craft** and **Achievements → Influence** — must each have at least one bullet where the daily entries support it; otherwise write `[no data]`.
- **Brain Dump** — must have at least one real entry (not the template placeholder). Brain Dump is for reflections, observations, patterns, hypotheses, and architectural thoughts — **not a recap of Achievements**. If a point is already covered in Achievements, it must not appear in Brain Dump. The two sections should be entirely non-overlapping: Achievements = what was done and its impact (factual); Brain Dump = the analytical/reflective layer on top of that.

Note: there is no "Goals for Next Week" section — carry-over goals are captured in the current week's **Goals for this week** (Step 6) instead.

Do not fabricate detail. Use `[no data]` where context is genuinely unavailable.
Once complete, treat the previous week as read-only — do not edit it further.

## Step 3 — Identify incomplete tickets

From the previous week's **This Weeks Tickets** table, identify every ticket that is **not** in a finished status (see Ticket status in Environment).

Note the Code, Name, current Status, and any active Blockers for each incomplete ticket.

Also review the previous week's **Action Items** section and identify any that are unresolved.

## Step 4 — Set up the current week's log

If the current week's file does not exist, create it using the template note above. Save it to the correct year folder.

If it already exists, open it and work with the existing content.

## Step 5 — Fill out Sprint Goals

Find the active sprint from the sprint field on the user's sprint tickets (JQL search: `sprint in openSprints() AND assignee = currentUser()`): its id, name, end date, `goal` and board id (`{BOARD_ID}`). If the user's tickets sit in more than one active sprint, ask which. The `goal` field is free text grouped by theme (e.g. performance, onboarding, reporting), not a ticket list. If no goal comes back, leave Sprint Goals as the template has it for the user to fill, say so, and continue with Step 6.

Replace the sprint goals heading in the current week's log with:

```
#### [{Sprint name} Goals - ends {D Mon}]({JIRA_SERVER}/jira/software/c/projects/{PROJECT_KEY}/boards/{BOARD_ID})
```

Add a `[ ]` item only for goal lines that involve the user's work — check the sprint's tickets assigned to the user (JQL search: `sprint = {sprint-id} AND assignee = currentUser()`) and link the relevant ticket(s) on each item. Ask the user if it's unclear which goal lines apply. If a goal was already completed in a prior week's log, mark it `[x]`.

## Step 6 — Populate Goals for this week

Under **Goals for this week**, add:

1. Each carried-over incomplete ticket as a `[ ]` item (use the ticket name, not just the ID)
2. Any sprint goal tickets not already listed

Exclude any ticket in a finished status — there's no action left to take on it this week, so it doesn't belong as a goal. Continue tracking it in **This Weeks Tickets**. The same exclusion applies to the Sprint Goals checklist (Step 5): a ticket in a finished status should be marked `[x]` there (dev work is done) rather than left as an open `[ ]` goal.

Remove template placeholder text.

## Step 7 — Populate This Weeks Tickets table

Add a row for each carried-over ticket with its Code, Name, and current Status from Step 3. Clear the Blockers column unless a blocker is still known to be active.

## Step 8 — Carry over Action Items

Under **Action Items**, add any unresolved action items identified in Step 3. Do not duplicate items that are already resolved. Remove the template `...` placeholder.

## Step 9 — Save and confirm

Write the updated current week's file. Then summarise what was done:

- Whether the previous week needed any fixes and what was filled in
- Which tickets were carried over
- Which sprint was matched and what the goals are, or that Sprint Goals was left for the user because no goal came back
- Which action items were brought forward
