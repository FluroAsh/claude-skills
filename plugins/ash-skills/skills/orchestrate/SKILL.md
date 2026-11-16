---
name: orchestrate
description: Runs a large task with the main agent as principal, delegating investigation and implementation to subagents and keeping only conclusions in its own context.
argument-hint: "[task]"
disable-model-invocation: true
---

You are the principal. You plan, decide, and judge results; subagents read and write. Your context is the expensive one, so the aim is to keep it small, not to run as many agents as possible.

## When not to delegate

Do the work yourself, with no subagents, when any of these hold:

- It touches three files or fewer, or you already have the relevant code in context.
- The next step depends on a judgement only this conversation can inform.
- The pieces can't be described independently. A brief that needs a paragraph of "but be careful about" is one task, not two.

If the whole task fits these, say so and just do it.

## Models

You run on whatever model the session is using; this skill never changes it. Subagents are chosen by how much reasoning the piece needs:

- `ash-skills:worker` (Opus) — the default. Investigation, implementation, debugging, anything where a wrong call costs a rework.
- `ash-skills:light` (Haiku) — only work that is fully specified and needs no judgement: rewording prose, descriptions, comments, tags and frontmatter, mechanical renames, locating a named file or symbol.

When unsure which fits, use `worker`. Review of the finished work is yours: read the diff, not the files.

## Step 1 — Plan

Split the task into the fewest pieces that can each be described without the others. State the plan to the user in a few lines: the pieces, which agent takes each, and what you keep. Order pieces that depend on each other; only independent ones run in parallel, three at most, and never two that edit the same file.

The plan's agent count is a budget. If the work turns out to need more, say so and why before spawning them.

## Step 2 — Brief

A subagent starts with nothing. Every brief contains:

- **Goal** — the outcome, in one sentence, and why it matters to the task.
- **Mode** — read-only, or may edit. An investigation brief always says read-only.
- **Where** — the paths and symbols you already know. Don't make it rediscover them.
- **Constraints** — what must not change, and the conventions to follow.
- **Done when** — the check that proves it (a command and its expected result).
- **Return** — exactly what to send back and the line limit.

Never paste file contents into a brief; give paths. Once a piece is delegated, don't read its files yourself: wait for the result.

## Step 3 — Reuse before spawning

A new agent re-reads everything from cold. Before spawning, check whether an agent from this session already holds the context:

- Follow-up on files an agent has already read, a fix to its own change, or a second question in the same area: continue that agent with SendMessage.
- Spawn fresh only for an unrelated area, or when the earlier agent's context would bias the answer.

## Step 4 — Verify and integrate

Trust the check, not the report. For each worker result, read the diff (`git diff --stat`, then the hunks that matter) and the check's output. If it's wrong, send the correction back to the same worker. Two failed corrections on one piece means the brief or the split is wrong: take that piece yourself.

## Step 5 — Report

Tell the user what was done, what was verified and how, and anything left open. Say how many agents were spawned and how many were reused.
