# ADR 0008: Plain-Text Boot and English-First UI

- **Status:** Superseded
- **Date:** 2026-10-19

## Context

Rivet needs a consistent language across its own utilities, while early startup must remain dependable and diagnosable. Build-time checks cannot confirm that a custom graphical splash successfully hands the display to the desktop manager on real hardware.

## Decision

- Retire the custom graphical boot animation and remove its splash package/theme integration from the source image.
- Use the standard Linux startup display: do not add `quiet` or `splash` to the live or installed boot command line, and keep `systemd.show_status=1` enabled so startup messages remain visible.
- Remove the corresponding Calamares configuration stage, so the installer does not try to configure a splash program that Rivet no longer ships.
- Keep the live session and default profile locale at `en_US.UTF-8`. Rivet-owned utilities and the Calamares wiki ship in English for now. Calamares retains its locale selector, so a selected installation locale can still change the installed system language.
- Do not add a boot delay merely to hold a branding screen. Reconsider a graphical identity only after a plain-text boot and the display-manager handoff pass BIOS, UEFI and installed-system tests.

## Consequences

The boot path is simpler and keeps useful diagnostics visible during startup. The #102 release remains available as a historical build, but its graphical splash failed during real user testing. The source correction is not a replacement ISO until a newly authorized build is completed and tested.
