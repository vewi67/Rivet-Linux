#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

required_files=(
  README.md
  AGENTS.md
  CONTRIBUTING.md
  build/build.sh
  build/config/package-lists/tip.list.chroot
  .github/workflows/build-iso.yml
)

echo "==> Checking required files..."
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || { echo "ERROR: missing required file: $file" >&2; exit 1; }
done

echo "==> Checking shell syntax..."
bash -n build/build.sh
bash -n scripts/validate-repo.sh

echo "==> Checking package list..."
mapfile -t packages < <(sed '/^[[:space:]]*$/d; /^[[:space:]]*#/d' build/config/package-lists/tip.list.chroot)
[[ ${#packages[@]} -gt 0 ]] || { echo "ERROR: package list is empty." >&2; exit 1; }

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

echo "==> Repository validation passed."
