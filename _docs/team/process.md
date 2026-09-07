# How work moves through this repo

Spec → backlog → issues → code → proof → commit.

1. **Spec.** [`_docs/plan.md`](../plan.md) is what the product should do.
   It changes rarely, and only deliberately.
2. **Backlog.** [`backlog.md`](../../backlog.md) breaks the spec into numbered tasks,
   ordered so nothing depends on a later one, each small enough for one sitting
   and each carrying a **Done when** check.
3. **Issues.** Every task is a GitHub issue with the same number, written to the
   shape in [`task-template.md`](task-template.md). Issues are labelled `MVP`
   (the first shippable version) or `post-MVP` (deferred).
4. **Code.** One task at a time, in backlog order.
5. **Proof.** Run the task's **Done when** check and show the real output. A
   task is not done because the code looks right — see the note on ambiguous
   output below.
6. **Commit.** One commit per task, with `Closes #N` in the message so the issue
   closes on push.

## Proving a task is done

Run the check. Paste what the terminal actually printed. Where success and
failure would look identical, find a second check that distinguishes them:

- `makemigrations` printing `No changes detected` means nothing on its own — it
  says that both for a correctly registered app with no model changes and for an
  app that was never registered. `showmigrations chores` tells them apart.
- A page that renders is not a page that works. Approving a chore twice returns
  `302` either way; only the balance and the ledger row count show whether it
  paid twice.
- A passing test suite proves nothing until you have seen it fail. Break the
  rule the test covers, watch it go red, then put the rule back.
- Check you are talking to the code you just wrote. A stale `runserver` holding
  the port will happily serve the old behaviour and look like a bug in the new
  work.

## Grooming

When an issue turns out to have left something behind, say so in the issue
under **Not in this issue** and file the remainder as its own issue rather than
widening the original. Follow-ups say plainly whether the spec asked for them or
whether they are engineering work the spec never mentioned.
