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
    bash build/build.sh

The build script checks its required inputs, configures live-build for Debian Trixie amd64, builds the image, checks the ISO boot metadata, and writes a SHA-256 checksum beside the ISO.

Expected output:

    build/live-image-amd64.hybrid.iso
    build/live-image-amd64.hybrid.iso.sha256

The exact ISO filename is determined by live-build. Build state is managed by live-build; the script does not delete the tracked configuration directory.

## GitHub Actions

The Build Rivet ISO workflow validates the repository first, builds in a clean Debian Trixie container, checks the generated ISO and checksum, and publishes the files directly to a GitHub Release. It does not use short-lived Actions artifacts.

GitHub limits each release asset to less than 2 GiB. If the generated ISO is larger, the workflow splits it into numbered parts below that limit and publishes a reassembly script plus the SHA-256 file. Download all parts into one directory and run `bash reassemble-rivet-iso.sh`; the script joins the parts and verifies the checksum.

## Installer mini-game

The Calamares branding slideshow includes a lightweight Rivet Pong prototype written in QML. During installation, move the mouse to control the left paddle; the computer controls the right paddle, and the first side to score five points wins. The game's timer follows Calamares slideshow activation and stops when the installer leaves the slideshow. The QML has not yet been verified at runtime inside a generated ISO, so this remains a prototype until that test is completed.

## Chip Fixs

Chip Fixs is packaged as a GTK 3 desktop application, with its diagnostic core separated for unit testing. The package list includes `dmidecode`, `smartmontools`, `lm-sensors`, and `mesa-utils` to make richer hardware information available. System checks are read-only; the limited audio and NetworkManager restarts require confirmation, and NetworkManager also requires administrative authorization. Advanced memory inventory and SMART health checks are explicit, read-only operations that request authorization.

The repository validation workflow compiles the app and core and runs `scripts/test-chip-fixs.py`. These checks do not replace launching the app in an XFCE session and testing it inside a newly generated ISO. Do not mark Chip Fixs complete until that runtime test succeeds.

## Latest generated ISO

The latest build is **#98**, published in [GitHub Releases](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-98). The workflow completed repository validation, the Debian Trixie installer integration check, ISO format/El Torito boot-metadata inspection, and SHA-256 verification before publishing.

The custom Chip Fixs logo is included from `assets/chip-fixs/logo.png`, staged at `build/config/includes.chroot/usr/share/rivet/chip-fixs/logo.png`, and installed into the hicolor icon theme by the branding hook. The repository also now contains an English-first locale hook and a scripted Plymouth theme; these changes are **not included** in ISO #98 and need a newly authorized build plus VM verification.

## Scope

This is a development/test image, not a stable release. Build-time checks passing does not prove that the desktop or installer work after boot. Boot in UEFI and BIOS VMs, first login, wallpaper cycling, Chip Fixs UI and repair confirmation, Calamares installation, first boot after installation, networking, audio, and package updates still require runtime testing.
