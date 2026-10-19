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

## Installer mini-game

The Calamares branding slideshow includes a lightweight Rivet Pong prototype written in QML. During installation, move the mouse to control the left paddle; the computer controls the right paddle, and the first side to score five points wins. The game's timer follows Calamares slideshow activation and stops when the installer leaves the slideshow. The QML has not yet been verified at runtime inside a generated ISO, so this remains a prototype until that test is completed.

## Chip Fixs

Chip Fixs is packaged as a GTK 3 desktop application, with its diagnostic core separated for unit testing. The package list includes `dmidecode`, `smartmontools`, `lm-sensors`, and `mesa-utils` to make richer hardware information available. System checks are read-only; the limited audio and NetworkManager restarts require confirmation, and NetworkManager also requires administrative authorization. Advanced memory inventory and SMART health checks are explicit, read-only operations that request authorization.

The repository validation workflow compiles the app and core and runs `scripts/test-chip-fixs.py`. These checks do not replace launching the app in an XFCE session and testing it inside a newly generated ISO. Do not mark Chip Fixs complete until that runtime test succeeds.

## Latest generated ISO

The latest published image is [**#102, Animated Boot Experience**](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102). It is published as `Rivet-Linux.amd64.iso` (1,773,174,784 bytes) together with its SHA-256 file, download notes, and the reassembly/verification script. SHA-256: `66f1fd8a37088e7649015036b5f7e2da9aab09d846a23008e66aebda6bc0b083`.

Build checks passed: repository validation, Debian Trixie package/Calamares integration, live-build configuration preflight, checksum verification, and explicit BIOS/UEFI El Torito boot-entry checks. The source tag points to the clean default-branch commit that supplies the build inputs. #101 has not yet been manually booted or installed in a VM; all post-boot behavior remains to be verified. Do not confuse the boot-catalog check with proof of a successful runtime boot.

No ISO is built on ordinary pushes. Build #102 is a one-time, explicitly authorized exception triggered only by the dedicated branch `rivet-iso102-authorized-once-20261019`; the workflow refuses to overwrite an existing `rivet-build-102` tag. All subsequent builds remain manual and require explicit `YES`, a positive unused release number, and all three pre-build checks to pass: repository validation, Debian Trixie package/installer integration, and live-build configuration preflight.

The custom Chip Fixs logo is included from `assets/chip-fixs/logo.png`, staged at `build/config/includes.chroot/usr/share/rivet/chip-fixs/logo.png`, and installed into the hicolor icon theme by the branding hook. The English-first locale hook and scripted Plymouth theme are in the source tree used to build #101; their appearance and behavior still need visual verification during VM testing.

## Scope

This is a development/test image, not a stable release. Build-time checks passing does not prove that the desktop or installer work after boot. Boot in UEFI and BIOS VMs, first login, wallpaper cycling, Chip Fixs UI and repair confirmation, Calamares installation, first boot after installation, networking, audio, and package updates still require runtime testing.
