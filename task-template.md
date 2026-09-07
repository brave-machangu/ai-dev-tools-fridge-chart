# Task template

The shape every issue in this repo uses. It exists because an issue has to be
readable on its own — if you need `_docs/plan.md` open beside it to know what to
build, the issue is not finished.

```markdown
<One line: what the app is, so the issue makes sense cold.>

## Scope

<What to build. Two or three sentences, no more.>

## Rules this has to respect

- <A product rule, stated here rather than left in the plan.>
- <The thing an implementer would otherwise get wrong by default.>

## Done when

<One check you can run. A command, or a click-through with an observable result.>

## Not in this issue

<What a reader might reasonably expect here but will not get, and the issue
number where that work lives instead. Omit if there is nothing to exclude.>
```

## Why each part is there

- **Context line** — someone opening the issue cold should not have to guess
  what a "ledger" or a "bounty" is.
- **Rules** — the product decisions that make an implementation right or wrong:
  points are only credited on approval, balances never go negative, bounties
  are claimed and never assigned. Leaving these in the spec means every
  implementer has to rediscover them.
- **Done when** — the acceptance check, phrased so it can be *run*. "Works
  correctly" is not one; "approving twice leaves the balance unchanged" is.
- **Not in this issue** — the boundary. Without it, a task quietly grows, or
  work falls between two issues and nobody notices.

## Sizing

One sitting. If a task needs two, it is two tasks. Order them so nothing
depends on an issue with a higher number.
