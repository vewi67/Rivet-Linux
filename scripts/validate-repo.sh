#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

required_files=(
  README.md
  AGENTS.md
  CONTRIBUTING.md
  build/build.sh
  build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot
  build/config/package-lists/tip.list.chroot
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
bash -n build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot
bash -n scripts/validate-repo.sh

echo "==> Checking package list..."
mapfile -t packages < <(
  sed '/^[[:space:]]*$/d; /^[[:space:]]*#/d' build/config/package-lists/tip.list.chroot
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

echo "==> Checking tracked build configuration..."
grep -q -- '--distribution trixie' build/build.sh
grep -q -- '--architectures amd64' build/build.sh
grep -q -- '--binary-images iso-hybrid' build/build.sh
grep -q '^calamares$' build/config/package-lists/tip.list.chroot
grep -q '^calamares-settings-debian$' build/config/package-lists/tip.list.chroot
grep -q '^lightdm-gtk-greeter$' build/config/package-lists/tip.list.chroot

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
  >/tmp/tip-portuguese-check.txt 2>/dev/null; then
  echo "ERROR: possible Portuguese text found in project documentation:" >&2
  cat /tmp/tip-portuguese-check.txt >&2
  exit 1
fi

echo "==> Repository validation passed."
