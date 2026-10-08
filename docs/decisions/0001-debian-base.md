# ADR 0001: Debian as the Base

- **Status:** Accepted
- **Date:** 2026-10-07

## Context

Tip needs a solid base so the project can focus on the distribution's experience and philosophy instead of rebuilding fundamental components without a reason.

## Decision

Tip is based on **Debian**.

## Consequences

### Positive

- Established Linux foundation.
- Less need to rebuild fundamental components.
- Access to Debian's package ecosystem and tooling.
- More freedom to build Tip's identity in the layers above.

### Negative

- Some Tip decisions depend on the chosen base and its release cycle.
- The project must carefully decide which components are configured and which receive Tip-specific customization.
- Tip remains responsible for integration and testing of the final experience.

## Decision boundary

This ADR defines only the **base family**.

It does not define:

- the Debian release;
- the desktop;
- the installer;
- the build system;
- the final package selection.

Those decisions belong in separate ADRs.
