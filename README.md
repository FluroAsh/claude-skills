# ash-skills

A [Claude Code](https://code.claude.com/docs/en/overview) plugin with skills for keeping a weekly work log in Obsidian, and preparing standups. The vault, folders, templates and Jira details are found on disk or through tools you already have connected, so the skills aren't tied to one person or employer.

The repo is public. It's built mainly for my own use and shared as-is.

## Quick start

From inside Claude Code:

```
/plugin marketplace add FluroAsh/claude-skills
/plugin install ash-skills@ash-skills
/ash-skills:setup
```

`setup` finds what it can, asks about the rest and stores the result. Restart Claude Code, then try `/ash-skills:standup`. It only reads, so it's safe to run first.

If these skills already exist as loose files in `~/.claude/skills` or `~/.claude/commands`, remove them, or each one shows up twice.

## Skills

| Skill | What it does |
|---|---|
| `setup` | Finds and stores the plugin's config, asking only what it can't discover. `--check` reports problems and changes nothing. Invoke it yourself; it never triggers on its own |
| `weekly-work-log` | Audits last week's log, then sets up this week's |
| `weekly-work-wrap` | End-of-week wrap-up of the current log, with an optional Tech Lead Review |
| `daily-work-wrap` | Single-day catch-up for days you forgot to log |
| `standup` | Standup prep. Read-only, chat output only. |

Invoke skills namespaced, eg: `/ash-skills:standup`.

## Dependencies

| Name | Required | Used by | Without it |
|---|---|---|---|
| [Claude Code](https://code.claude.com/docs/en/overview) | Required | All | Nothing runs |
| [Obsidian](https://obsidian.md) and its [CLI](https://obsidian.md/help/cli) | Required | All | Vault skills can't read or write notes. Turn on **Settings → General → Command line interface** |
| git, with `user.name` set | Required | Work-log skills, `standup` | Commits can't be matched to you |
| Atlassian MCP server (Jira, Confluence) | Required for Jira steps | Work-log skills, `standup`, `setup` | A skill that needs ticket status says so and skips that step. No CLI or API token is used |
| [GitHub CLI](https://cli.github.com) (`gh`), signed in | Optional | Work-log skills, `standup` | PR and review lookups are skipped |
| Slack MCP server | Optional | `daily-work-wrap`, `weekly-work-wrap`, `standup` | Slack signal is skipped |
| [Sunsama](https://www.sunsama.com) MCP server | Optional | Work-log skills, `standup`, `setup` | Skills work from git and your own input. It needs to expose `sunsama://tasks/{date}` and `sunsama://calendar/events/{date}` |

## Configuration

Every value is resolved the same way: a stored value wins, else it's discovered, else the skill asks one question and suggests `/ash-skills:setup`. `setup` stores everything it resolves, so you run it once and again only when the plugin adds a key or something moves. The full rules are in [`plugins/ash-skills/reference/config.md`](plugins/ash-skills/reference/config.md).

Stored values live locally on each machine. Change one with `/plugin configure ash-skills@ash-skills`, then restart Claude Code for it to apply.

### Conventional vault layout

Paths are relative to the vault root. A missing convention path falls back to a search for a folder with the same final name.

| Location | Convention |
|---|---|
| Templates | `00 - System/Templates/`, or the `folder` in `.obsidian/templates.json` |
| Weekly logs | `10 - Meetings/Weekly Work Logs/{YEAR}/`, files `MM-DD-YY.md` dated by the week's Monday |
| Standups | `10 - Meetings/<anything> Standup/`, or `10 - Meetings/Standup/` |
| Dev notes | `20 - Projects/**/Dev/`, one note per ticket |
| Team note | A vault-root note whose name ends in `Team` or `Squad` |

The vault itself comes from Obsidian's vault registry; with several vaults registered, you're asked which.

### Keys

None is required. Blank means the convention or discovery is used. In the examples, replace anything in `<angle brackets>` with your own value. Anything in `{braces}`, and the `MM`, `DD` and `YY` letters, is typed exactly as shown and filled in by the skills.

**Preferences**

| Key | Meaning | Blank means |
|---|---|---|
| `review_context_files` | Notes describing your career goals, growth areas or role expectations, vault-relative or absolute (one or more). The Tech Lead Review measures your week against them | Review off |
| `company_name` | Company the Tech Lead Review is written for, eg: `Acme` | Proposed from the Jira site (`acme.atlassian.net` gives `Acme`) |
| `sunsama_channel` | Sunsama channel for tasks the skills create | Ask, or create without a channel |

**Layout overrides**

| Key | Meaning | Blank means |
|---|---|---|
| `vault_path` | Absolute path to the vault root, eg: `/Users/<username>/Documents/Obsidian/<vault>`. The vault name is its last folder | Obsidian's vault registry |
| `weekly_log_folder` | Folder for weekly logs, eg: `<folder>/Weekly Work Logs/{YEAR}` | `10 - Meetings/Weekly Work Logs/{YEAR}` |
| `log_filename_format` | Filename for a week's log: `MM` month, `DD` day, `YY` two-digit year, so `MM-DD-YY.md` gives `03-16-26.md` | Matches existing logs, else `MM-DD-YY.md` |
| `weekly_log_template` | Template note for a new week's log | `Weekly Work Log` in the templates folder |
| `standup_folder` | Folder for standup notes | A folder ending in `Standup` under `10 - Meetings` |
| `standup_template` | Template note for a standup | `Standup Template` in the templates folder |
| `dev_note_folder` | Folder for dev notes | The `Dev` folder under `20 - Projects` (asked if there are several) |
| `dev_note_template` | Template note for a dev note | `Development Template` in the templates folder |
| `team_context_file` | Note listing teammates' names, roles and standup order | A vault-root note ending in `Team` or `Squad`, else names built from Jira, with no standup order |

**Jira values, stored by `setup`**

| Key | Meaning | Blank means |
|---|---|---|
| `jira_site` | Jira site host, eg: `<company>.atlassian.net` | The site the Atlassian MCP reports |
| `jira_project` | Your team's project key, eg: `PROJ` | The key most of your open sprint tickets share |
| `story_points_field` | Story points custom field id, eg: `customfield_<number>` | Found by name in Jira's field metadata |

The Tech Lead Review is an optional closing section of `weekly-work-wrap`: a short, critical read of your week, written as a tech lead at your company, ending with one thing to try next week.

## Weekly log template

The skills expect your template to have these sections. They don't create it for you.

- Monday to Friday daily entries
- Goals for this week
- Sprint Goals
- This Weeks Tickets (a table with Code, Name, Status and Blockers columns)
- Action Items
- Achievements, with Delivery, Craft and Influence subsections
- Brain Dump
- AI-free Reflection

## Updating and local testing

To ship a change, bump `version` in `plugins/ash-skills/.claude-plugin/plugin.json`, push, then run `/plugin marketplace update ash-skills` on each machine. Without a version bump, installed copies may not update.

To test local changes without pushing:

```bash
claude --plugin-dir ./plugins/ash-skills
claude plugin validate ./plugins/ash-skills
```

`setup` can't read or save config for a plugin loaded with `--plugin-dir`: `claude plugin configure` only works on an installed plugin. It still shows what discovery finds.

## Known limitations

- None of the Atlassian MCP calls have been run against a live site yet.
- Untested: the sprint goal lookup in `weekly-work-log`, which reads the sprint field on one of your sprint tickets. If no goal comes back, Sprint Goals is left for you to fill. The sprint heading link also needs a board id from that field.
- Untested: whether getting an issue through the MCP returns its comments, which `standup` reads for a blocked ticket's reason.
- Untested: finding the story points field by name, and the example MCP tool names for the site and field metadata.
- Untested: the upgrade from an earlier version, including whether a stored value for the removed `vault_name` key causes a warning. The CLI can't clear it.
- Untested: the Obsidian vault registry paths on Linux and Windows.
- `gh pr list` only sees the current repo. Review lookups use `gh search prs`, which searches across repos.
- In `weekly-work-wrap`, the ticket-link style and the Tech Lead Review voice are opinionated and not configurable. The "Toggle" issue-type exclusion assumes that Jira issue type exists, and is harmless if it doesn't.
