---
name: weekly-work-log
description: Set up or update the weekly work log in the user's Obsidian vault.
---

Set up or update the weekly work log in the user's Obsidian vault.

Plugin config values below come from the user config; a blank value means "not configured".

## Configuration

- Vault: `${user_config.vault_name}`, rooted at `${user_config.vault_path}`
- Weekly logs: `${user_config.weekly_log_folder}/` (`{YEAR}` = four-digit year)
- File naming: `${user_config.log_filename_format}`, dated by the week's Monday
- Template note: `${user_config.weekly_log_template}`

## Environment

Resolved from the shell, not plugin config:

- Jira: the `jira` CLI's config (`~/.config/.jira/.config.yml`) supplies `{JIRA_SERVER}` (`server`), `{PROJECT_KEY}` (`project.key`) and `{BOARD_ID}` (`board.id`); `jira me` is the signed-in user; REST calls use `$JIRA_API_TOKEN`
- Ticket status: read from Jira at runtime (`jira issue view {KEY} --raw`, `fields.status.statusCategory.key`: `new`, `indeterminate` or `done`). A ticket is *finished* when its category is `done`, or its status says only release/deploy remains (e.g. "Pending Deploy", "Ready for Release")

## Step 1 — Identify the relevant files

Calculate the Monday of the current week and the Monday of the previous week based on today's date.
Derive the file paths for both weeks from the weekly logs folder and file naming above.
Read both files. If the current week's file does not exist, you will create it in Step 4.

## Step 2 — Audit and complete the previous week's log

Open the previous week's file and check each of the following. Fix anything that is incomplete before moving on:

- **Daily entries** — Monday through Friday must each have at least one bullet point of content. If a day is blank or only contains `-`, fill it in using context from other days, ticket notes, or standup notes. If no context exists, write `[no data]`.
- **Achievements → What** — must have at least one bullet describing what was shipped or completed.
- **Achievements → Impact & How** — must explain the impact and how it was achieved.
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

Fetch the active sprints on the board: `curl -s -u "$(jira me):$JIRA_API_TOKEN" "{JIRA_SERVER}/rest/agile/1.0/board/{BOARD_ID}/sprint?state=active"`. The board may also list other teams' sprints — use the active sprint that contains tickets assigned to the user, and ask if it's ambiguous. Its `goal` field is free text grouped by theme (e.g. performance, onboarding, reporting), not a ticket list.

Replace the sprint goals heading in the current week's log with:

```
#### [{Sprint name} Goals - ends {D Mon}]({JIRA_SERVER}/jira/software/c/projects/{PROJECT_KEY}/boards/{BOARD_ID})
```

Add a `[ ]` item only for goal lines that involve the user's work — check the sprint's tickets assigned to the user (`jira sprint list <sprint-id> --plain --columns KEY,SUMMARY,STATUS,ASSIGNEE`) and link the relevant ticket(s) on each item. Ask the user if it's unclear which goal lines apply. If a goal was already completed in a prior week's log, mark it `[x]`.

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
- Which sprint was matched and what the goals are
- Which action items were brought forward
