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

The Build Rivet ISO workflow validates the repository and builds the ISO in a clean Debian Trixie container for pull requests that change build inputs. This lets CI catch build failures before a change is merged. Pull-request builds upload the ISO and checksum as a temporary artifact retained for one day; they do not publish a release.

After a successful build on `main`, the workflow publishes the ISO and checksum as a GitHub pre-release marked as a development build. A manual run on a non-`main` branch builds and validates the ISO without publishing a release.

The build, checksum validation, artifact upload, and release publication are separate steps. Check the failed step in the workflow log before deciding which part failed.

## Scope

This produces a development/test image, not a release. Boot, installer, first-login, hardware, and upgrade testing are still required before the project can call the ISO usable.
