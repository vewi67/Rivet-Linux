# ADR 0008: Scripted Boot Identity and English-First UI

- **Status:** Accepted
- **Date:** 2026-10-18

## Context

Rivet needs a distinct boot experience and consistent language across its own utilities. The base image uses Debian components, and the boot splash must not require a video, an always-running service, or a custom animation framework.

## Decision

- Use Debian's Plymouth script theme for the Rivet boot identity, without a resident animation service.
- During startup, show the actual status/message updates received by Plymouth in a restrained terminal-style panel. Enable `systemd.show_status=1` on both the live and installed boot paths so quiet boot does not suppress systemd's terse service statuses.
- As boot approaches the graphical handoff, transition to the aspect-ratio-preserved Rivet logo over a subtle animated blue/cyan smoke layer, then fade in **“Welcome to Rivet Linux”** and keep the final identity visible until Plymouth exits.
- Generate eight small transparent smoke frames deterministically during image configuration. The theme consumes them from the initramfs; no background process or animation framework is added.
- Keep all animation in the Plymouth script. The Rivet logo is copied into the theme during image configuration and the initramfs is regenerated through Plymouth's supported helper.
- Set the live session and default profile locale to `en_US.UTF-8`. Rivet-owned utilities and the Calamares slideshow ship in English for now. Calamares retains its locale selector, so a selected install locale can still change the installed system locale; additional Rivet UI translations are deferred.
- Do not delay boot just to hold a branding screen. The final animation runs before Plymouth hands the display to LightDM; it cannot draw over a desktop that is already interactive. Exact timing and the final handoff must be tested on the generated ISO.

## Consequences

The visual identity uses a maintained Debian component and adds no resident process. The smoke textures are build-time assets; the image already includes Pillow for other branded build operations. Repository validation does not prove that the animation appears correctly on every graphics driver; UEFI/BIOS VM testing and installed-system first boot remain required.
