#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
cd "$BUILD_DIR"

command -v lb >/dev/null 2>&1 || {
  echo "ERROR: live-build is not installed." >&2
  echo "Install the live-build package and try again." >&2
  exit 1
}

mkdir -p config/package-lists
mkdir -p config/includes.chroot/etc/skel

lb_args=(
  --distribution trixie
  --architectures amd64
  --archive-areas "main contrib non-free non-free-firmware"
  --binary-images iso-hybrid
  --bootappend-live "boot=live components username=rivet"
  --debian-installer none
  --apt-recommends true
  --memtest none
  --firmware-binary true
  --firmware-chroot true
  --iso-application "Rivet Linux"
  --iso-publisher "Rivet Linux Project"
  --iso-volume "RIVET_LINUX"
)

lb config "${lb_args[@]}"

echo "==> Building Rivet Linux..."
lb build

echo "==> Build complete."
ls -lh live-image-*.hybrid.iso
