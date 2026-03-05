---
name: skill-install-claude-code
description: Use when a user asks to install, add, or manage a Claude Code plugin from the official marketplace or a third-party source.
---

# Skill Install for Claude Code

Install and manage Claude Code plugins via the CLI.

## Required inputs

Ask the user before installing:

| Input | Question | Required | Default |
|-------|----------|----------|---------|
| **Plugin name** | Which plugin do you want to install? | Yes | — |
| **Source** | Official marketplace or third-party? | If third-party | official |
| **Scope** | User-level, project-level, or local-only? | No | `user` |

If the user provides a command like "install superpowers", infer plugin name and source (official). Only ask for missing information.

**Inferring from URLs:** If the user provides a URL, extract the plugin name and source:

| URL pattern | Plugin name | Source |
|-------------|-------------|--------|
| `https://claude.com/plugins/<name>` | last path segment | official (→ section A) |
| `https://github.com/<owner>/<repo>` | — | third-party (→ section B) |

## Commands reference

| Command | Purpose |
|---------|---------|
| `claude plugin install <plugin>@<marketplace>` | Install a plugin from a marketplace |
| `claude plugin list` | List installed plugins |
| `claude plugin marketplace add <source>` | Add a third-party marketplace source |
| `claude plugin marketplace list` | List configured marketplaces |

## A) Official plugin (from `claude-plugins-official`)

The official marketplace is available by default. Install directly:

```bash
claude plugin install <plugin-name>@claude-plugins-official
```

**Example — installing the superpowers plugin:**

```bash
claude plugin install superpowers@claude-plugins-official
```

Choose scope with `--scope`:

| Scope | Effect | Stored in |
|-------|--------|-----------|
| `user` (default) | Available across all your projects | `~/.claude/settings.json` |
| `project` | Shared with collaborators via git | `.claude/settings.json` |
| `local` | Only you, only this repo (gitignored) | `.claude/settings.local.json` |

```bash
# Install for the whole team
claude plugin install superpowers@claude-plugins-official --scope project
```

## B) Third-party plugin (not on official marketplace)

**Confirm with the user before adding a third-party source** — this grants trust to an external repository.

Three steps: **add the marketplace**, **find the marketplace name**, then **install the plugin**.

**Step 1 — Add the marketplace source:**

```bash
# From GitHub (owner/repo format)
claude plugin marketplace add owner/repo-name

# From a full Git URL
claude plugin marketplace add https://github.com/obra/superpowers.git

# From a local directory
claude plugin marketplace add ./path/to/marketplace

# From a remote marketplace.json
claude plugin marketplace add https://example.com/marketplace.json
```

**Step 2 — Find the marketplace name and available plugins:**

The marketplace name comes from the `name` field in the repository's `.claude-plugin/marketplace.json` — it is NOT the repo name. After adding, run:

```bash
claude plugin marketplace list
```

Show the user the marketplace name and available plugins. Let them choose which plugin to install.

**Step 3 — Install the chosen plugin:**

```bash
claude plugin install plugin-name@marketplace-name
```

## Managing plugins

If the user doesn't specify the marketplace name, run `claude plugin list` first to find the full `plugin-name@marketplace-name` identifier.

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

# Remove a third-party marketplace
claude plugin marketplace remove marketplace-name
```

## Verifying installation

After install, confirm the plugin is registered:

```bash
claude plugin list
```

**Important:** Newly installed plugins are NOT available in the current session. The user must start a new Claude Code session for installed plugins to take effect.
