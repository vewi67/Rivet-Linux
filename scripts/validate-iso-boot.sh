#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/validate-iso-boot.sh PATH_TO_ISO" >&2
  exit 2
fi

iso="$1"
if [[ ! -f "$iso" || ! -s "$iso" ]]; then
  echo "ERROR: ISO is missing or empty: $iso" >&2
  exit 1
fi

for command_name in file xorriso grep; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "ERROR: required ISO validation command '$command_name' is not installed." >&2
    exit 1
  fi
done

echo "==> Checking ISO file type:"
file "$iso"

echo "==> Inspecting El Torito boot entries:"
if ! boot_report="$(xorriso -indev "$iso" -report_el_torito plain 2>&1)"; then
  printf '%s\n' "$boot_report" >&2
  echo "ERROR: xorriso could not inspect the ISO boot catalog." >&2
  exit 1
fi
printf '%s\n' "$boot_report"

for platform in BIOS UEFI; do
  if ! grep -Eq "El Torito boot img[[:space:]]*:[[:space:]]*[0-9]+[[:space:]]+$platform[[:space:]]+y([[:space:]]|$)" <<<"$boot_report"; then
    echo "ERROR: ISO does not contain a bootable El Torito entry for $platform." >&2
    exit 1
  fi
done

echo "ISO boot validation passed: bootable BIOS and UEFI El Torito entries are present."
