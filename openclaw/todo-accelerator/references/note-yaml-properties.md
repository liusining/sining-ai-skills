# Note YAML Properties

Each to-do companion note has a YAML frontmatter block. Below are all properties and which commands read or update them.

| Property | Type | Description | Read by | Written by |
|----------|------|-------------|---------|------------|
| `priority` | int | Urgency level (0 = normal, higher = more urgent) | `work-on-todo` (selection), `list-pending` (display) | `add-todo --priority N` |
| `iterate` | int | How many times this to-do has been worked on | `work-on-todo` (reads before incrementing) | `work-on-todo` (increments by 1) |
| `iteration-started-at` | string | ISO timestamp of when the current iteration began | — | `work-on-todo` (set to current time) |
| `created-at` | string | ISO timestamp of when the to-do was created | — | `add-todo` (set via template) |
| `target` | list | Expected outcomes / deliverables | — | `add-todo --targets` (set via template) |
