---
name: create-pr
description: Creates or updates a GitHub pull request via gh with a brief generated description. Use when the user wants to open a PR, create a pull request, push and open a PR, or refresh an existing PR's description.
---

Open a GitHub pull request for the current branch, or update the one that already exists.

## Environment

- GitHub: `gh`, signed in. Stop and say so if it isn't
- Jira and Confluence: an Atlassian MCP server, if connected. `{JIRA_SERVER}` is `https://` plus `${user_config.jira_site}`, else the site the MCP reports. Tool names vary by server, so the steps name the capability and give a tool name as an example. Without it, leave the ticket as a bare key with no link and skip the Jira and Confluence lookups in Step 1a

## Step 1 — Gather context

1. Base branch: the one the user names, otherwise `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`.
2. `git fetch origin {base}`, then `git log origin/{base}..HEAD --oneline` and `git diff origin/{base}...HEAD --stat`, so the description matches what GitHub will compare against. Read the diff itself only where the commits don't explain the change.
3. `gh pr view --json url,title,body` — if a PR already exists for this branch, update it in Step 4 instead of creating one.
4. Ticket id: taken from the branch name (e.g. `feature/PROJ-123-add-trending-badge`) or given by the user. Never invent one or use a placeholder (`PROJ-xxxxx`, `NO-TICKET`, `N/A`).

## Step 1a — Extra context, only when the description needs it

The commits and diff are the default source. Reach for Jira, Confluence or other PRs only when one of these holds, and skip this step entirely otherwise:

- **The intent isn't clear from the commits and diff** — read the ticket (get issue, e.g. `getJiraIssue`). This is the one lookup worth making for most ticketed work that isn't self-explanatory; a typo fix or dependency bump doesn't need it.
- **The ticket, commits or branch reference another ticket** (a blocker, dependency, parent epic or follow-up) and the description has to explain that relationship — read that ticket too. One hop only: don't follow the tickets it links to.
- **The change is stacked on, depends on, or revisits an earlier PR** — `gh pr view {number|branch} --json title,body,url,state`; to find past PRs for the same ticket, `gh pr list --state all --search "{TICKET}" --json number,title,url,state`.
- **The ticket points to a Confluence page that defines the behaviour being implemented** (a spec or design doc, not a general wiki link) — read that page (e.g. `getConfluencePage`), and take only the section that applies.

Use what you read to sharpen the one-line summary and the bullets, and to link related tickets and PRs. Don't paste ticket or page content into the body. If the Atlassian MCP isn't connected, carry on without it.

## Step 2 — Title

Match the repo's own convention: read `gh pr list --state merged --limit 5 --json title` and follow the shape those titles share (conventional-commit prefix, ticket prefix, casing). With no history to go on, use `{TICKET}: {Summary}` when there is a ticket and a plain summary when there isn't.

## Step 3 — Body

If the repo has a PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, or `pull_request_template.md` at the root or in `docs/`), fill that in and keep its headings. Otherwise use:

```markdown
### [{TICKET}]({JIRA_SERVER}/browse/{TICKET})

{One sentence: the intent of the change.}

### What changed

- {2–4 bullets at feature or area level}

### Notes

{Only non-obvious engineering context: an environment caveat, a side effect, a migration step.}
```

- Omit the ticket heading when there is no ticket (use the bare key as the heading when the Jira site isn't known), and `### Notes` when there is nothing to put in it.
- Brevity is the priority. A large diff does not justify more bullets: group related changes, and don't list files, helpers or sub-components unless one matters to the reviewer on its own.
- Leave out test additions unless tests are the deliverable or encode behaviour the reviewer must know. No QA steps, test plans or verification checklists.
- Add a `### Behaviour` section (one small Mermaid chart or table) only when branching rules or config mappings would otherwise take several sentences. Check it against the code; if unsure, leave it out.
- Use diagrams sparingly, and only where one makes the PR easier to review: an architecture change, or a user or data flow across several steps. GitHub renders Mermaid natively, so check the chart on the PR after publishing. If its lines tangle (the same check repeated for each way in, say), a table reads better.
- When the change replaces legacy behaviour, a table with a column for each side can show the difference at a glance, with ✅ and ❌ marking what each one does:

  | Scenario | Legacy | New |
  | --- | --- | --- |
  | {what the user does} | ❌ {what happened} | ✅ {what happens now} |
- Stacked PR (the base is another feature branch): link the parent PR, found with `gh pr list --head {base} --json url`, not the branch.
- Screenshots: `gh` cannot upload images. For a visual change, add an empty `### Screenshots` heading and tell the user to drag the images into the PR on GitHub.
- Say "legacy" for the page, flow or behaviour being replaced, never "old", and "new" or "redesigned" for what replaces it.
- Domain terms: if a glossary skill for the company's domain is installed, use product and domain terms as it defines them.

## Step 4 — Create or update

Write the body to a temp file, and pass the title in single quotes (escaping any `'` in it), so backticks and `$(...)` in either are never run by the shell.

When updating, keep any section of the existing body the new one doesn't cover (screenshots, reviewer notes).

```bash
git push -u origin HEAD                 # only when the branch has no upstream or is ahead of it
gh pr create --base {base} --title '{title}' --body-file {file}     # add --draft when asked
gh pr edit --base {base} --title '{title}' --body-file {file}       # when a PR already exists
```

Reply with the PR URL and the title used.
