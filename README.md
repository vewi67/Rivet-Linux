# Rivet Linux

<p align="center">
  <strong>Your computer. Your rules.</strong><br>
  A Debian-based Linux distribution exploring what AI-led development can build.
</p>

<p align="center">
  <a href="https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102"><strong>⬇️ Download Rivet Linux #102</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/vewi67/Rivet-Linux/releases">All releases</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/vewi67/Rivet-Linux/issues">Report an issue</a>
</p>

> [!CAUTION]
> **Experimental ISO: download only if you want to test an unfinished project.** Rivet Linux is in **pre-alpha**, and there is a high chance this ISO may fail to boot, install, or work correctly after installation. It is **not recommended for normal use**. Test it in a virtual machine if possible. Do not install it on a computer you rely on, and never use it with important data.
>
> Build #102 has a known startup-splash problem that prevented a normal desktop handoff in testing. Fixes have been made in the source, but those changes have **not** been built into a replacement ISO yet. The download is still the older #102 image.

## What is Rivet?

Rivet Linux is a Debian-based distribution built around one simple principle:

**YOUR COMPUTER IS YOURS. CHANGE WHAT YOU WANT.**

The goal is to make everyday computing straightforward without taking control away from the person using the computer. Rivet is an independent, experimental project built with Debian components, an XFCE desktop, and custom Rivet tools and artwork.

## Why Rivet is different

### The ambition: a Linux distribution made entirely through AI-led development

AI is a central builder and collaborator across Rivet's code, configuration, documentation, troubleshooting, and design. Rivet aims to push toward a Linux distribution whose development is carried out entirely through AI-led implementation, with human direction and review.

**Our search for prior art:** we found projects such as [SlopOS](https://github.com/SlopLabs/slopos), which describes itself as an operating system designed and written by AI agents, and [UniqOS](https://github.com/NullLabTests/UniqOS), a custom operating system built with AI assistance. We also found Linux distributions that integrate AI or describe themselves as *vibe-coded*. However, in the sources we checked, we did **not** find independently verified evidence establishing that an earlier Linux distribution was developed **100% by AI**.

That does **not** prove Rivet is the world's first. “100% AI-made” can mean different things, and Rivet's development still involves human direction, decisions, and review. For now, we describe being first as an **ambition and a claim under investigation**, not a verified world record.

**Know an earlier project that fits this exact claim?** Please [open an issue](https://github.com/vewi67/Rivet-Linux/issues) with its name and evidence or links. We'll review credible examples and update this section if we find a project that predates Rivet or better fits the description. The goal is to get the history right, not to win an argument.

### Our principles

- **Control:** important system decisions should not be hidden.
- **Simplicity:** common tasks should have obvious paths.
- **Freedom:** users can configure the system and choose their software.
- **Lightweight by design:** avoid unnecessary software, services, and layers.
- **Compatibility:** build on Debian and established Linux components.
- **Clarity:** prefer predictable behavior over unexplained automation.

## Project status

**Pre-alpha. Not ready for daily use.**

The development configuration includes:

- Debian live-build image configuration
- XFCE desktop, LightDM, and Thunar
- Rivet branding, wallpapers, and Chip the beaver mascot
- Calamares installer branding
- Chip welcome experience and installed settings hub
- Rivet Atmosphere wallpaper controls
- GNOME Software integration for Debian packages and Flatpak
- Chip Fixs, an early system-diagnostics and repair prototype

These features are part of the development configuration. Their presence does **not** mean every feature has been fully tested in a booted or installed system.

### What still needs testing

BIOS and UEFI boot, installation to a virtual disk, first login, removal of live-session-only entries after installation, networking, audio, wallpapers, the settings hub, software installation, and behavior on real hardware all need further runtime verification.

The latest source changes include removing the faulty custom startup-splash integration, restoring visible Linux startup messages, simplifying the live dock, and replacing the experimental Rivet Pong installer slideshow with a readable Rivet information page. **These source fixes are not included in the published #102 ISO.**

## Download

**[Get Rivet Linux #102 from GitHub Releases](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102)**

The release page contains the ISO and its supporting download files. Read the warning at the top before downloading. This is an experimental development image, not a stable release.

## Technology

| Component | Choice |
|---|---|
| Base | Debian 13 Trixie |
| Architecture | amd64 |
| Desktop | XFCE |
| Display server | Xorg |
| Display manager | LightDM |
| File manager | Thunar |
| Networking | NetworkManager |
| Audio | PipeWire + WirePlumber |
| Init | systemd |
| Initramfs | initramfs-tools |
| Bootloader | GRUB |
| Default filesystem | ext4 |
| ISO builder | Debian live-build |
| Installer | Calamares |
| Software management | APT, dpkg, GNOME Software, Flatpak/Flathub |
| Welcome experience | Python + GTK 3 |
| Wallpaper controls | XFCE + GTK 3 |
| System utility | Chip Fixs, Python + GTK 3 |
| Mascot | Chip the beaver |

## Repository layout

- `.github/workflows/`: repository checks and ISO build workflow
- `build/build.sh`: local ISO build entry point
- `build/config/package-lists/`: installed software selection
- `build/config/hooks/`: image-time configuration
- `build/config/includes.chroot/`: files included in the live system
- `config/`: project-level configuration notes
- `docs/`: architecture, philosophy, and roadmap
- `scripts/`: repository validation

## Validate the repository

From the repository root, run:

```bash
bash scripts/validate-repo.sh
```

This checks required files, shell and Python syntax, package-list consistency, branding assets, launcher integration, and documentation conventions. It does not build or test the ISO.

## Build locally

On a Debian-based build environment with `live-build`, `xorriso`, `file`, and `coreutils` installed, first run the configuration preflight:

```bash
bash build/build.sh --configure-only
```

After reviewing the preflight and deciding to build, run:

```bash
bash build/build.sh
```

The ISO and SHA-256 checksum are written under `build/`. See [build/README.md](build/README.md) for details.

The automated manual-ISO workflow requires explicit `YES` authorization, an unused release number, and all required pre-build checks. A normal push does not build or publish an ISO.

## First milestone

Rivet's first milestone is a bootable, usable, installable ISO that can:

1. Boot in a virtual machine using BIOS or UEFI.
2. Start XFCE.
3. Provide working networking and audio when supported by the environment.
4. Launch included applications.
5. Open the Rivet-branded Calamares installer.
6. Install to a virtual disk and boot the installed system.
7. Create and use a normal account.
8. Update installed packages.

Rivet has **not yet demonstrated that all these milestones work reliably**. The project is still under active development.

## License and attribution

Rivet's original source code, build scripts, and configuration are licensed under **GNU GPL-3.0-or-later**, unless a file says otherwise. Covered code may be used, modified, and redistributed under the license's terms, with required notices preserved.

Rivet branding and artwork, including the name, logo, and Chip mascot, are not automatically covered by the code license. See [docs/branding-and-attribution.md](docs/branding-and-attribution.md) for attribution guidance, branding boundaries, and third-party license notes.

## Development rule

> **Define before implementing. Keep stable components when they work. Do not add complexity just because it is possible.**

See [docs/architecture.md](docs/architecture.md), [docs/roadmap.md](docs/roadmap.md), [docs/branding-and-attribution.md](docs/branding-and-attribution.md), and [CONTRIBUTING.md](CONTRIBUTING.md).
