#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PACKAGE_LIST="build/config/package-lists/rivet.list.chroot"
BRANDING_HOOK="build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot"
CHIP_DIR="build/config/includes.chroot/usr/share/rivet/chip"
WELCOME_APP="build/config/includes.chroot/usr/bin/rivet-welcome"
WELCOME_AUTOSTART="build/config/includes.chroot/etc/xdg/autostart/rivet-welcome.desktop"
WELCOME_LAUNCHER="build/config/includes.chroot/usr/share/applications/rivet-welcome.desktop"

required_files=(
  README.md AGENTS.md CONTRIBUTING.md
  build/README.md build/build.sh
  "$BRANDING_HOOK" "$PACKAGE_LIST" "$WELCOME_APP"
  "$WELCOME_AUTOSTART" "$WELCOME_LAUNCHER"
  "$CHIP_DIR/README.md"
  .github/workflows/build-iso.yml .github/workflows/validate.yml
  config/README.md scripts/README.md
  docs/philosophy.md docs/architecture.md docs/roadmap.md docs/visual-assets.md
)

echo "==> Checking required files..."
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    echo "ERROR: missing required file: $file" >&2
    exit 1
  }
done

echo "==> Checking shell syntax..."
bash -n build/build.sh
bash -n "$BRANDING_HOOK"
bash -n scripts/validate-repo.sh

echo "==> Checking Python syntax..."
PYTHONPYCACHEPREFIX=/tmp/rivet-pycache python3 -m py_compile "$WELCOME_APP"

echo "==> Checking package list..."
mapfile -t packages < <(sed '/^[[:space:]]*$/d; /^[[:space:]]*#/d' "$PACKAGE_LIST")
[[ ${#packages[@]} -gt 0 ]] || {
  echo "ERROR: package list is empty." >&2
  exit 1
}

if printf '%s\n' "${packages[@]}" | grep -qvE '^[a-z0-9][a-z0-9+.-]*$'; then
  echo "ERROR: package list contains an invalid package name." >&2
  printf '%s\n' "${packages[@]}" >&2
  exit 1
fi

duplicates="$(printf '%s\n' "${packages[@]}" | sort | uniq -d)"
if [[ -n "$duplicates" ]]; then
  echo "ERROR: duplicate package names found:" >&2
  printf '%s\n' "$duplicates" >&2
  exit 1
fi

require_package() {
  local package="$1"
  grep -Fxq "$package" "$PACKAGE_LIST" || {
    echo "ERROR: required package is missing: $package" >&2
    exit 1
  }
}

echo "==> Checking required packages..."
for package in \
  xfce4 thunar lightdm lightdm-gtk-greeter xserver-xorg \
  network-manager network-manager-gnome pipewire pipewire-pulse wireplumber \
  firefox-esr calamares calamares-settings-debian sudo \
  python3-gi gir1.2-gtk-3.0; do
  require_package "$package"
done

echo "==> Checking build and branding identity..."
for setting in \
  '--distribution trixie' \
  '--architectures amd64' \
  '--binary-images iso-hybrid' \
  '--iso-application "Rivet Linux"' \
  '--iso-publisher "Rivet Linux Project"' \
  '--iso-volume "RIVET_LINUX"'; do
  grep -Fq -- "$setting" build/build.sh || {
    echo "ERROR: build identity setting missing: $setting" >&2
    exit 1
  }
done
grep -Fq 'productName: Rivet Linux' "$BRANDING_HOOK"
grep -Fq 'shortProductName: Rivet' "$BRANDING_HOOK"
grep -Fq 'bootloaderEntryName: Rivet Linux' "$BRANDING_HOOK"
grep -Fq 'name: Build Rivet ISO' .github/workflows/build-iso.yml
grep -Fq 'name: Publish ISO as a GitHub Release' .github/workflows/build-iso.yml
grep -Fq 'tag_name: rivet-build-' .github/workflows/build-iso.yml
grep -Fq 'name: Validate Rivet' .github/workflows/validate.yml

echo "==> Checking required visual assets..."
for asset in \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-waves.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-factory.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-chip.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-prism.jpeg \
  build/config/includes.chroot/etc/calamares/branding/rivet/rivet.logo.png; do
  [[ -s "$asset" ]] || {
    echo "ERROR: missing or empty Rivet asset: $asset" >&2
    exit 1
  }
done

echo "==> Checking Chip and launcher integration..."
chip_count="$(find "$CHIP_DIR" -maxdepth 1 -type f -name '*.png' | wc -l)"
if [[ "$chip_count" -lt 5 ]]; then
  echo "ERROR: expected at least five Chip PNG poses, found $chip_count." >&2
  exit 1
fi

grep -Fq 'Exec=/usr/bin/rivet-welcome' "$WELCOME_AUTOSTART"
grep -Fq 'OnlyShowIn=XFCE;' "$WELCOME_AUTOSTART"
grep -Fq 'Exec=/usr/bin/rivet-welcome --show-again' "$WELCOME_LAUNCHER"
grep -Fq 'Icon=rivet' "$WELCOME_LAUNCHER"
grep -Fq 'Welcome to Rivet Linux' "$WELCOME_APP"
grep -Fq 'CHIP_DIR = "/usr/share/rivet/chip"' "$WELCOME_APP"
grep -Fq -- '--show-again' "$WELCOME_APP"
grep -Fq 'branding: rivet' "$BRANDING_HOOK"
grep -Fq 'calamares-install-debian' "$BRANDING_HOOK"
grep -Fq 'Icon=rivet' "$BRANDING_HOOK"

echo "==> Checking documentation language..."
if grep -RniE '(^|[[:space:]])(para|uma|das|dos|não|aqui|deve|somente|pacotes|instalar|teste|experiência|configuração|usuário)([[:space:]]|$)' \
  README.md AGENTS.md CONTRIBUTING.md docs build/README.md build/config config scripts .github/pull_request_template.md \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.sh' --exclude-dir='.git' \
  >/tmp/rivet-portuguese-check.txt 2>/dev/null; then
  echo "ERROR: possible Portuguese text found in project documentation:" >&2
  cat /tmp/rivet-portuguese-check.txt >&2
  exit 1
fi

echo "==> Repository validation passed."
