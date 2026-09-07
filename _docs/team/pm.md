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

## After the MVP — issues #12–#18, six of seven done

| Issue | State |
| --- | --- |
| #12 Automated tests | Done. 26 tests over approval, redemption, rotation, constraints and access |
| #13 Deliver the reminders | Done. SMTP from the environment, scheduling documented in [`../deployment.md`](../deployment.md) |
| #15 Harden settings | Done. Key, debug and hosts from the environment; `check --deploy` is clean |
| #16 Retire finished bounties | Done. An approved bounty leaves the board and the printed chart |
| #17 Set up a family without the admin | Done. `/setup/` takes a new parent from nothing to a printable week |
| #18 Remove the uv-init leftovers | Done. The project is no longer built as a package |
| **#14 PostgreSQL** | **Open.** The engine switches on `POSTGRES_DB` and the driver is an optional extra, but `migrate` has never run against a real server, so the constraints are proven on SQLite only |

## What the MVP deliberately does not do

Children have no accounts, no app, and no screen. The output for them is a sheet
of paper. Anything that puts a child in front of the software is out of scope,
not merely deferred.
