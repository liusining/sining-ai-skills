---
name: skill-install
description: Use when a user asks to install, add, or update an OpenClaw skill.
---

# Skill Install

Install skills with a consistent, safety-first workflow.

## Required questions

Ask the user two things before installing:
1. **What is the source?**
   - plain name (example: `skill-guard`) — searched on ClawHub
   - ClawHub URL
   - GitHub URL
   - local file path — a skill directory on disk (e.g. `~/projects/my-skill`)
   - any other URL — agent fetches the page and follows installation instructions found there
2. **What install scope?**
   - **shared** — available to all agents on this machine
   - **current agent** — only the agent running in the current workspace
   - **a separate agent** — a different agent instance identified by its agent ID

If unclear, stop and ask.

## Resolve source format

### A) Input is a plain name

1. Search ClawHub: `clawhub search "<query>"`
2. Pick top candidate slug(s) and confirm with user before install.
3. Stage to a temporary directory for scanning before install:
   ```bash
   clawhub --workdir /tmp/clawhub-staging install <slug>
   ```
4. Run skill-guard scan on `/tmp/clawhub-staging/skills/<slug>` (see safety gate below).
5. If scan passes, copy into `<workdir>/skills/<name>` and clean up staging.

### B) Input is a ClawHub URL

1. Extract slug from URL path (last segment).
2. Optionally verify metadata with `clawhub inspect <slug>`.
3. Confirm extracted slug with user if ambiguous.
4. Stage, scan, and install using the same steps as flow A (steps 3–5).

### C) Input is a GitHub URL

1. Parse the URL to extract repo, ref (branch/tag/commit), and subdirectory path:
   - `https://github.com/owner/repo` — full repo, default branch
   - `https://github.com/owner/repo/tree/v4.3.1/skills/my-skill` — specific ref (`v4.3.1`) and subdirectory (`skills/my-skill`)
   - `https://github.com/owner/repo/tree/main/skills/my-skill` — specific branch and subdirectory
2. Clone to `/tmp/<repo-name>`, checking out the specific ref if present:
   ```bash
   git clone --branch <ref> --depth 1 <repo-url> /tmp/<repo-name>
   ```
   If no ref is specified, clone the default branch.
3. Locate the skill folder:
   - If the URL includes a subdirectory path, use that path directly as the skill folder.
   - Otherwise, find the directory containing `SKILL.md`:
     - If `SKILL.md` is at the repo root, the skill folder is the repo root itself.
     - If `SKILL.md` is nested, the skill folder is that subdirectory.
     - If multiple `SKILL.md` files exist, ask user which one.
4. Read frontmatter `name` from `SKILL.md` and use it as destination folder name.
5. Run skill-guard scan on the skill folder (see safety gate below).
6. If scan passes, copy the skill folder into `<workdir>/skills/<name>`.
7. Clean up the `/tmp/<repo-name>` staging directory.

### D) Input is a local file path

1. Verify the path exists and contains a `SKILL.md`.
2. Read frontmatter `name` from `SKILL.md` and use it as the destination folder name.
3. Run skill-guard scan on the local folder (see safety gate below).
4. If scan passes, create a **symlink** using the absolute path to the source:
   ```bash
   ln -s /absolute/path/to/source <workdir>/skills/<name>
   ```
   Always expand `~` to the full absolute path. This avoids duplicating files and keeps the local development copy as the single source of truth.

### E) Input is any other URL

1. **Ask the user to confirm they trust the content at this URL before proceeding.**
2. Fetch the page content.
2. Read the page for installation instructions or a link to the skill source.
3. If the page links to a GitHub repo or ClawHub slug, fall back to the matching flow above (A/B/C).
4. If the page provides a direct download (zip, tar), download to `/tmp/` and extract. Locate the `SKILL.md` inside and treat as a staged skill — run skill-guard scan before copying to destination.
5. If no clear instructions exist, report to user and ask how to proceed.

## Resolve install scope (target workdir)

- **Shared (all agents):** `~/.openclaw` — skill is available to every agent on this machine
- **Current agent:** the working directory of the current agent session (typically the project root, e.g. the output of `pwd` in the agent's shell)
- **A separate agent:** a different agent instance, identified by agent ID
  - `main` → `~/.openclaw/workspace`
  - others → `~/.openclaw/workspace-<agentId>`
  - If the workspace path does not exist, **stop and report the error** to the user. Do not create it — the agent ID may be wrong. Ask the user to confirm the agent ID or list known agents.

Install destination is always `<workdir>/skills/<skill-name>`.

## Mandatory safety gate: skill-guard

Before final install, follow **skill-guard** skill to scan the skill for threats.

**REQUIRED SUB-SKILL:** Use `skill-guard` for the scanning workflow.

### Ensure skill-guard is available

1. Check if skill-guard is already installed:
   ```bash
   ls ~/.openclaw/skills/skill-guard/SKILL.md
   ```
2. If not found, install it:
   ```bash
   clawhub --workdir ~/.openclaw install skill-guard
   ```

### Run the safety scan

Invoke skill-guard on the skill to be installed. skill-guard's own SKILL.md defines the scanning procedure — follow it.

If threats are found, do **not** auto-install. Ask user whether to stop or manually override.

## Install execution details

- Create destination skills directory if missing.
- If destination already exists, ask whether to overwrite (or use `--force` when already approved).
- Keep folder structure valid (`<skill>/SKILL.md` required).
- **Local sources:** use symlinks (see section D above).
- **Remote sources:** copy files directly — avoid symlinks for portability.

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
