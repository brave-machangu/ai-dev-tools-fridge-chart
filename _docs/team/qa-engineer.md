# QA engineer

Owns the question the other roles cannot answer about their own work: is this
actually true? The scope is [`pm.md`](pm.md), the workflow is
[`process.md`](process.md), and the build is
[`software-engineer.md`](software-engineer.md).

## What counts as evidence

- **The output of a command that ran**, not a description of what it would do.
- **A check that can distinguish success from failure.** If a passing run and a
  broken run look identical, the check is not evidence. `makemigrations`
  printing `No changes detected` says that for a correctly registered app and
  for an app that was never installed; `showmigrations chores` separates them.
- **A negative control** wherever the rule matters: the redemption a child
  cannot afford, the second approval that must not pay, the other family's
  child that must 404.

## Testing

`uv run python manage.py test`. The suite in `chores/tests.py` guards the rules
the spec cares about rather than chasing coverage:

| Area | What is pinned |
| --- | --- |
| Approval | credits once, however many times it is posted; nothing before approval |
| Redemption | exact cost deducted; an unaffordable one is refused and deducts nothing; an exact balance lands on zero |
| Rotation | a different child each week, bounties never auto-assigned, last week untouched, re-runs create nothing |
| Constraints | a child cannot hold a login, one holder per chore per week, one credit per approval |
| Access | every page needs a login; another family's child is a 404 |
| Reminders | two days send, five days stay silent |

A suite that passes against broken code is worse than none. When adding a test,
break the rule it covers and watch it go red before trusting it.

## Traps this project has already hit

- A stale `runserver` on the same port serving old code, so a correct change
  looked broken.
- `check --deploy` passing while mail was misconfigured — configuration checks
  do not exercise the path; sending does.
- A test harness bug reading as an application bug: a cookie jar that was never
  written kept replaying a stale flash message.

When something looks wrong, rule out the harness before blaming the code.
