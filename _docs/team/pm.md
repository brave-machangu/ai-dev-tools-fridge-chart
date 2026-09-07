# Scope: what ships in the MVP

The MVP is the whole loop from [`_docs/plan.md`](../plan.md): chores rotate
weekly, a parent approves them, points accrue, bounties get claimed, rewards get
spent, and the week prints as a chart for the fridge.

## In the MVP — issues #1–#11, all shipped

| | |
| --- | --- |
| #1 #3 #4 | Family, profiles, chores, rewards, assignments, ledger |
| #2 | Parent-only access; children never sign in |
| #5 | Weekly rotation of routine chores |
| #6 | Dashboard and parent approval — the only thing that pays points |
| #7 | Balances and the ledger audit trail |
| #8 #9 | Bounty board and reward redemption |
| #10 #11 | The printable fridge chart and the Friday/Sunday reminders |

## Deferred — issues #12–#18

| Issue | Why it waits |
| --- | --- |
| #12 Automated tests | Every rule has been verified by hand; nothing guards them yet |
| #13 Deliver the reminders | The command works; nothing schedules it and mail goes to the console |
| #14 PostgreSQL | The spec asks for it in production. SQLite runs the MVP, so this is the one line of the spec the MVP knowingly ships short |
| #15 Harden settings | Development `SECRET_KEY`, `DEBUG = True`, empty `ALLOWED_HOSTS` — fine locally, not beyond |
| #16 Retire finished bounties | The board only grows; cosmetic until a family has used it for a while |
| #17 Set up a family without the admin | A parent needs a superuser today. Blocks real users, not the demo |
| #18 Remove the uv-init leftovers | Repository tidiness |

## What the MVP deliberately does not do

Children have no accounts, no app, and no screen. The output for them is a sheet
of paper. Anything that puts a child in front of the software is out of scope,
not merely deferred.
