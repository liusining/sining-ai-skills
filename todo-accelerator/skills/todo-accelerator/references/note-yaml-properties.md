# Note YAML Properties

Each to-do companion note has a YAML frontmatter block. Below are all properties and which commands read or update them.

| Property | Type | Description | Read by | Written by |
|----------|------|-------------|---------|------------|
| `priority` | int | Urgency level (0 = normal, higher = more urgent) | `work-on-todo` (selection), `list-pending` (display) | `add-todo --priority N` |
| `iterate` | int | How many times this to-do has been worked on | `work-on-todo` (reads before incrementing) | `work-on-todo` (increments by 1) |
| `iteration-started-at` | string | ISO timestamp of when the current iteration began | — | `work-on-todo` (set to current time) |
| `created-at` | string | ISO timestamp of when the to-do was created | — | `add-todo` (set via template) |
| `allow-subagent` | bool | Whether the agent may delegate to a subagent (true = allowed, model choice is up to the agent) | `work-on-todo` (instruction) | `add-todo --allow-subagent` (set via template) |
| `assigned-agent` | string | Agent name that owns this to-do. Defaults to `$AGENT_ID`. Each agent only processes to-dos assigned to itself | `work-on-todo` (filtering), `list-pending` (filtering) | `add-todo` (defaults to `$AGENT_ID`) |
| `target` | list | Expected outcomes / deliverables | `work-on-todo` (display) | `add-todo --targets` (set via template) |
