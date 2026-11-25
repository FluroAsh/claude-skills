---
name: create-pr
description: Creates or updates a GitHub pull request via gh, with a concise description written for the reviewer - plain-English prose, tables or a diagram only where they make the change easier to see, and the current state only. Use when the user wants to open a PR, create a pull request, push and open a PR, or refresh or tidy up an existing PR's description.
---

Open a GitHub pull request for the current branch, or update the one that already exists.

The description is for a reviewer who knows the codebase and has the diff open: usually a frontend engineer or QA, sometimes a backend engineer when the change touches an API or contract. Write for that one reader; don't address sections to other audiences. Its job is to tell them what changed in behaviour, why, and what to look at closely. The diff already shows which files changed and how.

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

Use what you read to sharpen the summary and the bullets, and to link related tickets and PRs. Don't paste ticket or page content into the body. If the Atlassian MCP isn't connected, carry on without it.

## Step 2 — Title

Match the repo's own convention: read `gh pr list --state merged --limit 5 --json title` and follow the shape those titles share (conventional-commit prefix, ticket prefix, casing). With no history to go on, use `{TICKET}: {Summary}` when there is a ticket and a plain summary when there isn't.

## Step 3 — Body

The repo's PR template is the base every description is built on; this skill's sections and examples shape what goes inside it, with your own judgement for the rest. If the repo has a PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, or `pull_request_template.md` at the root or in `docs/`), fill that in and keep all its headings, even ones with nothing to add (answer them in a few words, e.g. "No visual change", or leave their checkboxes). Replace its italic placeholder hints rather than keeping them, and where a hint conflicts with these rules (e.g. "list the commits"), these rules win. The ticket heading and the sections below go first under its description heading. Otherwise use them as they are:

```markdown
### [{TICKET}]({JIRA_SERVER}/browse/{TICKET})

{One or two sentences: the problem, and what is true once this merges.}

### What changed

- **{The behaviour that changed, in plain words.}** {At most two short sentences: where it lives if that isn't obvious, and why.}

### Worth a close look

- **{The risky or subtle part, in plain words.}** {Where it lives (one component or function name), and the edge case to check.}

### Notes

{Only non-obvious engineering context: an environment caveat, a side effect, a migration step. Optional.}
```

Everything the skill adds sits under the template's description heading, in this order: ticket heading, summary, What changed, Worth a close look, the optional sections below, Notes, then the collapsed complementary material. The template's other headings follow as the template has them.

**Worth a close look** is what replaces a file list: 1–3 bullets that send the reviewer to where the risk is (timing, a shared API, an edge case the tests lean on). Name just enough code to find it. Leave it out for a change with nothing subtle in it.

Optional sections, each only when it earns its place, in this order after **Worth a close look**:

