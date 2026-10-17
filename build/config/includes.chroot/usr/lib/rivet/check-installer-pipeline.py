#!/usr/bin/python3
"""Validate that Rivet ships a complete, safety-checked Calamares install path."""

import argparse
import re
import sys
import tempfile
from pathlib import Path

REQUIRED_SHOW_MODULES = (
    "welcome",
    "locale",
    "keyboard",
    "partition",
    "users",
    "summary",
)

# This ordered subsequence describes the actual installation work. Debian may
# add helper modules between these stages; those are allowed and remain intact.
REQUIRED_EXEC_ORDER = (
    "partition",
    "mount",
    "unpackfs",
    "machineid",
    "fstab",
    "locale",
    "keyboard",
    "localecfg",
    "users",
    "displaymanager",
    "networkcfg",
    "hwclock",
    "services-systemd",
    "bootloader-config",
    "grubcfg",
    "bootloader",
    "packages",
    "initramfs",
    "umount",
)

REQUIRED_MODULE_CONFIGS = (
    "bootloader.conf",
    "displaymanager.conf",
    "fstab.conf",
    "mount.conf",
    "packages.conf",
    "unpackfs.conf",
    "users.conf",
)

REQUIRED_HELPERS = (
    "/usr/share/calamares/helpers/calamares-bootloader-config",
    "/usr/share/calamares/helpers/calamares-sources-media",
    "/usr/share/calamares/helpers/calamares-sources-final",
)

REQUIRED_EXECUTABLES = (
    "/usr/bin/calamares",
    "/usr/bin/calamares-install-debian",
    "/usr/bin/pkexec",
    "/usr/bin/sudo",
    "/usr/bin/xhost",
    "/usr/bin/xprop",
    "/usr/bin/xwininfo",
)

def setting(text, key):
    match = re.search(
        rf"(?m)^{re.escape(key)}:[ \t]*([^#\r\n]+)",
        text,
    )
    return match.group(1).strip().strip("\"'") if match else None


def parse_sequence(text):
    """Read Calamares show/exec phases without depending on PyYAML."""
    phases = []
    in_sequence = False
    current = None

    for line in text.splitlines():
        if not in_sequence:
            if re.match(r"^sequence:[ \t]*(?:#.*)?$", line):
                in_sequence = True
            continue

        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        phase_match = re.match(r"^-\s+(show|exec):\s*(?:#.*)?$", line)
        if phase_match:
            current = {"kind": phase_match.group(1), "modules": []}
            phases.append(current)
            continue

        # The next top-level setting marks the end of the sequence block.
        if line and not line[0].isspace() and not line.startswith("- "):
            break

        module_match = re.match(r"^\s+-\s+([A-Za-z0-9_@.-]+)\s*(?:#.*)?$", line)
        if current and module_match:
            current["modules"].append(module_match.group(1))

    return phases


def ordered_subsequence(actual, required):
    index = 0
    for module in actual:
        if index < len(required) and module == required[index]:
            index += 1
    return index == len(required)


def check_root(root):
    root = Path(root)
    problems = []

    def file_at(path):
        return root / path.lstrip("/")

    settings_path = file_at("/etc/calamares/settings.conf")
    if not settings_path.is_file():
        return [f"missing Calamares settings: {settings_path}"]

    settings_text = settings_path.read_text(encoding="utf-8", errors="replace")
    expected_settings = {
        "branding": "rivet",
        "oem-setup": "false",
        "dont-chroot": "false",
        "prompt-install": "true",
        "disable-cancel-during-exec": "true",
    }
    for key, expected in expected_settings.items():
        actual = setting(settings_text, key)
        if actual != expected:
            problems.append(
                f"settings.conf must declare {key}: {expected} (found {actual!r})"
            )

    phases = parse_sequence(settings_text)
    shows = [phase["modules"] for phase in phases if phase["kind"] == "show"]
    exec_phases = [phase["modules"] for phase in phases if phase["kind"] == "exec"]

    if not phases:
        problems.append("settings.conf has no readable Calamares sequence.")
    if not any(all(module in modules for module in REQUIRED_SHOW_MODULES) for modules in shows):
        problems.append(
            "the preparation UI must include welcome, locale, keyboard, partition, users, and summary."
        )

    if len(exec_phases) != 1:
        problems.append(
            f"expected one ordered installation exec phase, found {len(exec_phases)}."
        )
    elif not ordered_subsequence(exec_phases[0], REQUIRED_EXEC_ORDER):
        missing = [
            module for module in REQUIRED_EXEC_ORDER
            if module not in exec_phases[0]
        ]
        problems.append(
            "installation sequence is incomplete or out of order; missing required stages: "
            + (", ".join(missing) if missing else "required stages are out of order")
        )

    if not any(
        phase["kind"] == "show"
        and "finished" in phase["modules"]
        and phases.index(phase) > next(
            (i for i, item in enumerate(phases) if item["kind"] == "exec"),
            -1,
        )
        for phase in phases
    ):
        problems.append("a finished page must follow the installation phase.")

    modules_dir = file_at("/etc/calamares/modules")
    for name in REQUIRED_MODULE_CONFIGS:
        path = modules_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            problems.append(f"missing or empty Calamares module configuration: {path}")

    unpackfs_path = modules_dir / "unpackfs.conf"
    if unpackfs_path.is_file():
        unpackfs = unpackfs_path.read_text(encoding="utf-8", errors="replace")
        for required in (
            "/run/live/medium/live/filesystem.squashfs",
            'sourcefs: "squashfs"',
            "destination:",
        ):
            if required not in unpackfs:
                problems.append(
                    f"unpackfs.conf does not point at the live system image correctly (missing {required!r})."
                )

    bootloader_path = modules_dir / "bootloader.conf"
    if bootloader_path.is_file():
        bootloader = bootloader_path.read_text(encoding="utf-8", errors="replace")
        for required in (
            'efiBootLoader: "grub"',
            'grubInstall: "grub-install"',
            'grubMkconfig: "grub-mkconfig"',
            "installEFIFallback: true",
        ):
            if required not in bootloader:
                problems.append(
                    f"bootloader.conf is missing required GRUB/UEFI setting: {required}"
                )

    for path in REQUIRED_HELPERS:
        if not file_at(path).is_file():
            problems.append(f"missing Calamares helper: {file_at(path)}")

    for path in REQUIRED_EXECUTABLES:
        absolute = file_at(path)
        if not absolute.is_file() or not absolute.stat().st_mode & 0o111:
            problems.append(f"missing or non-executable installer dependency: {absolute}")

    return problems


