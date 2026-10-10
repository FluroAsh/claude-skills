# ash-skills

A [Claude Code](https://code.claude.com/docs/en/overview) plugin with the skills I use to keep a weekly work log in Obsidian. Personal settings such as the vault, folders and template are set once through the plugin's config prompt, so the skills aren't tied to one person or employer.

## Skills

| Skill | What it does | Needs |
|---|---|---|
| `weekly-work-log` | Audits last week's log, then sets up this week's | Obsidian, Jira |
| `weekly-work-wrap` | End-of-week wrap-up of the current log | Obsidian, Jira, git, `gh`, Sunsama (optional) |
| `daily-work-wrap` | Single-day catch-up for days you forgot to log | Obsidian, Jira, git, `gh`, Sunsama (optional) |
| `standup` | Standup prep. Read-only, chat output only | Obsidian, Jira, git, `gh`, Sunsama (optional) |

Invoke them namespaced, e.g. `/ash-skills:standup`. If `gh` or Sunsama is unavailable, the skills skip those steps.

## Setup

Claude Code, Obsidian and Jira are needed by every skill. The rest are only needed by the skills that list them above.

### Claude Code

```bash
brew install --cask claude-code
claude
```

Sign in when prompted on first run.

[Other install methods](https://code.claude.com/docs/en/overview)

### git

```bash
git config --global user.name "Your Name"
```

The skills use this name to find your commits.

### Obsidian

Install Obsidian and open your vault. Then turn on **Settings → General → Command line interface** and follow the registration prompt, which asks for admin rights on macOS.

[Download](https://obsidian.md) · [CLI docs](https://obsidian.md/help/cli)

### Jira

```bash
brew install ankitpokhrel/jira-cli/jira-cli
export JIRA_API_TOKEN="..."   # add this to your shell profile
jira init
```

[Create an API token](https://id.atlassian.com/manage-profile/security/api-tokens) · [jira-cli docs](https://github.com/ankitpokhrel/jira-cli)

### GitHub

```bash
brew install gh
gh auth login
```

[GitHub CLI docs](https://cli.github.com)

### Sunsama (optional)

Connect a Sunsama MCP server to Claude Code. It needs to expose `sunsama://tasks/{date}` and `sunsama://calendar/events/{date}`. Without one, the skills work from git and your own input.

[Sunsama](https://www.sunsama.com)

### The plugin

From inside Claude Code:

```
/plugin marketplace add FluroAsh/claude-skills
/plugin install ash-skills@ash-skills
```

Answer the config prompts, covered in the next section. Then run `/ash-skills:standup` to check everything works. It only reads, so it's safe to try first.

- **Private repo:** the machine needs GitHub access before the marketplace can be added.
- **Existing copies:** if these skills already exist as loose files in `~/.claude/skills` or `~/.claude/commands`, remove them, or each one shows up twice.

## Configuration

Claude Code prompts for these when the plugin is enabled. Values are stored locally on each machine. Change them later with `/config`.

| Field | Required | Meaning | Example |
|---|---|---|---|
| `vault_name` | yes | Obsidian vault name, as the Obsidian CLI knows it | `Work` |
| `vault_path` | yes | Absolute path to the vault root | `/Users/you/Documents/Work` |
| `weekly_log_template` | yes | Template note used to create a new week's log, relative to the vault root | `Templates/Weekly Work Log.md` |
| `weekly_log_folder` | no | Folder for weekly logs, relative to the vault root. `{YEAR}` expands to the four-digit year. Default `Weekly Work Logs/{YEAR}` | `Logs/{YEAR}` |
| `log_filename_format` | no | Filename pattern for a week's log, dated by that week's Monday. Default `MM-DD-YY.md` | `MM-DD-YY.md` |
| `company_name` | no | Used to calibrate the weekly Tech Lead Review | `Acme` |
| `review_context_files` | no | Notes (absolute or vault-relative) the Tech Lead Review is grounded in. Leave empty to skip the review | `Career/Goals.md` |

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

## Known limitations

- Untested: how list-valued or blank optional config values render when substituted into a skill.
- Untested: the Jira status-category lookup against a live ticket.
- `gh pr list` only sees the current repo. Review lookups use `gh search prs`, which searches across repos.
- In `weekly-work-wrap`, the ticket-link style and the Tech Lead Review voice are opinionated and not configurable. The "Toggle" issue-type exclusion assumes that Jira issue type exists, and is harmless if it doesn't.
