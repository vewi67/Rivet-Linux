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

The Build Rivet ISO workflow validates the repository first, builds in a clean Debian Trixie container, checks the generated ISO and checksum, then uploads the ISO and checksum as a short-lived artifact.

If the build succeeds but artifact upload fails, read the workflow log carefully: artifact storage quota and ISO compilation are separate stages. A failed upload does not mean the ISO itself failed to build.

## Scope

This produces a development/test image, not a release. Boot, installer, first-login, hardware, and upgrade testing are still required before the project can call the ISO usable.
