# ADR 0002: XFCE as the Initial Desktop

- **Status:** Accepted
- **Date:** 2026-10-07

## Context

The first Tip version needs to be usable quickly, work well across varied hardware, and keep the interface simple without blocking customization.

## Decision

The initial desktop is **XFCE 4.20 on Xorg**.

## Why XFCE

- Lightweight and suitable for modest hardware.
- Conventional interface that is easy to understand.
- XFWM provides window management without requiring another desktop compositor.
- Modular and highly configurable.
- Available directly in Debian 13.

Tip will not create its own desktop environment for the first version.

## Main components

- Desktop: XFCE
- Display server: Xorg
- Display manager: LightDM
- File manager: Thunar
- Terminal: xfce4-terminal
- Network UI: NetworkManager + GTK applet

## Future decision

Wayland may be evaluated later, but it is not part of the first version because the current priority is stability and fast delivery.
