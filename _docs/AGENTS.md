# AGENTS.md

A Django app for managing family chores with a point-based reward system.
Parents use the browser; children never sign in. The spec is [`plan.md`](plan.md),
broken into numbered tasks in [`../backlog.md`](../backlog.md), one GitHub issue each.

## Commands

Everything runs through `uv` — there is no activated virtualenv.

- `uv sync` — install dependencies
- `uv run python manage.py runserver` — dev server on :8000
- `uv run python manage.py makemigrations chores && uv run python manage.py migrate` — after a model change
- `uv run python manage.py test` — the suite
- `uv run python manage.py generate_week` — rotate next week's routine chores

## Rules

- Dependencies are added in `pyproject.toml`, via `uv add`. Do not add one
  without asking.
- Only build what `plan.md` describes. Do not invent features — most notably,
  children have no login and no child-facing UI.
- A task is done when its **Done when:** check in `backlog.md` has actually been
  run. Show the output; do not conclude it works from reading the code.
- Work comes from GitHub issues, labelled `MVP` or `post-MVP`. Finish one with
  a commit saying `Closes #N`; if it left something behind, file that as its own
  issue instead of widening this one. The shape of an issue is in
  [`team/task-template.md`](team/task-template.md).
- Keep this file short. Every session pays for it, so a rule earns its place
  only if it changes what an agent does whatever the task is, and cannot be
  seen from the code.
