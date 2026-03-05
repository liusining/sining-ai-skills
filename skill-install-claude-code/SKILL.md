---
name: skill-install-claude-code
description: Use when a user asks to install, add, or manage a Claude Code plugin.
---

# Skill Install for Claude Code

Install and manage Claude Code plugins via the CLI.

## Commands reference

| Command | Purpose |
|---------|---------|
| `claude plugin install <plugin>@<marketplace>` | Install a plugin from a marketplace |
| `claude plugin list` | List installed plugins |
| `claude plugin add <source>` | Add a third-party marketplace source |

## A) Official plugin (from `claude-plugins-official`)

The official marketplace is available by default. Install directly:

```bash
claude plugin install <plugin-name>@claude-plugins-official
```

**Example — installing the code-review plugin:**

```bash
claude plugin install code-review@claude-plugins-official
```

Choose scope with `--scope`:

| Scope | Effect | Stored in |
|-------|--------|-----------|
| `user` (default) | Available across all your projects | `~/.claude/settings.json` |
| `project` | Shared with collaborators via git | `.claude/settings.json` |
| `local` | Only you, only this repo (gitignored) | `.claude/settings.local.json` |

```bash
# Install for the whole team
claude plugin install code-review@claude-plugins-official --scope project
```

## B) Third-party plugin (not on official marketplace)

Two steps: **add the marketplace**, then **install the plugin**.

**Step 1 — Add the marketplace source:**

```bash
# From GitHub (owner/repo format)
claude plugin add owner/repo-name

# From a full Git URL
claude plugin add https://gitlab.com/org/plugins.git

# From a local directory
claude plugin add ./path/to/marketplace

# From a remote marketplace.json
claude plugin add https://example.com/marketplace.json
```

**Step 2 — Install the plugin from the new marketplace:**

```bash
claude plugin install plugin-name@marketplace-name
```

## Managing plugins

```bash
# List all installed plugins
claude plugin list

# Disable a plugin without removing it
claude plugin disable plugin-name@marketplace-name

# Re-enable a disabled plugin
claude plugin enable plugin-name@marketplace-name

# Update a plugin to latest version
claude plugin update plugin-name@marketplace-name

# Uninstall a plugin
claude plugin uninstall plugin-name@marketplace-name
```

## Verifying installation

After install, confirm the plugin is active:

```bash
claude plugin list
```

Remind the user that existing sessions may need a refresh or new session to pick up newly installed plugins.
