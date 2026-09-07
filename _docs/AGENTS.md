# AGENTS.md

Guidance for coding agents working in this repo. Humans are welcome to read it too.

## What this is

A Django app that helps a family manage chores with a point-based reward system.
Parents run everything from the browser; children never sign in and interact with
a printed weekly chart instead. The spec is [`plan.md`](plan.md); the work is
broken into numbered tasks in [`../backlog.md`](../backlog.md), one GitHub issue
each.

## Commands

Everything runs through `uv` — there is no activated virtualenv.

- `uv sync` — install dependencies
- `uv run python manage.py runserver` — the dev server on :8000
- `uv run python manage.py check` — Django system checks
- `uv run python manage.py makemigrations chores` — generate migrations after a model change
- `uv run python manage.py migrate` — apply them
- `uv run python manage.py test` — the whole suite (there are no tests yet, so this reports `NO TESTS RAN`)
- `uv run python manage.py test chores` — just this app
- `uv run python manage.py generate_week` — rotate next week's routine chores
- `uv run python manage.py shell -c "..."` — a quick check against real data

## Rules

- Dependencies are added in `pyproject.toml`, via `uv add`. Do not add one
  without asking.
- Work the backlog in order. Each task in `backlog.md` has a **Done when:**
  line — run it and paste the real output. Do not report a task done on the
  strength of having read the code.
- `makemigrations` saying `No changes detected` is not proof of anything. Check
  what you actually meant to verify.
- Children have no login credentials. `Profile.user` is null for them, and a
  check constraint enforces it. Do not add a child-facing login.
- Rules that matter belong in the database, not only in view code: point
  balances, one holder per chore per week, and one credit per approval are all
  enforced by constraints.
- Only build what `plan.md` describes. Do not invent features.
- Never commit `db.sqlite3`, `.venv/`, or `__pycache__/` — `.gitignore` covers
  them. The dev database is disposable.
- Match the surrounding style: single-quoted strings, four-space indents, and
  the same comment density as the code already there.

## Layout

```
config/          Django project (settings, root urls, wsgi/asgi)
chores/          the one app: models, views, templates, admin
  management/commands/generate_week.py
_docs/           plan and agent guidance
backlog.md       numbered tasks, mirrored as GitHub issues
```
