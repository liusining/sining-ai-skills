# Initialization

One-time setup for To-Do Accelerator. Required when `todo-accelerator-config.yaml` does not exist in this skill's directory.

## Prerequisites

1. **Python 3** with **PyYAML** installed:
   ```bash
   pip3 install PyYAML
   ```

2. An **Obsidian Kanban board** — a `.md` file whose YAML frontmatter or settings block contains `kanban-plugin:`. If the board file lacks this identifier, the skill cannot be used.

## Steps

### 1. Gather information from the user

Ask the user for three paths:

| Parameter | Description |
|-----------|-------------|
| **Board file** | The `.md` file used as the Kanban board |
| **Notes folder** | Where companion note files should be stored |
| **Template file** | The markdown template for new to-do notes |

### 2. Run init

```bash
python3 <skill-dir>/scripts/todo.py \
  --config <skill-dir>/todo-accelerator-config.yaml \
  init \
  --board "/absolute/path/to/board.md" \
  --notes-folder "/absolute/path/to/notes/" \
  --template "/absolute/path/to/template.md"
```

The script:
- Validates the board contains `kanban-plugin:` identifier
- Creates the notes folder if it doesn't exist
- Validates the template file exists
- Writes `todo-accelerator-config.yaml` with relative paths
- **Errors if a config file already exists at that path** — delete it first to reinitialize

If validation fails, inform the user and ask for corrected paths.

### 3. Confirm

If the command prints "Initialized: ..." — setup is complete.

### 4. Add heartbeat activity

Add the following instruction to your heartbeat configuration so that Agents automatically process to-do items:

> Call `work-on-todo` to pick up a pending to-do. Follow the returned prompt to process it. Upon completion or when encountering difficulties that prevent you from continuing, call `commit` to finalize the work.

## Template Requirements

The template file must contain these placeholders:
- `{{targets}}` — replaced with YAML list items
- `{{requirements}}` — replaced with markdown checklist items
- `{{created_at}}` — replaced with ISO timestamp

And these section headings:
- `# What's More` — requirements checklist
- `# Target` — results and deliverables
- `# Investigation and Problems` — ongoing findings and obstacles