- **Impact** (name it for what's affected, e.g. "Analytics impact"): keep it visible, since QA tests from it. A table, when the change alters what other people see or rely on (UI states, analytics, an API, config) across several cases. One row per case, with Before and After columns against the base branch.
- **Decisions**: the calls a reviewer might question, as a table (`Decision | Why`), one short line of reasoning each. Not every choice made while building. Rationale isn't something to test, so it usually belongs in the collapsed block at the end; keep it visible only when the PR is mainly a design choice.
- **Testing**: one or two sentences on what the tests prove and anything checked by hand, and where. When the template has a testing section, this goes there instead, under its checkboxes, and not under the description too.
- **Complementary material** last, in a collapsed `<details>` with a plain summary line named for its content ("Edge cases and follow-ups"), not for an audience: out of scope, follow-ups, and secondary detail. It's there for whoever wants it but isn't the first thing a reviewer reads.

### Match the shape to the PR

Before drafting, read the closest example in `examples/` (indexed in `examples/README.md`) and take its shape. A small fix needs two sentences; don't add sections because this skill or the template lists them. Screenshots are the exception to keeping it short: whatever the type, a change that shows on screen gets them as evidence.

| PR type | Usually needs |
| --- | --- |
| Small fix | The summary and one bullet, plus before/after screenshots when the fix shows on screen |
| Feature behind a flag | A flag callout, What changed, Worth a close look, screenshots |
| Change others rely on (analytics, events, permissions, data) | A callout on the effect, What changed, a visible impact table |
| Refactor | What stays the same and how that's proven; any place the old copies had drifted |
| Dependency upgrade or security bump | The behaviour differences and what was held back; a bare bump is one sentence |
| CI, build or dev tooling | What changes for developers, how it was checked, how to roll back |
| SDK, API client or contract | A stack note when stacked, a contract table a backend reviewer can check |
| Removing a flag, dead code or a legacy path | Why it's safe now, and the merge precondition as a callout |

Risk facts go up front when they exist, as one callout line each rather than a section: a feature flag and where it's on, a merge precondition or ordering, how to roll back.

### Writing rules

- **Plain English first.** Short sentences, one idea each, in the active voice: "The booking now saves once the guest picks a date", not "`saveDraft`, run by a watcher on `selectedDate`, saves…". Code names go in backticks where the reviewer needs to recognise them, never as a chain of clauses.
- **Guide by change, not by file.** Lead each bullet with the behaviour, then work where it lives into the sentence if that isn't obvious ("…, handled in the checkout page"), rather than tacking on "Lives in `File.vue`". No "Where to look" or file-by-file lists, and no file names in testing notes. Assume the reviewer knows the codebase.
- **Explain the why, not the mechanics.** Leave out how the code does it (watchers, getters, which helper computes a flag, refactors in passing) unless that mechanism is what needs reviewing. Then name it once, in one sentence; a new option on a shared API is a fair example ("`useCheckout` takes an optional `onRetry`, so other callers are unchanged").
- **Define a term once,** before or where it's first used (never in a later section), and use the same word every time after.
- **Brevity over completeness.** A large diff does not justify more bullets: group related changes. 2–5 bullets is normal. One point per paragraph.
- **Tables and diagrams only where they help.** A table for three or more parallel cases (before/after, options, mappings). A small Mermaid chart only for a flow or state change that would take a paragraph to describe, and only if it shows every branch the reviewer has to check; a happy-path-only diagram hides the cases that matter. Never both for the same content, and never forced onto a simple change. Check either against the code; if unsure, leave it out.
- **Callouts for emphasis, sparingly.** A GitHub alert (`> [!IMPORTANT]`, `> [!WARNING]`, `> [!NOTE]`) for the one or two things a reviewer must not miss: a behaviour change others rely on, a deploy or data caveat, a merge dependency. Put it straight after the summary, in one or two sentences. Never for routine content, and never more than two.
- **Emojis as signposts, not decoration.** One on a section heading can help a reviewer scan (🔍 Worth a close look, 📊 Impact, ⚖️ Decisions). None in bullets, table cells or prose, and leave the repo template's own headings as they are.
- **No test file lists, QA scripts or verification checklists.** Testing notes say what is covered, not how to rerun it.
- Omit the ticket heading when there is no ticket (use the bare key as the heading when the Jira site isn't known), and any of this skill's sections with nothing in it. A template's own headings stay.
- Stacked PR (the base is another feature branch): link the parent PR, found with `gh pr list --head {base} --json url`, not the branch.
- **Screenshots are evidence.** Any change a user can see gets them, bug fixes and copy changes included: before and after for a fix or a changed screen, each state for a feature (flag on and off, empty, error). A one-line caption under each says what to look at. They're the reviewer's and QA's visual reference, so short descriptions still carry them. Only a change with nothing on screen (logic, analytics, CI, types, tests) says "No visual change".
- `gh` cannot upload images. If a screenshot skill is installed, use it to capture and attach them; otherwise leave the screenshots heading in place (the template's, or a `### Screenshots` you add) with the captions as placeholders, and tell the user which shots to drag in on GitHub.
- Domain terms: if a glossary skill for the company's domain is installed, use product and domain terms as it defines them.

## Step 3a — Critical pass

Before writing anything to GitHub, reread the draft as the reviewer would, cold, and fix it:

1. **Could someone outside this conversation follow it?** Remove context only the author has: review history, earlier attempts, and wording that compares against an earlier revision of the PR ("now uses `whenever`", "after review"). Describing how behaviour differs from the base branch ("no longer sends…") is the point of the PR and stays.
2. **Is every sentence current?** It describes the branch as it is. A fixed review finding, a reverted approach or a superseded decision is deleted, not marked as changed. That includes test notes ("rather than a mock") that only make sense against an earlier revision.
3. **Is every sentence needed?** If the diff, the ticket or the title already says it, cut it. If a paragraph makes several points, split it or cut it down to the one that matters.
4. **Does it read cleanly aloud?** Rewrite any sentence with nested clauses, a run of code names, or a subject the reader has to hunt for.
5. **Is the format right?** A paragraph listing parallel cases becomes a table. A table with one row becomes a sentence. A diagram that repeats the bullets goes.

## Step 3b — Humanizer pass

After Step 3a, run the prose (summary, bullets, callouts, table cells, Testing and Notes) through `ash-skills:humanizer` in embedded mode. It rewrites wording; it never decides what goes in. Where it conflicts with this skill, this skill wins:

- **Register:** technical and neutral. No opinions or asides, and no detail the diff, commits or ticket don't support.
- **Leave as written:** headings and their one emoji, alert markers (`> [!NOTE]`), the bold lead of a What changed or Worth a close look bullet, one short informative bold label (**Flag:**, **Held back:**; "Heads up:" goes), a bold defined term, code, links, ticket keys, event and property names, numbers (a range like 1–100 keeps its dash) and table structure.
- **Contrasts:** keep a not-X-but-Y when the negative half is the base branch's behaviour ("once per load, not per keystroke") or corrects an assumption (`abandoned` read as a drop-off). Rewrite one that only adds weight.
- **No cutting:** Step 3a decides what stays. Cut only a closing line that repeats the bullet above it.

Then check that no number, name, flag, event, before/after value or risk fact changed, and restore any that did. When updating, cover only sections this skill rewrote, not ones someone else added.

## Step 4 — Create or update

Write the body to a temp file, and pass the title in single quotes (escaping any `'` in it), so backticks and `$(...)` in either are never run by the shell.

**Updating rewrites the description to the current state.** Write the sections this skill owns afresh from the diff and commits, as if no description existed, then mine the old body only for facts the diff can't show (manual testing, decisions and their reasons, links, terms the team already uses). Don't paraphrase its sentences or keep its layout because it was there, and don't append to it or patch one line. Run Steps 3a and 3b on the whole result. Keep a section someone else added (screenshots, reviewer notes, a bot's summary) only while it's still true.

```bash
git push -u origin HEAD                 # only when the branch has no upstream or is ahead of it
gh pr create --base {base} --title '{title}' --body-file {file}     # add --draft when asked
gh pr edit --base {base} --title '{title}' --body-file {file}       # when a PR already exists
```

Reply with the PR URL and the title used.
