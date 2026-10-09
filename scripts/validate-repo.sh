#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PACKAGE_LIST="build/config/package-lists/rivet.list.chroot"
BRANDING_HOOK="build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot"

required_files=(
  README.md
  AGENTS.md
  CONTRIBUTING.md
  build/build.sh
  "$BRANDING_HOOK"
  "$PACKAGE_LIST"
  .github/workflows/build-iso.yml
  .github/workflows/validate.yml
  build/README.md
  config/README.md
  scripts/README.md
  docs/philosophy.md
  docs/architecture.md
  docs/roadmap.md
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

echo "==> Checking package list..."
mapfile -t packages < <(
  sed '/^[[:space:]]*$/d; /^[[:space:]]*#/d' "$PACKAGE_LIST"
)

[[ ${#packages[@]} -gt 0 ]] || {
  echo "ERROR: package list is empty." >&2
  exit 1
}

if printf '%s\n' "${packages[@]}" | grep -qvE '^[a-z0-9][a-z0-9+.-]*$'; then
  echo "ERROR: package list contains an invalid package name." >&2
  printf '%s\n' "${packages[@]}" >&2
  exit 1
fi

if [[ $(printf '%s\n' "${packages[@]}" | sort | uniq -d | wc -l) -ne 0 ]]; then
  echo "ERROR: duplicate package names found." >&2
  printf '%s\n' "${packages[@]}" | sort | uniq -d >&2
  exit 1
fi

echo "==> Checking Rivet build identity..."
grep -q -- '--distribution trixie' build/build.sh
grep -q -- '--architectures amd64' build/build.sh
grep -q -- '--binary-images iso-hybrid' build/build.sh
grep -q -- '--iso-application "Rivet Linux"' build/build.sh
grep -q -- '--iso-publisher "Rivet Linux Project"' build/build.sh
grep -q -- '--iso-volume "RIVET_LINUX"' build/build.sh
grep -q 'productName: Rivet Linux' "$BRANDING_HOOK"
grep -q 'shortProductName: Rivet' "$BRANDING_HOOK"
grep -q 'bootloaderEntryName: Rivet Linux' "$BRANDING_HOOK"
grep -q '^name: Build Rivet ISO$' .github/workflows/build-iso.yml
grep -q 'name: rivet-iso' .github/workflows/build-iso.yml
grep -q '^name: Validate Rivet$' .github/workflows/validate.yml

echo "==> Checking required packages..."
grep -q '^calamares$' "$PACKAGE_LIST"
grep -q '^calamares-settings-debian$' "$PACKAGE_LIST"
grep -q '^lightdm-gtk-greeter$' "$PACKAGE_LIST"

echo "==> Checking Rivet visual assets..."
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
