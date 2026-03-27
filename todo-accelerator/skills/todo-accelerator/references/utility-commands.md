# Utility Commands

Less frequently used commands. `<CMD>` is the same base command defined in `SKILL.md`.

## remove-todo

Remove a to-do from Ideas and delete its companion note. Only tasks in Ideas can be removed — tasks in other columns are protected.

```bash
<CMD> remove-todo --name "todo name"
```

Use `list-pending --all` to find the exact name before removing.

## organize

Sort loose `.md` files in the board directory into `cards/` and `targets/` subfolders. Run after manually creating notes in the board directory to keep it tidy.

```bash
<CMD> organize
```
