---
name: skill-install
description: Install OpenClaw skills safely from a skill name, ClawHub URL, or GitHub URL. Use when a user asks to add/update skills and choose install scope (shared all agents, current agent, or a specific agent). Ask for source + target scope, then run skill-guard before final install.
---

# Skill Install

Install skills with a consistent, safety-first workflow.

## Required questions

Ask the user two things before installing:
1. **What skill to install?**
   - plain name (example: `skill-guard`)
   - ClawHub URL
   - GitHub URL
2. **Where to install?**
   - shared for all agents
   - current agent only
   - a specific agent

If unclear, stop and ask.

## Resolve source format

### A) Input is a plain name

1. Search ClawHub: `clawhub search "<query>"`
2. Pick top candidate slug(s) and confirm with user before install.
3. Use confirmed slug for install.

### B) Input is a ClawHub URL

1. Extract slug from URL path (last segment).
2. Optionally verify metadata with `clawhub inspect <slug>`.
3. Confirm extracted slug with user if ambiguous.

### C) Input is a GitHub URL

1. Clone to temporary staging directory.
2. Locate target skill folder containing `SKILL.md`.
   - If multiple matches exist, ask user which one.
3. Read frontmatter `name` and use it as destination folder name.

## Resolve install scope (target workdir)

- **Shared (all agents):** `~/.openclaw`
- **Current agent:** current workspace path
- **Specific agent:**
  - `main` → `~/.openclaw/workspace`
  - others → `~/.openclaw/workspace-<agentId>` (verify path exists)

Install destination is always `<workdir>/skills/<skill-name>`.

## Mandatory safety gate: skill-guard

Before final install, run **skill-guard**.

### Ensure skill-guard is available (shared)

```bash
clawhub --workdir ~/.openclaw install skill-guard --force
```

### For ClawHub installs (name or ClawHub URL)

Use skill-guard wrapper (pre-install scan + install on pass):

```bash
CLAWHUB_WORKDIR="<target-workdir>" \
~/.openclaw/skills/skill-guard/scripts/safe-install.sh <slug> [--version X.Y.Z] [--force]
```

Handle results:
- exit `0`: clean, installed
- exit `2`: threats found, do **not** auto-install; ask user whether to stop or manually override
- exit `1`: operational failure; report error

### For GitHub installs

1. Stage repository files in `/tmp`.
2. Run scanner directly on staged skill folder:

```bash
uvx mcp-scan@latest --skills <staged-skill-folder>
```

3. If scanner flags risks, stop and ask user whether to continue.
4. If clean, copy staged folder into `<target-workdir>/skills/<name>`.

## Install execution details

- Create destination skills directory if missing.
- If destination already exists, ask whether to overwrite (or use `--force` when already approved).
- Keep folder structure valid (`<skill>/SKILL.md` required).
- Avoid symlinks for packaged/distributable reliability.

## Post-install checks

1. Verify `SKILL.md` exists at destination.
2. Show installed path and source used.
3. Remind user that existing sessions may need refresh/new session to pick up new skills.

## Output format

Report concise result:
- source type + normalized slug/name
- target scope + target path
- safety scan result (pass/block/error)
- final install status
