---
name: compact-notes
description: Condense, tidy or summarise notes in place — a whole note, one section of it, or pasted text. Use when asked to compact, condense, shorten, clean up or summarise meeting notes or a transcription-tool paste. Keeps decisions, owners, numbers, ticket keys and open questions; drops filler and paste noise. Drafts first, writes only on confirmation.
argument-hint: "<file> [instructions] [--section \"Heading\"] [--keep-original] [--dry-run]"
---

Condense a note, or one section of it, in place. Callers bring their own shape; the rules below are the defaults.

## Configuration

Resolve the vault (`vault_path`) and team context (`team_context_file`) per `${CLAUDE_PLUGIN_ROOT}/reference/config.md`. The vault name for `obsidian vault="..."` is the last segment of the vault path. Read and write notes via the Obsidian CLI; fall back to Read/Edit only if the CLI fails.

## Arguments

| Argument | Does |
|---|---|
| `<file>` | Absolute path, or relative to the vault root. A bare name matching several notes: ask which |
| Instructions | Free text after the path that steers the run ("focus on decisions", "group by ticket", "shorter"). Overrides the defaults below |
| `--section "Heading"` | Compact only that section, up to the next heading of the same or higher level |
| `--keep-original` | Keep the source under `## Original notes` at the bottom |
| `--dry-run` | Draft only. Never offer to write |

No file but text in the message: compact the text and show it. Nothing to write.

## Finding the source

- With `--section`: the source is that section's body. The heading line stays.
- Otherwise: from the note's only H1 to the end of the file or the next H1. No H1: the body after the frontmatter.
- Frontmatter and `%% … %%` hints are never source.
- Frontmatter has `compacted:`, or the body already looks compact: say so and ask before running. There is no original to go back to.

## Refining

Each refinement ("shorter", "you dropped X") re-runs on the original source, not the previous draft, until the source is overwritten.

## Keep

- Decisions and their reasons. Proposals are marked as not decided
- Owners and next steps, under their topic. `(?)` when nobody was named
- Numbers, dates that matter later, ticket keys (`PROJ-123`)
- Open questions and disagreements
- Blockers and risks

## Drop

- Small talk, repetition, filler
- A generated "next steps" block that only repeats the bullets above
- Transcript links and transcript sections

## Clean up the paste

- Remove paste-time timestamps and date headers. Keep dates that are content, like deadlines
- Remove runs of blank lines, blank lines inside lists, empty bullets and empty headings
- Remove tool footers and UI text
- One bullet marker, one indent style
- Section-heading names are content, and so are the people's names a source attaches to a heading

## Fidelity

- Never invent a decision, owner or detail.
- Fix names and ticket keys that speech-to-text clearly mangled, using team context: the team note, else the roster from Jira. Names not found there keep `(?)`.
- Anything else unclear: write it as heard and flag `(?)`.

## Default shape

- Keep the source H1 as the title.
- `##` sections by topic, not speaker, unless the note is per-person by nature.
- Tight bullets. No separate Actions or Blockers sections; they sit under their topic.
- Aim for a third to half of the source length.

## Workflow

1. Read the note and find the source.
2. Draft. Show it in the terminal with line counts before and after.
3. Refine on request (see Refining).
4. `--dry-run`: stop here.
5. Ask to write, saying the original will be removed (or kept under `## Original notes` with `--keep-original`). Write only on a yes.
6. Write:
   - Replace only the source. With `--section`, the rest of the file stays byte-identical.
   - Set `updated` (today, `YYYY-MM-DD`) and `compacted` (today) in the frontmatter.
   - Remove any paste hint (`%% … %%`).
7. Verify the written note: one H1, no leftover transcript or paste hint, no double blank lines, a blank line before every table. Fix and re-check if any fail.
8. Report the path, line counts before and after, and `obsidian://open?vault={vault}&file={path, URL-encoded, no .md}`.

## When loaded by another skill

Another skill (e.g. `standup --after`, `dev-note --after`) may load this one; its rules then apply in the same conversation.

- The caller supplies the section (`--section`) and its shape as instructions. The caller's shape overrides the default shape; Keep, Drop, Clean up and Fidelity still apply.
- Produce the draft and ask nothing. Do not write.
- The calling skill owns the single confirmation and the write. If it then asks for the write, run steps 6–8.

## Rules

- Nothing is written without confirmation.
- `--dry-run` never offers to write.
- Never touch content outside the source.
