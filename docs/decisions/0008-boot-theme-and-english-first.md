# ADR 0008: Scripted Boot Identity and English-First UI

- **Status:** Accepted
- **Date:** 2026-10-18

## Context

Rivet needs a distinct boot experience and consistent language across its own utilities. The base image uses Debian components, and the boot splash must not require a video, an always-running service, or a custom animation framework.

## Decision

- Use Debian's Plymouth script theme for the Rivet boot identity.
- Slowly rotate the existing Rivet logo, animate a layered blue energy haze under **“Let us Do the Magic”**, then fade to **“Welcome to Rivet Linux”** as boot approaches the graphical handoff.
- Keep the animation in the Plymouth script. The Rivet logo is copied into the theme during image configuration.
- Enable `quiet splash` on the live kernel command line, select the Rivet Plymouth theme, and regenerate initramfs through Plymouth's supported helper.
- Set the live session and default profile locale to `en_US.UTF-8`. Rivet-owned utilities and the Calamares slideshow ship in English for now. Calamares retains its locale selector, so a selected install locale can still change the installed system locale; additional Rivet UI translations are deferred.
- Do not delay boot just to hold a branding screen. Exact timing and the final handoff must be tested on the generated ISO because Plymouth exits when the system hands over the display.

## Consequences

The visual identity uses a maintained Debian component and adds no resident process. The image gains Plymouth and locales packages. Repository validation does not prove that the animation appears correctly on every graphics driver; UEFI/BIOS VM testing and installed-system first boot remain required.
