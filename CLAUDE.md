# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A collection of AI agent skills (for Claude Code / OpenClaw). Each skill is a self-contained directory with a `SKILL.md` file that defines its metadata and implementation workflow.

## Repository Structure

```
<skill-name>/
  SKILL.md          # Skill definition (YAML frontmatter + markdown body)
```

Every skill follows this pattern:
- **YAML frontmatter** (`---` delimited) with `name` and `description` fields
- **Markdown body** containing the full workflow: required inputs, step-by-step procedures, error handling, and reference tables

### Current Skills

- `snell-surge-deploy/` — Deploy Snell proxy server on a Linux VPS and configure local Surge proxy
- `skill-install/` — Install OpenClaw skills from ClawHub or GitHub with mandatory security scanning

## Conventions

### Commit Messages

Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`. Co-author line is added automatically.

### Skill Authoring

- Skills are documentation-driven — the `SKILL.md` IS the implementation (the agent follows it as instructions)
- Include mandatory user inputs as a table with examples and required/optional flags
- Include error handling sections with common mistakes tables
- Redact sensitive values (keys, passwords) in all agent output — write them only to config files
- Safety-first: include confirmation prompts before destructive or irreversible operations
- Cross-platform support: detect OS/architecture automatically rather than asking the user
