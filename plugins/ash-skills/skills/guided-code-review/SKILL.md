---
name: guided-code-review
description: Guided review of a GitHub PR from its URL. Gives a plain summary of what the PR does, a review map (affected app routes, environments, ticket, Confluence pages, API docs, files to read first), then runs Matt Pocock's two-axis code-review (Standards and Spec). Invoke it yourself; it never triggers on its own.
argument-hint: "<GitHub PR URL>"
disable-model-invocation: true
---

# Guided code review

The only input is a PR URL, such as `https://github.com/<owner>/<repo>/pull/<n>`. The output goes to the terminal in three parts, in this order:

1. **Summary**: what the PR does and why.
2. **Review map**: where the change lives in the running app, and the links and files a reviewer needs.
3. **Code review**: Matt Pocock's `code-review`, with Standards and Spec reported side by side.

This is read-only. Leave the PR alone: no comments, reviews, labels or pushes. Never check out a branch in any working checkout either.

## 1. Gather

**PR.** Run `gh pr view <url> --json title,body,headRefName,baseRefName,commits,files,additions,deletions`. Save `gh pr diff <url>` to the scratchpad. Diffs run to thousands of lines, so read them from the file in parts.

**Git refs.** Fetch into a bare repo under a private namespace. That way no working tree and no branch is touched. Use an existing bare mirror of the repo if you keep one (eg `~/workspaces/.mirrors/<repo>.git`):

```bash
M=<path to the bare mirror>
git -C $M fetch -q origin +refs/heads/<base>:refs/review/<N>/base +refs/pull/<N>/head:refs/review/<N>/head
```

If there is no mirror, make a blobless bare clone in the scratchpad (`git clone --bare --filter=blob:none`) and fetch the same refs into it.

Diff with `refs/review/<N>/base...refs/review/<N>/head`. Before going on, check that the file count matches the `files` list from `gh`. A stale base pulls in other people's merged work: a stale local `main` can turn a 37-file diff into hundreds.

**Ticket.** Take the Jira key from the PR title, branch or body. Fetch it through the Atlassian MCP (on the v2 connector, `view: "evidence"`), which returns the description, ACs, parent epic and issue links. Then fetch the epic's summary.

**Confluence.** Run one CQL search on the feature's nouns, the epic's theme and "test plan", for example `title ~ "activity log" OR title ~ "TIP 12"`. Keep the pages a reviewer would actually open: design or spike pages, the epic's plan, and test plans for the same area. An existing test plan is often the best checklist for "behaves the same as before".

## 2. Summary

Write it for a reviewer who hasn't seen the ticket:

- **In one line**: what the PR achieves, and the epic or larger effort it belongs to.
- **What changed**: numbered groups by concern (new library code, schemas, app callers moved over, code deleted, behaviour fixes). Each group names its main files in backticks.
- **What users notice**: concrete behaviour changes, or "nothing" when it is a pure refactor.
- **Why it matters**: what it unblocks (linked tickets) and what it removes.

Base every claim on the diff, the PR body or the ticket. If the PR body claims something the diff doesn't show, say so instead of repeating it.

## 3. Review map

Trace each changed component up to the page that renders it. The goal is a URL a reviewer can open.

- **Routes.** Learn the repo's routing convention from its `AGENTS.md` or router setup. With file-based pages (eg `apps/<app>/src/pages/`), tabs are often a query parameter whose key can differ per page, so read the page file for it rather than assuming `tab`. List each view as route, component, and the endpoints it calls.
- **What to check on each view**: one line per view naming the behaviour the PR changes there.
- **Environments.** Take base URLs from the team note (`team_context_file`, see `reference/config.md`), the repo's docs or your own notes. Say which environments still run the old code, since they are useful for comparing before and after. Give the PR preview URL if the app has one; otherwise say a local dev server or a deploy is needed.
- **Ticket and plans**: the PR, the ticket (note any QA label), the epic, linked or blocked tickets, and the Confluence pages from step 1.
- **API contract**: the OpenAPI links the code cites in `@see` tags, for each endpoint and schema the PR adds or changes.
- **Code to read first**: a table of about five to eight files, each with one line on why it matters. Include any shared default or config the change inherits silently, such as query defaults or an HTTP serializer.

Use `<companyUid>`-style placeholders for IDs. Say which links you didn't open.

## 4. Code review

Invoke `mattpocock-skills:code-review` with the Skill tool, passing the PR URL. Give it the fixed point and spec you already have:

- **Diff**: `refs/review/<N>/base...refs/review/<N>/head` in the mirror. Tell any sub-agent that exact command and to read files with `git show refs/review/<N>/head:<path>`.
- **Spec**: the Jira ticket from step 1.
- **Standards sources**: root and per-app or per-lib `AGENTS.md` and `CLAUDE.md`, plus `.claude/rules/*`. These may only exist on disk in a local checkout, not in git. If so, read them there and say so.

Use one sub-agent at most. Give the Standards axis to one background agent with the full brief and smell baseline, and do the Spec axis yourself while it runs. Report the two axes under separate headings, as the skill asks, and end with its one-line summary.

## 5. Humanize, then print

Before printing, run the prose from the Summary, the Review map and the Code review through this plugin's `humanizer` skill in embedded mode. If it isn't loaded, read `../humanizer/SKILL.md` and apply it. It changes prose only: code, paths, URLs, ticket keys and table data stay exactly as written. Check that no finding, file reference or number was lost in the rewrite.

Print the three parts under `# Summary`, `# Review map` and `# Code review`. End with one line on what you didn't check, for example "didn't run tests" or "links not opened". Then offer once to publish it as an Artifact page for sharing.
