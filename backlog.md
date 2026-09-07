# Implementation Backlog — Family Chore & Reward Manager

Derived from [`_docs/plan.md`](_docs/plan.md). Scope is limited to what that spec
describes — nothing is invented here.

Tasks are ordered by dependency: no task depends on one that comes after it.
Everything lives in the `chores` app unless stated otherwise. Tasks 10 and 11 are
the riskier extras (PDF, reminders) — the app is usable without them, so it is
safe to stop after Task 9.

Run every `manage.py` command through uv, e.g. `uv run python manage.py check`.

Each task is mirrored as a [GitHub issue](../../issues) with the same number, so
progress lives there rather than being duplicated here. All eleven are done and
labelled `MVP`; work they left behind was filed separately as `post-MVP` issues
and is now done too, apart from PostgreSQL. See
[`pm.md`](_docs/team/pm.md).

---

## Task 1 — Family and Profile models

Add the `Family` model and a `Profile` model that attaches to Django's built-in
`User` and carries a role of either `PARENT` or `CHILD`. Children exist as
profiles only and never get login credentials, so a child `Profile` must be
creatable without a `User`. Register both in the Django admin so you can create
a family and its members by hand.

**Done when:** `uv run python manage.py makemigrations chores` generates
`0001_initial.py`, `uv run python manage.py migrate` applies it, and in
`uv run python manage.py shell -c "..."` you can create one `Family`, one parent
`Profile` and two child `Profiles`, then print them back.

---

## Task 2 — Parent-only access and base layout

Wire up `chores/urls.py`, include it from `config/urls.py`, and add a base
template plus a `@login_required` home view showing the logged-in parent's
family. Use Django's built-in auth views for login/logout — children never sign
in, so there is no self-registration flow to build.

**Done when:** `uv run python manage.py runserver` starts, visiting `/` while
logged out redirects to the login page, and after logging in as a superuser you
see the home page with your family name.

---

## Task 3 — Chore and Reward models

Add `Chore` with a title, base point value and a type of `ROUTINE` or `BOUNTY`,
and `Reward` with a name and point cost. Both belong to a `Family`. Register them
in the admin so a parent can define the chore list and the custom rewards store.

**Done when:** migrations apply cleanly and, in the admin at `/admin/`, you can
create two routine chores, one bounty chore and two rewards, and see them listed.

---

## Task 4 — ChoreAssignment and LedgerEntry models

Add `ChoreAssignment` linking a `Chore` to a child `Profile` for a specific week,
with an approval state (pending / approved) — points are never credited
automatically. Add `LedgerEntry` recording a point change against a child, with a
reason and a sign so it covers both earning and spending. Add a helper that sums a
child's ledger into a current balance.

**Done when:** migrations apply, and in the shell you can create an assignment,
add two `LedgerEntry` rows (one earn, one spend), and print a balance that matches
the arithmetic by hand.

---

## Task 5 — Weekly assignment generation with rotation

Write a management command that generates the coming week's `ChoreAssignment`
rows for a family, rotating routine chores between the children so a different
child gets each chore each week. Unfinished assignments from the previous week are
left behind and never carried forward — the week starts clean, with no penalty.

**Done when:** running the command twice for two consecutive weeks
(`uv run python manage.py generate_week ...`) produces assignments where the same
chore is held by different children in week 1 and week 2, and last week's pending
rows are untouched.

---

## Task 6 — Weekly dashboard with approve action

Build the parent's main screen: the current week's assignments grouped by child,
each pending one with an "Approve" button. Approving flips the assignment to
approved and writes a `LedgerEntry` crediting the chore's points to that child.
Approving twice must not credit twice.

**Done when:** with the server running you approve a chore in the browser, the
child's balance increases by exactly the chore's point value, and re-submitting
the same approval leaves the balance unchanged.

---

## Task 7 — Balances and ledger view

Add a page listing every child in the family with their current point balance, and
a per-child page showing their `LedgerEntry` history so points earned and spent
can be audited.

**Done when:** the balances page totals match the ledger rows for each child after
you approve two chores of different values.

---

## Task 8 — Bounty board

Add a page listing the family's open `BOUNTY` chores with their point values, plus
a form for a parent to post a new one. A parent can assign a bounty to the child
who claimed it, which creates a `ChoreAssignment` that then flows through the same
approval path as a routine chore.

**Done when:** you post a bounty in the browser, assign it to a child, approve it
from the dashboard, and the child's balance rises by the bounty's point value.

---

## Task 9 — Reward redemption

Add a page listing the family's rewards with their point costs and a "Redeem"
action per child. Redeeming writes a negative `LedgerEntry` for the cost. A
redemption that would take a child below zero must be rejected with a visible
error, since balances never go negative.

**Done when:** redeeming a reward a child can afford drops their balance by
exactly the cost, and attempting one they cannot afford shows an error and leaves
the balance unchanged.

---

## Task 10 — Printable weekly PDF chart *(riskier — optional)*

Add a view that renders the coming week's chart as a PDF using WeasyPrint or
ReportLab: the chore rotation per child, current point balances, and the open
bounties. This is the fridge printout, so keep the layout to a single clean page.

**Done when:** hitting the PDF URL downloads a file that opens in a PDF reader and
shows the same rotation, balances and bounties as the dashboard for that week.

---

## Task 11 — Friday and Sunday reminders *(riskier — optional)*

Add a management command that sends the two low-noise reminders described in the
spec: a Friday nudge to review and approve the week's chores, and a Sunday nudge
to generate and print next week's chart. Use Django's email backend and send only
to parent accounts — no daily notifications.

**Done when:** running the command prints the correct reminder for a simulated
Friday and the other one for a simulated Sunday, and prints nothing on other
days. Django 6.1 configures mail through `MAILERS`, which `startproject`
already points at the console backend, so no extra setup is needed.
