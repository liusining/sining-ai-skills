# Initialization — Claude Code

One-time setup for To-Do Accelerator on Claude Code.

## Prerequisites

1. **Python 3** with **PyYAML** installed: `pip3 install PyYAML`
2. An existing Obsidian Kanban board (`.md` file with `kanban-plugin` identifier and `##` column headings: Ideas, 推进中, 审阅中, Done, Archive)
3. An existing notes folder for companion note files

## Why not use `init`?

The `init` subcommand creates a new board from the template. If your board already has data (existing `##` headings), `init` will refuse to run — and even if it could, it would overwrite your existing tasks. Skip `init` and create the config manually.

## Steps

### 1. Create config file

Create `todo-accelerator-config.yaml` in a shared location (e.g., `~/.config/todo-accelerator/todo-accelerator-config.yaml`) so all agents on the same machine share one config. Use absolute paths:

```yaml
board: /absolute/path/to/board.md
notes_folder: /absolute/path/to/notes/
template: /absolute/path/to/todo-accelerator/assets/note-template.md
```

Add the config directory to `.gitignore` so each machine can maintain its own config.

### 2. Verify

```bash
python3 <skill-dir>/scripts/todo.py --config <config-path> list-pending
```

Should list pending to-dos or print "No pending to-dos in Ideas."

### 3. Set up periodic checks (replaces OpenClaw heartbeat)

In Claude Code, use `CronCreate` to schedule periodic `work-on-todo` checks:

```
CronCreate cron="*/10 * * * *" prompt="<work-on-todo prompt>"
```

This replaces OpenClaw's heartbeat mechanism. CronCreate jobs are session-scoped (lost on exit, auto-expire after 7 days).

**Do NOT auto-start the cron on session startup.** Only create it when the user explicitly requests periodic checks (e.g. during intensive TODO sessions). The user specifies the interval; default to every 10 minutes if not specified.

## Concept mapping: OpenClaw → Claude Code

| OpenClaw | Claude Code |
|----------|-------------|
| Agent heartbeat event | CronCreate periodic check |
| HEARTBEAT.md | CLAUDE.md instructions |
| Agent workspace | Working directory |
| `--assigned-agent` (cross-agent delegation) | `AGENT_ID` env var; each agent only processes its own tasks |
| `--allow-subagent` | Agent tool (subagent) |
