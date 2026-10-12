#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
cd "$BUILD_DIR"

for command_name in lb xorriso file sha256sum; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "ERROR: required command '$command_name' is not installed." >&2
    echo "Install live-build, xorriso, file, and coreutils, then try again." >&2
    exit 1
  fi
done

PACKAGE_LIST="config/package-lists/rivet.list.chroot"
BRANDING_HOOK="config/hooks/normal/0100-configure-rivet-branding.hook.chroot"

[[ -s "$PACKAGE_LIST" ]] || {
  echo "ERROR: Rivet package list is missing or empty: $PACKAGE_LIST" >&2
  exit 1
}
[[ -s "$BRANDING_HOOK" ]] || {
  echo "ERROR: Rivet branding hook is missing or empty: $BRANDING_HOOK" >&2
  exit 1
}

mkdir -p config/package-lists config/includes.chroot/etc/skel

# live-build only executes executable hooks. Make every normal hook executable
# so local builds run the same image-configuration steps as CI, including the
# Calamares slideshow hook that repairs branding.desc and writes show.qml.
find config/hooks/normal -maxdepth 1 -type f -name '*.hook.chroot' -exec chmod 0755 {} +

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

echo "==> Configuring Rivet Linux for Debian Trixie (amd64)..."
lb config "${lb_args[@]}"

echo "==> Building Rivet Linux..."
lb build

shopt -s nullglob
images=(live-image-*.hybrid.iso)
if [[ ${#images[@]} -ne 1 ]]; then
  echo "ERROR: expected exactly one ISO, found ${#images[@]}." >&2
  printf '%s\n' "${images[@]}" >&2
  exit 1
fi

iso="${images[0]}"
[[ -s "$iso" ]] || {
  echo "ERROR: generated ISO is empty: $iso" >&2
  exit 1
}

echo "==> Checking ISO format..."
file "$iso"
xorriso -indev "$iso" -report_el_torito plain

checksum_file="$iso.sha256"
sha256sum "$iso" | tee "$checksum_file"

echo "==> Build and ISO checks completed."
ls -lh "$iso" "$checksum_file"
