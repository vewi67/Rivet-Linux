# Rivet Linux

> **Your computer. Your rules.**

Rivet is a Debian-based Linux distribution built around one simple idea:

**YOUR COMPUTER IS YOURS. CHANGE WHAT YOU WANT.**

Rivet aims to make everyday computing straightforward without taking control away from the user.

## Principles

- **Control:** important system decisions should not be hidden.
- **Simplicity:** common tasks should have obvious paths.
- **Freedom:** users can configure the system and choose their software.
- **Lightweight by design:** avoid unnecessary software, services, and layers.
- **Compatibility:** reuse Debian components and established tools.
- **Clarity:** prefer predictable behavior over unexplained automation.

## Project status

**Pre-alpha. Not ready for daily use.**

The Debian live-build configuration, Rivet visual identity, Calamares branding, Chip welcome experience, Rivet Atmosphere controls, GNOME Software store with Debian package and Flatpak integration, and Chip Fixs prototype are integrated into the development configuration. The Calamares slideshow now presents a readable Rivet history/wiki page instead of the experimental Rivet Pong game. Chip Fixs includes a GTK interface, separate diagnostic core, hardware inventory, bounded system checks, confirmation-gated service repairs, and its custom icon.

**Latest published image: [Rivet Linux #102](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102).** A real test found that the custom startup splash in #102 failed before a normal desktop handoff. The current source correction removes the splash program and its custom integration, restores visible Linux startup messages, simplifies the live dock and replaces Rivet Pong with a readable installer wiki. These are source changes, not a new ISO: no replacement image has been built or published yet.

Those are build-time and image-structure checks, not a substitute for testing the new ISO in a VM. Still to verify at runtime: BIOS and UEFI boots, the installed first-login flow, disappearance of live-only dock/menu entries after installation, the Rivet Control Center, networking, audio, wallpapers, Calamares branding, GNOME Software operations, and real-hardware behavior. Rivet remains pre-alpha and is not ready for daily use.

The manual ISO workflow requires an explicit `YES` authorization, an unused release number, and all three pre-build checks. A normal push does not build or publish an ISO.

## Current architecture

| Component | Choice |
|---|---|
| Base | Debian 13 Trixie |
| Architecture | amd64 |
| Desktop | XFCE |
| Display server | Xorg |
| Display manager | LightDM |
| File manager | Thunar |
| Network | NetworkManager |
| Audio | PipeWire + WirePlumber |
| Init | systemd |
| Initramfs | initramfs-tools |
| Bootloader | GRUB |
| Default filesystem | ext4 |
| ISO builder | Debian live-build |
| Installer | Calamares |
| Package management | APT + dpkg + GNOME Software + Flatpak/Flathub |
| Welcome experience | Python + GTK 3 live welcome and installed settings hub |
| Wallpaper atmosphere | XFCE native backdrop cycler + GTK 3 control |
| System utility | Chip Fixs (Python + GTK 3) |
| Mascot | Chip the beaver |

## Repository layout

- .github/workflows/: repository checks and ISO build
- build/build.sh: local ISO build entry point
- build/config/package-lists/: installed software selection
- build/config/hooks/: image-time configuration
- build/config/includes.chroot/: files included in the live system
- config/: project-level configuration notes
- docs/: architecture, philosophy, and roadmap
- scripts/: repository validation

## Validate the repository

Run from the repository root:

    bash scripts/validate-repo.sh

This checks required files, shell and Python syntax, package-list consistency, branding assets, launcher integration, and documentation conventions. It does not replace building or testing the ISO.

## Build locally

On a Debian-based build environment with live-build, xorriso, file, and coreutils installed, first check the live-build configuration without generating an ISO:

    bash build/build.sh --configure-only

When that preflight passes and you have decided to build locally, run:

    bash build/build.sh

The resulting ISO and its SHA-256 checksum are written under build/. See build/README.md for details.

## First milestone

The first milestone is a bootable, usable, installable ISO that can:

1. boot in a virtual machine using BIOS or UEFI;
2. start XFCE;
3. provide working networking;
4. provide audio when the virtual machine exposes it;
5. launch the included applications;
6. open the Rivet-branded Calamares installer;
7. install to a virtual disk;
8. boot the installed system;
9. create and use a normal account;
10. update installed packages.

This is a development image, not a release. Do not use it as the only copy of an important system.

## License and attribution

Rivet's original source code, build scripts, and configuration are licensed under **GNU GPL-3.0-or-later**, unless a file says otherwise. This lets others use Rivet as a foundation, modify it, and redistribute covered code under the license's terms. Modified distributions must preserve required notices and clearly identify modifications as required by the GPL.

Rivet branding and artwork, including the name, logo, and Chip mascot, are not automatically covered by the code license. See [docs/branding-and-attribution.md](docs/branding-and-attribution.md) for attribution guidance, branding boundaries, and third-party license notes.

## Development rule

> **Define before implementing. Keep stable components when they work. Do not add complexity just because it is possible.**

See docs/architecture.md, docs/roadmap.md, docs/branding-and-attribution.md, and CONTRIBUTING.md.
