# ADR 0006: Software Management and Updates

- **Status:** Accepted
- **Date:** 2026-10-18

## Package management

Rivet uses **APT + dpkg**, inherited from Debian. There is no custom package manager.

## Graphical interface

The default image includes GNOME Software as the user-facing application store, with plugins for Debian packages and Flatpak. Synaptic remains available as an advanced graphical package manager, and APT remains available in the terminal.

The store is an interface to existing package-management systems, not a new package format or custom package manager.

## Flatpak and Flathub

Flatpak and the GNOME Software Flatpak plugin are installed by default. The build configures the official Flathub repository descriptor under `/etc/flatpak/remotes.d/` so Flatpak applications can be discovered through the store.

The image build fetches the official descriptor from Flathub and validates its repository URL and presence of its signing key. A build must fail visibly if the descriptor cannot be retrieved or does not pass validation. Flathub is a third-party application source for Flatpak; Rivet does not add third-party APT repositories by default.

Users should review an application's publisher and permissions before installing it. Package updates remain handled by the relevant package-management system through the software store or command-line tools.

## Updates

Rivet uses the official Debian updates for Trixie. Flatpak applications use the configured Flatpak remote. There is no custom update service.

## Shell

The default shell is **Bash**, following Debian. The terminal is not removed or hidden from the interface.

## Policy

Rivet should keep software sources limited and clearly documented. Prefer established package-management tools over unnecessary custom layers.
