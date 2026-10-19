# ISO Build

The build/ directory contains the inputs and entry point for the Rivet Linux development ISO.

## Build system

Rivet uses Debian live-build inside a Debian Trixie container in GitHub Actions. The build definition is versioned under build/config/:

- package-lists/ selects installed software.
- includes.chroot/ supplies files that should exist in the generated system.
- hooks/ applies configuration after packages are installed.

## Local build

Use a Debian-based environment with live-build, xorriso, file, and coreutils installed. Run from the repository root:

    bash scripts/validate-repo.sh
    bash build/build.sh --configure-only
    bash build/build.sh

The build script checks its required inputs, configures live-build for Debian Trixie amd64, builds the image, checks the ISO boot metadata, and writes a SHA-256 checksum beside the ISO. The final image is renamed from live-build's generic output to `Rivet-Linux.amd64.iso` before its checksum is written.

Expected output:

    build/Rivet-Linux.amd64.iso
    build/Rivet-Linux.amd64.iso.sha256

The build script clears previous live-build stages when present, removes only generated live-build configuration values and stale ISO/checksum outputs, and retains the tracked package lists, hooks, chroot includes, and package cache. It then regenerates a fresh configuration from the versioned build arguments.

## GitHub Actions

The Build Rivet ISO workflow requires static repository validation, a Debian Trixie installer integration test, and a live-build configuration preflight before building in a clean Debian Trixie container. It then checks the generated ISO and checksum and publishes the files directly to a GitHub Release. The configuration preflight runs `bash build/build.sh --configure-only`, which executes `lb config` and stops before `lb build`. It does not use short-lived Actions artifacts.

GitHub limits each release asset to less than 2 GiB. If the generated ISO is larger, the workflow splits it into numbered parts below that limit and publishes a reassembly script plus the SHA-256 file. Download all parts into one directory and run `bash reassemble-rivet-iso.sh`; the script joins the parts and verifies the checksum.

## Calamares wiki

The installer slideshow now tells the story of Rivet Linux in two readable columns. It covers the Debian/XFCE foundation, visual identity and bundled tools, lessons from the #102 startup failure, and next verification steps. The text uses a normal font size and can scroll vertically on smaller installer windows. The previous mouse-controlled Rivet Pong prototype has been removed.

## Chip Fixs

Chip Fixs is packaged as a GTK 3 desktop application, with its diagnostic core separated for unit testing. The package list includes `dmidecode`, `smartmontools`, `lm-sensors`, and `mesa-utils` to make richer hardware information available. System checks are read-only; the limited audio and NetworkManager restarts require confirmation, and NetworkManager also requires administrative authorization. Advanced memory inventory and SMART health checks are explicit, read-only operations that request authorization.

The repository validation workflow compiles the app and core and runs `scripts/test-chip-fixs.py`. These checks do not replace launching the app in an XFCE session and testing it inside a newly generated ISO. Do not mark Chip Fixs complete until that runtime test succeeds.

## Latest generated ISO

The latest published image remains [**#102**](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102), named `Rivet-Linux.amd64.iso`. During a real user test, the custom startup splash failed and the system did not complete the desktop handoff. The green build checks and BIOS/UEFI boot-catalog checks did not detect this runtime problem.

The source correction removes the splash packages, custom theme, status bridge and installer configuration stage; it restores visible text boot status, trims the live dock, and replaces Rivet Pong with the installer wiki. This source revision has not yet been built into a replacement ISO. No ISO is built on normal pushes, and a new build still requires explicit user authorization.

## Scope

This is a development/test image, not a stable release. Build-time checks passing does not prove that the desktop or installer work after boot. Boot in UEFI and BIOS VMs, first login, wallpaper cycling, Chip Fixs UI and repair confirmation, Calamares installation, first boot after installation, networking, audio, and package updates still require runtime testing.
