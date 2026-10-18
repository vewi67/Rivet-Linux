# ADR 0004: Initial System Profile

- **Status:** Accepted
- **Date:** 2026-10-07

## Goal

Define the minimum system decisions required for the first usable ISO.

## Base

- Debian 13 Trixie
- Initial architecture: amd64
- Kernel: standard Debian kernel
- Init: systemd
- Initramfs: initramfs-tools
- Bootloader: GRUB
- Default installer filesystem: ext4

Rivet will not ship a custom kernel or init system in the first version.

## Graphical session

- Xorg
- XFCE
- LightDM
- Thunar
- xfce4-terminal

## Services

- NetworkManager for networking
- PipeWire + WirePlumber for audio
- Debian services only when required by the system or supported hardware

The general rule is not to enable extra daemons just to add optional features.

## Initial software

The first ISO should contain only software needed for a usable desktop.

### Included

- Firefox ESR
- LibreOffice Writer and Calc
- core XFCE utilities
- required file and storage utilities
- GParted
- Synaptic
- basic diagnostic and networking tools

### Not included by default

- Steam
- Wine
- large multimedia application collections
- large development toolchains
- custom telemetry services
- duplicate applications with the same purpose

Users can install these later.

## Language and locale

The live session and default profile use English (United States), `en_US.UTF-8`. Rivet-owned utilities and the Calamares slideshow are authored in English for the current pre-alpha stage. Calamares keeps its locale selector, so an installer choice can still affect the installed system locale; additional Rivet UI translations are deferred to a later milestone.

## Updates

The system follows normal Debian updates for Trixie. Rivet does not ship its own update mechanism in the first version.

## Security

- Keep Debian's privilege model.
- Normal users do not have permanent root access.
- Administrative operations use sudo/polkit.
- Do not create custom authentication.

## Applied philosophy

The ISO should be ready to use without turning "ready to use" into "filled with things the user did not ask for."
