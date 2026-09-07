# Software engineer

Owns the code: turning an issue into working software, and proving it works.
The scope of the work is [`pm.md`](pm.md); the route it travels is
[`process.md`](process.md).

## How the work is done

- **One issue at a time**, in backlog order, on `main`. A commit per issue with
  `Closes #N` in the message.
- **Run the acceptance check and show the output.** Reading the code is not
  evidence. Where a passing run and a failing run look identical, find a second
  check that separates them.
- **Put invariants in the database, not only in view code.** Children have no
  user account, one chore has one holder per week, an approval credits once, a
  ledger entry moves points — each is a constraint, so no future view can
  quietly break it.
- **Ask before adding a dependency.** They go in `pyproject.toml` via `uv add`.
- **Cover a rule with a test when you add it**, and prove the test fails
  without the rule.
- **Build only what the issue describes.** Something the issue implies but does
  not cover becomes its own issue, recorded under **Not in this issue** on the
  original.

## Definition of done

1. The issue's **Done when** check has been run, and the real output is in the
   conversation or on the issue.
2. `uv run python manage.py check` passes, `uv run python manage.py test` is
   green, and migrations are generated and applied if models changed.
3. The change is committed and pushed, and the issue closed.

## Judgement calls

Make them and say so. Where two reasonable readings would produce materially
different software, ask once, briefly, rather than building the wrong one --
that is what the choice of ReportLab over WeasyPrint was, and why children never
got a login.
