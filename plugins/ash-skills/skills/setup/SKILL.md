---
name: setup
description: Set up or check the ash-skills config — discovers the vault, layout, templates and Jira values, asks only what's left, and stores everything it resolves. Run once after install, and again when the plugin adds a key or something moves. `--check` reports problems and changes nothing.
argument-hint: "[--check]"
disable-model-invocation: true
---

Configuration wizard for this plugin. Discovery does the work; the user answers only what's left. Read `${CLAUDE_PLUGIN_ROOT}/reference/config.md` first: its resolution order, layout and discovery tables apply here and aren't repeated.

With `--check`, run Steps 1–3 and then Check mode only. Nothing is saved.

## Step 1 — Read stored values

Run `claude plugin configure ash-skills@ash-skills --json` (read-only). It returns `schema` (the keys the plugin defines), `inputs` (stored values; a `multiple` key comes back as one comma-separated string), `choices`, `configured` and `unconfigured`. Use this, not `${user_config.*}` substitution.

If it fails with "No installed plugin has the id", the plugin was loaded with `--plugin-dir`. Say so, treat every key as unset, and carry on: discovery and the table still work, but nothing can be saved until the plugin is installed.

## Step 2 — Resolve every key

For every key in `schema`, resolve the value per config.md and record its source: `stored`, `convention`, `environment` or `not found`. Note every candidate when there are several (vaults, `Dev/` folders, Jira sites, team notes).

- Resolve the vault path first; every layout path depends on it.
- Layout paths: confirm each folder or template exists in the vault. For `log_filename_format`, infer from existing logs.
- Jira (Atlassian MCP): site, project key, and the story points field id from field metadata. If the MCP isn't connected, mark these `not found` and say so.
- Tier 1 (`review_context_files`, `company_name`, `sunsama_channel`): stored value, else propose (company from the Jira subdomain, channels listed by the Sunsama MCP), else `not found`.

## Step 3 — Show the table

One table, every key in `schema` order: key, value, source. Mark anything missing or ambiguous. Show it before asking anything.

## Step 4 — Ask what's left

Ask one question at a time, only about values that are missing, ambiguous, or a Tier 1 choice. Offer picks where there's a list (vaults, folders, Sunsama channels). Every Tier 1 question can be skipped; a skipped key is saved as `""`, so `--check` treats it as answered. Ask nothing about a value resolved unambiguously.

For a missing folder or template, offer to leave it blank (the skills then ask when they need it) or take a path from the user.

## Step 5 — Confirm

Store every resolved value, including layout paths that match the convention and the Jira values. Show two lists, **Will save** (key: new value, with the old value if it changes) and **Will clear** (keys the user asked to blank), and ask to confirm. Skip keys whose stored value already matches. If nothing changes, say so and stop.

If Step 1 failed, show the lists, say they can't be saved until the plugin is installed, and stop.

## Step 6 — Save

Pipe a JSON object to `claude plugin configure ash-skills@ash-skills --values-stdin`:

- Only keys being changed; keys left out keep their values.
- Every value a single-line string. A `multiple` key is one comma-separated string. `""` clears a key.
- Only keys in `schema`: an undefined key is rejected.
- Never edit `settings.json` directly.

On an error, show it and stop. Don't retry with a different payload.

## Step 7 — Finish

Tell the user: restart Claude Code for the saved values to apply. Until then, other skills in this session still see the old values (or discovery, where a key was unset).

## Check mode

Read-only: never save, never ask to fix. After Steps 1–3, list each problem with its fix:

| Problem | Fix |
|---|---|
| A stored or discovered folder or note path that doesn't exist | Rerun `/ash-skills:setup`, or `/plugin configure ash-skills@ash-skills` |
| A template that can't be found | Rerun `/ash-skills:setup` |
| A key in `schema` with no stored value (in `unconfigured`) | Rerun `/ash-skills:setup` to store it |
| A stored key the plugin no longer defines (in `inputs`, not in `schema`, e.g. `vault_name`) | Harmless to the skills. The CLI can't clear it; remove it from the plugin's options in Claude Code's settings if it causes a warning |
| Atlassian MCP not connected | Connect it, then rerun `/ash-skills:setup` for the Jira values |

If Step 1 failed, say stored values couldn't be read and report only discovery problems. If nothing is wrong, say so in one line.
