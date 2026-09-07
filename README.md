# Family Chore & Reward Manager

A web-based application that helps families manage household chores through a point-based reward
system. Parents run everything from a browser; kids interact with a printable weekly chart on the
fridge instead of another screen.

## Why

Most chore apps put a phone in every child's hand. This one deliberately keeps the digital surface
parent-only and makes its primary output a piece of paper.

## Core ideas

- **Points store** — kids earn points for chores and spend them on rewards the parents define
  (e.g. "1 Hour Screen Time" = 50 pts).
- **Parent approval** — chores only credit points after a parent reviews and approves them.
- **Clean slate weekly** — nothing rolls over, no negative points; the week resets every Monday.
- **Auto-rotating routines** — recurring chores rotate between children each week for fairness.
- **Bonus bounties** — one-off, higher-value tasks kids can claim voluntarily.
- **The fridge chart** — a weekly PDF with rotations, point balances, and open bounties.
- **Low-noise reminders** — Friday (approve the week) and Sunday (print next week's chart).

## Tech stack

| Layer | Choice |
| --- | --- |
| Backend | Django (Python) |
| Database | SQLite (dev) / PostgreSQL (prod) via the Django ORM |
| Frontend | Django templates (HTML/CSS), minimal JavaScript |
| PDF | ReportLab |

## Data model (preview)

`Family`, `Profile` (parent/child), `Chore`, `ChoreAssignment`, `Reward`, `LedgerEntry`.

## Getting started

Everything runs through [uv](https://docs.astral.sh/uv/) — there is no activated virtualenv.

```
uv sync                                  # install dependencies
uv run python manage.py migrate          # set up the database
uv run python manage.py createsuperuser  # a parent who can reach /admin/
uv run python manage.py runserver        # http://127.0.0.1:8000/
```

Sign in and the app walks you through creating the family, its children, the
recurring chores and the rewards. Then generate a week of chores:

```
uv run python manage.py generate_week
```

## Repository layout

```
config/            Django project: settings, root urls, wsgi/asgi
chores/            the app: models, views, templates, admin
  management/commands/generate_week.py
_docs/plan.md      full project scope
_docs/AGENTS.md    guidance for coding agents
backlog.md         numbered tasks, mirrored as GitHub issues
```

## Status

Working. Chores rotate weekly, a parent approves them, points accrue, bounties
get claimed, and rewards get spent — the whole loop from
[`_docs/plan.md`](_docs/plan.md).

| Built | |
| --- | --- |
| Family and profiles | parents sign in, children never do |
| Chores and rewards | routine and bounty chores, a custom rewards store |
| Weekly rotation | `generate_week` rotates routine chores between children |
| Dashboard | the week grouped by child, with parent approval |
| Balances and ledger | per-child totals and a full audit trail |
| Bounty board | post a bounty, claim it, approve it |
| Reward redemption | spend points, never below zero |
| Fridge chart | the week as a one-page PDF, ready to print |
| Reminders | Friday to approve, Sunday to print; silent otherwise |

All eleven tasks in [`backlog.md`](backlog.md) are done and their
[GitHub issues](../../issues) closed.

## How the work is tracked

[`_docs/plan.md`](_docs/plan.md) is the spec, [`backlog.md`](backlog.md) breaks
it into numbered tasks, and each task is a GitHub issue with the same number.
Issues are labelled `MVP` or `post-MVP`; [`pm.md`](_docs/team/pm.md) says what is in each
and why. [`process.md`](_docs/team/process.md) describes how a task goes from spec to
commit, and [`task-template.md`](_docs/team/task-template.md) is the shape an issue takes.

## Not ready for production

The MVP runs, but it is set up for a laptop, not a household on the internet:

- the fallback `SECRET_KEY` in `settings.py` is public; set `DJANGO_SECRET_KEY`
  and `DJANGO_DEBUG=false` before serving anything
  (see [`_docs/deployment.md`](_docs/deployment.md))
- SQLite only; the spec asks for PostgreSQL in production ([#14](../../issues/14))
- no automated tests — every rule was verified by hand ([#12](../../issues/12))
- reminders need SMTP settings and a daily schedule — see
  [`_docs/deployment.md`](_docs/deployment.md)
