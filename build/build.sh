#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build"
cd "$BUILD_DIR"

command -v lb >/dev/null 2>&1 || {
  echo "ERRO: live-build não está instalado."
  echo "Instale o pacote live-build e tente novamente."
  exit 1
}

mkdir -p config/package-lists
mkdir -p config/includes.chroot/etc/skel

lb config \
  --distribution trixie \
  --architectures amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components username=tip" \
  --debian-installer none \
  --apt-recommends true \
  --memtest none \
  --firmware-binary true \
  --firmware-chroot true

echo "==> Construindo Tip..."
lb build

echo "==> Build concluído."
ls -lh live-image-*.hybrid.iso
