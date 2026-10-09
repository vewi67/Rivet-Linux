# Contributing to Rivet

Rivet is still in its foundation phase. At this stage, project stability means making careful decisions before adding complexity.

## Required rules

1. Read the relevant documentation in `docs/` before changing architecture.
2. Do not introduce a technology, daemon, framework, or layer just because it looks interesting.
3. Do not replace Debian components without a documented reason.
4. Architectural changes must update the relevant decision record.
5. Do not remove existing functionality without documenting the reason and alternative.
6. Avoid large changes that are difficult to review.
7. Agents must not delete or rewrite files that are unrelated to the task.
8. Before marking work complete, check changed files, paths, and broken references.
9. Build scripts must fail explicitly. Do not hide errors with `|| true` or equivalent without a documented reason.
10. The repository must remain reproducible by another contributor.

## AI agents

AI agents can help implement Rivet, but they are **not architectural authority**.

An agent should:

- stay within the task scope;
- explain changes that affect other areas;
- preserve documented decisions;
- prefer a small correct change over speculative rewrites;
- stop when an architectural choice has not been made.

### Anti-chaos rule

If a task requires choosing between two architectures that are not documented yet, **do not invent a third option**. Record the decision that is needed and wait for it.

## Before submitting a change

Confirm:

- the file is in the expected location;
- no unrelated files were changed;
- references to paths still work;
- documentation remains consistent;
- the project can still be built or validated for its current stage.

## Philosophy

The goal is not to make Rivet look complicated.

The goal is to make the computer feel simple **without taking control away from the user**.