def sample_settings():
    show = " ".join(REQUIRED_SHOW_MODULES)
    exec_phase = " ".join(REQUIRED_EXEC_ORDER)
    return f"""---
oem-setup: false
disable-cancel-during-exec: true
sequence:
- show:
  - welcome
  - locale
  - keyboard
  - partition
  - users
  - summary
- exec:
{''.join('  - ' + item + chr(10) for item in REQUIRED_EXEC_ORDER)}- show:
  - finished
branding: rivet
prompt-install: true
dont-chroot: false
"""


def self_test():
    with tempfile.TemporaryDirectory(prefix="rivet-installer-check-") as temp:
        root = Path(temp)
        (root / "etc/calamares/modules").mkdir(parents=True)
        (root / "usr/share/calamares/helpers").mkdir(parents=True)
        (root / "usr/bin").mkdir(parents=True)

        (root / "etc/calamares/settings.conf").write_text(
            sample_settings(), encoding="utf-8"
        )
        (root / "etc/calamares/modules/unpackfs.conf").write_text(
            'unpack:\n    - source: "/run/live/medium/live/filesystem.squashfs"\n'
            '      sourcefs: "squashfs"\n      destination: ""\n',
            encoding="utf-8",
        )
        (root / "etc/calamares/modules/bootloader.conf").write_text(
            'efiBootLoader: "grub"\ngrubInstall: "grub-install"\n'
            'grubMkconfig: "grub-mkconfig"\ninstallEFIFallback: true\n',
            encoding="utf-8",
        )
        for name in REQUIRED_MODULE_CONFIGS:
            path = root / "etc/calamares/modules" / name
            if not path.exists():
                path.write_text("# test fixture\n", encoding="utf-8")
        for path in REQUIRED_HELPERS:
            item = root / path.lstrip("/")
            item.write_text("# test fixture\n", encoding="utf-8")
        for path in REQUIRED_EXECUTABLES:
            item = root / path.lstrip("/")
            item.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            item.chmod(0o755)

        problems = check_root(root)
        if problems:
            raise AssertionError("valid installer fixture rejected: " + "; ".join(problems))

        settings_file = root / "etc/calamares/settings.conf"
        broken = settings_file.read_text(encoding="utf-8").replace("  - unpackfs\n", "")
        settings_file.write_text(broken, encoding="utf-8")
        problems = check_root(root)
        if not any("installation sequence is incomplete" in problem for problem in problems):
            raise AssertionError("missing unpackfs stage was not detected")

        settings_file.write_text(sample_settings(), encoding="utf-8")
        (root / "etc/calamares/modules/unpackfs.conf").write_text(
            'unpack:\n    - source: "/wrong/path/filesystem.squashfs"\n'
            '      sourcefs: "squashfs"\n      destination: ""\n',
            encoding="utf-8",
        )
        problems = check_root(root)
        if not any("unpackfs.conf does not point" in problem for problem in problems):
            raise AssertionError("incorrect live filesystem source was not detected")

    print("Rivet installer pipeline tests passed: missing install stages and an invalid system-image source are detected.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="/", help="Root directory of an installed/live Rivet system.")
    parser.add_argument("--self-test", action="store_true", help="Test the pipeline validator against a temporary fixture.")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        return 0

    problems = check_root(args.root)
    if problems:
        print("Rivet installer pipeline preflight FAILED:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print("Rivet installer pipeline verified: disk setup, live image extraction, system configuration, GRUB/UEFI boot, and completion stages are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
