# Rivet Agent Guidelines

These rules apply to any AI agent modifying this repository.

## Priorities

1. Preserve documented behavior and decisions.
2. Make only the changes required by the task.
3. Do not invent architecture to fill gaps.
4. Do not delete or rewrite files without a clear reason.
5. Always validate the result after editing.

## Before editing

Read:

- `README.md`
- `CONTRIBUTING.md`
- `docs/philosophy.md`
- `docs/architecture.md`
- the relevant ADR, when one exists

Then identify exactly which files need to change.

## While editing

- Prefer small, localized changes.
- Preserve existing names, paths, and interfaces.
- Do not add dependencies without justification.
- Do not make destructive changes.
- Do not force branches or rewrite history.
- Do not hide errors.
- Do not clean up unrelated code.

## Architecture

Rivet is based on Debian.

Undecided architecture must not be treated as decided. In particular, do not silently choose a different desktop, installer, build system, or custom tooling.

When a change represents an architectural decision, document it first or stop and ask for the decision.

## Build and validation

When a build system exists:

- failures must stop the process;
- intermediate results must be identifiable;
- destructive commands require a clear reason;
- a build that has not passed its checks must not be marked as complete.

## Before finishing

Check:

- changed files;
- paths;
- cross-file references;
- syntax;
- available tests;
- affected documentation.

Report exactly what changed and what remains unverified.

## Fundamental rule

**Do not turn a small task into a rewrite of Rivet.**
