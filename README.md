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
| PDF | WeasyPrint or ReportLab |

## Data model (preview)

`Family`, `Profile` (parent/child), `Chore`, `ChoreAssignment`, `Reward`, `LedgerEntry`.

## Repository layout

```
_docs/plan.md    Full project scope and plan
.gitignore
README.md
```

## Status

Planning stage — see [`_docs/plan.md`](_docs/plan.md) for the full scope. No application code yet.
