# ADR 0006: Software Management and Updates

- **Status:** Accepted
- **Date:** 2026-10-07

## Package management

Rivet uses **APT + dpkg**, inherited from Debian.

There is no custom package manager in the first version.

## Interface

The first ISO provides:

- APT for terminal users;
- Synaptic as a simple graphical package manager.

A custom tool may be created later only if a real usability problem is found that these tools do not solve well.

## Flatpak

Flatpak is not required and is not installed by default in the first ISO.

The Debian repositories are the priority because this avoids duplicating software update systems and software sources.

Flatpak may be offered later as a documented option.

## Updates

Rivet uses the official Debian updates for Trixie.

There is no custom update service at this stage.

Security updates and bug fixes remain on the normal Debian update path.

## Third-party repositories

The ISO does not add third-party repositories by default.

Users may add external repositories themselves.

## Shell

The default shell is **Bash**, following Debian.

The terminal is not removed or hidden from the interface.

## Policy

Rivet should have few software sources, and they should be clear and predictable.

**A known, trusted tool is preferable to an unnecessary custom layer.**
