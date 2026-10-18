#!/usr/bin/python3
"""Preflight the real Debian Trixie Calamares installation pipeline."""

import argparse
import re
import stat
import sys
import tempfile
from pathlib import Path

REQUIRED_SHOW_MODULES = (
    "welcome", "locale", "keyboard", "partition", "users", "summary",
)

# Match the Debian Trixie settings sequence. Extra upstream steps are allowed,
# but disk setup, squashfs extraction, account setup, GRUB and source cleanup
# must exist in the right order.
REQUIRED_EXEC_ORDER = (
    "partition",
    "mount",
    "unpackfs",
    "luksbootkeyfile",
    "dpkg-unsafe-io",
    "sources-media",
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
    "plymouthcfg",
    "initramfscfg",
    "initramfs",
    "dpkg-unsafe-io-undo",
    "sources-media-unmount",
    "sources-final",
    "umount",
)

REQUIRED_MODULE_CONFIGS = (
    "bootloader.conf",
    "displaymanager.conf",
    "finished.conf",
    "fstab.conf",
    "luksopenswaphookcfg.conf",
    "machineid.conf",
    "mount.conf",
    "packages.conf",
    "unpackfs.conf",
    "users.conf",
    "welcome.conf",
)

REQUIRED_HELPERS = (
    "/usr/share/calamares/helpers/calamares-bootloader-config",
    "/usr/share/calamares/helpers/calamares-sources-media",
    "/usr/share/calamares/helpers/calamares-sources-final",
)

REQUIRED_MODULE_DESCRIPTORS = (
    "/usr/lib/calamares/modules/bootloader-config/module.desc",
    "/usr/lib/calamares/modules/dpkg-unsafe-io/module.desc",
    "/usr/lib/calamares/modules/dpkg-unsafe-io-undo/module.desc",
    "/usr/lib/calamares/modules/sources-final/module.desc",
    "/usr/lib/calamares/modules/sources-media-unmount/module.desc",
    "/usr/lib/calamares/modules/sources-media/module.desc",
)

REQUIRED_EXECUTABLES = (
    "/usr/bin/calamares",
    "/usr/bin/calamares-install-debian",
    "/usr/bin/pkexec",
    "/usr/bin/sudo",
    "/usr/bin/xhost",
    "/usr/bin/xprop",
    "/usr/bin/xwininfo",
    "/usr/bin/rsync",
    "/usr/bin/unsquashfs",
)


def setting(text, key):
    match = re.search(
        rf"(?m)^{re.escape(key)}:[ \t]*([^#\r\n]+)",
        text,
    )
    return match.group(1).strip().strip("\"'") if match else None


def parse_sequence(text):
    """Read Calamares show/exec phases without relying on optional PyYAML."""
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


def is_executable(path):
    try:
        return path.is_file() and bool(path.stat().st_mode & 0o111)
    except OSError:
        return False


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

    module_search = re.search(r"(?m)^modules-search:[ \t]*\[([^\]]+)\]", settings_text)
    if not module_search or "local" not in module_search.group(1) or "/usr/lib/calamares/modules" not in module_search.group(1):
        problems.append(
            "settings.conf must search the packaged Calamares modules using local and /usr/lib/calamares/modules."
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
        missing = [module for module in REQUIRED_EXEC_ORDER if module not in exec_phases[0]]
        problems.append(
            "installation sequence is incomplete or out of order; required stages missing: "
            + (", ".join(missing) if missing else "required stages are out of order")
        )

    exec_index = next(
        (index for index, phase in enumerate(phases) if phase["kind"] == "exec"),
        None,
    )
    if exec_index is None or not any(
        index > exec_index
        and phase["kind"] == "show"
        and "finished" in phase["modules"]
        for index, phase in enumerate(phases)
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
            'destination: ""',
        ):
            if required not in unpackfs:
                problems.append(
                    f"unpackfs.conf does not extract the live system to the target root (missing {required!r})."
                )

    bootloader_path = modules_dir / "bootloader.conf"
    if bootloader_path.is_file():
        bootloader = bootloader_path.read_text(encoding="utf-8", errors="replace")
        for required in (
            'efiBootLoader: "grub"',
            'grubInstall: "grub-install"',
            'grubMkconfig: "grub-mkconfig"',
            'grubCfg: "/boot/grub/grub.cfg"',
            "installEFIFallback: true",
        ):
            if required not in bootloader:
                problems.append(
                    f"bootloader.conf is missing required GRUB/UEFI setting: {required}"
                )

    mount_path = modules_dir / "mount.conf"
    if mount_path.is_file():
        mount_config = mount_path.read_text(encoding="utf-8", errors="replace")
        for required in (
            "extraMounts:",
            "mountPoint: /proc",
            "mountPoint: /sys",
            "mountPoint: /dev",
            "mountPoint: /run",
            "mountPoint: /run/udev",
            "mountPoint: /dev/pts",
            "mountPoint: /sys/firmware/efi/efivars",
        ):
            if required not in mount_config:
                problems.append(
                    f"mount.conf is missing a required target mount: {required}"
                )

    users_path = modules_dir / "users.conf"
    if users_path.is_file():
        users_config = users_path.read_text(encoding="utf-8", errors="replace")
        if setting(users_config, "sudoersGroup") != "sudo":
            problems.append("users.conf must grant the created account administrative access through sudo.")
        if not re.search(r"(?m)^\s+-\s+sudo\s*(?:#.*)?$", users_config):
            problems.append("users.conf defaultGroups must include sudo.")

        requirements = re.search(
            r"(?ms)^passwordRequirements:[ \\t]*\\n(.*?)(?=^[A-Za-z][A-Za-z0-9_-]*:)",
            users_config,
        )
        if not requirements:
            problems.append("users.conf must define passwordRequirements.")
        else:
            password_policy = requirements.group(1)
            if not re.search(r"(?m)^\\s+minLength:[ \\t]*1(?:[ \\t]*#.*)?$", password_policy):
                problems.append("users.conf must allow any non-empty password (minLength: 1).")
            if not re.search(r"(?m)^\\s+maxLength:[ \\t]*-1(?:[ \\t]*#.*)?$", password_policy):
                problems.append("users.conf must not impose a maximum password length.")
            for setting_text in ("- minlen=0", "- minclass=0"):
                if setting_text not in password_policy:
                    problems.append(f"users.conf password policy is missing {setting_text!r}.")
        if setting(users_config, "allowWeakPasswords") != "true":
            problems.append("users.conf must permit weak passwords rather than rejecting them.")
        if setting(users_config, "allowWeakPasswordsDefault") != "true":
            problems.append("users.conf must enable the allow-weak-passwords option by default.")

    packages_path = modules_dir / "packages.conf"
    if packages_path.is_file():
        packages_config = packages_path.read_text(encoding="utf-8", errors="replace")
        if setting(packages_config, "backend") != "apt":
            problems.append("packages.conf must use APT on the Debian target.")
        for package in ("live-boot", "live-config", "live-tools", "calamares-settings-debian"):
            if not re.search(rf"(?m)^\s*-\s*['\"]?{re.escape(package)}['\"]?\s*(?:#.*)?$", packages_config):
                problems.append(
                    f"packages.conf must remove the live-only/installer package {package!r} from the installed system."
                )

    welcome_path = modules_dir / "welcome.conf"
    if welcome_path.is_file():
        welcome_config = welcome_path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"(?m)^\s*requiredStorage:\s*15(?:\.0+)?\s*(?:#.*)?$", welcome_config):
            problems.append("welcome.conf must enforce the Debian installer minimum of 15 GB storage.")

    for path in REQUIRED_HELPERS:
        absolute = file_at(path)
        if not is_executable(absolute):
            problems.append(f"missing or non-executable Calamares helper: {absolute}")

    for path in REQUIRED_MODULE_DESCRIPTORS:
        absolute = file_at(path)
        if not absolute.is_file() or absolute.stat().st_size == 0:
            problems.append(f"missing Calamares module descriptor: {absolute}")

    for path in REQUIRED_EXECUTABLES:
        absolute = file_at(path)
        if not is_executable(absolute):
            problems.append(f"missing or non-executable installer dependency: {absolute}")

    return problems


def sample_settings():
    return f"""---
modules-search: [ local, /usr/lib/calamares/modules ]
oem-setup: false
disable-cancel-during-exec: true
sequence:
- show:
{''.join('  - ' + item + chr(10) for item in REQUIRED_SHOW_MODULES)}- exec:
{''.join('  - ' + item + chr(10) for item in REQUIRED_EXEC_ORDER)}- show:
  - finished
branding: rivet
prompt-install: true
dont-chroot: false
"""


def write_fixture_file(root, path, content, executable=False):
    target = root / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    if executable:
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def self_test():
    with tempfile.TemporaryDirectory(prefix="rivet-installer-check-") as temp:
        root = Path(temp)
        (root / "etc/calamares/modules").mkdir(parents=True)
        (root / "usr/bin").mkdir(parents=True)

        write_fixture_file(root, "/etc/calamares/settings.conf", sample_settings())
        write_fixture_file(
            root, "/etc/calamares/modules/unpackfs.conf",
            'unpack:\n    - source: "/run/live/medium/live/filesystem.squashfs"\n'
            '      sourcefs: "squashfs"\n      destination: ""\n',
        )
        write_fixture_file(
            root, "/etc/calamares/modules/bootloader.conf",
            'efiBootLoader: "grub"\ngrubInstall: "grub-install"\n'
            'grubMkconfig: "grub-mkconfig"\ngrubCfg: "/boot/grub/grub.cfg"\n'
            'installEFIFallback: true\n',
        )
        write_fixture_file(
            root, "/etc/calamares/modules/mount.conf",
            'extraMounts:\n'
            ' - device: proc\n   mountPoint: /proc\n'
            ' - device: sys\n   mountPoint: /sys\n'
            ' - device: /dev\n   mountPoint: /dev\n'
            ' - device: tmpfs\n   mountPoint: /run\n'
            ' - device: /run/udev\n   mountPoint: /run/udev\n'
            ' - device: /dev/pts\n   mountPoint: /dev/pts\n'
            ' - device: efivarfs\n   mountPoint: /sys/firmware/efi/efivars\n',
        )
        write_fixture_file(
            root, "/etc/calamares/modules/users.conf",
            'defaultGroups:\n - cdrom\n - sudo\nsudoersGroup: sudo\n'
            'passwordRequirements:\n    minLength: 1\n    maxLength: -1\n'
            '    libpwquality:\n        - minlen=0\n        - minclass=0\n'
            'allowWeakPasswords: true\nallowWeakPasswordsDefault: true\n',
        )
        write_fixture_file(
            root, "/etc/calamares/modules/packages.conf",
            'backend: apt\noperations:\n - remove:\n'
            "   - 'live-boot'\n   - 'live-config'\n   - 'live-tools'\n"
            "   - 'calamares-settings-debian'\n",
        )
        write_fixture_file(
            root, "/etc/calamares/modules/welcome.conf",
            'requirements:\n requiredStorage: 15\n',
        )

        for name in REQUIRED_MODULE_CONFIGS:
            path = "/etc/calamares/modules/" + name
            target = root / path.lstrip("/")
            if not target.exists():
                write_fixture_file(root, path, "# test fixture\n")

        for path in REQUIRED_HELPERS:
            write_fixture_file(root, path, "#!/bin/sh\nexit 0\n", executable=True)

        for path in REQUIRED_MODULE_DESCRIPTORS:
            write_fixture_file(root, path, '---\ntype: "job"\nname: fixture\n')

        for path in REQUIRED_EXECUTABLES:
            write_fixture_file(root, path, "#!/bin/sh\nexit 0\n", executable=True)

        problems = check_root(root)
        if problems:
            raise AssertionError("valid Debian Trixie fixture rejected: " + "; ".join(problems))

        settings_file = root / "etc/calamares/settings.conf"
        broken = settings_file.read_text(encoding="utf-8").replace("  - unpackfs\n", "")
        settings_file.write_text(broken, encoding="utf-8")
        problems = check_root(root)
        if not any("installation sequence is incomplete" in problem for problem in problems):
            raise AssertionError("missing unpackfs stage was not detected")

        settings_file.write_text(sample_settings(), encoding="utf-8")
        write_fixture_file(
            root, "/etc/calamares/modules/unpackfs.conf",
            'unpack:\n    - source: "/wrong/path/filesystem.squashfs"\n'
            '      sourcefs: "squashfs"\n      destination: ""\n',
        )
        problems = check_root(root)
        if not any("unpackfs.conf does not extract" in problem for problem in problems):
            raise AssertionError("incorrect live filesystem source was not detected")

        write_fixture_file(
            root, "/etc/calamares/modules/unpackfs.conf",
            'unpack:\n    - source: "/run/live/medium/live/filesystem.squashfs"\n'
            '      sourcefs: "squashfs"\n      destination: ""\n',
        )
        write_fixture_file(
            root, "/etc/calamares/modules/packages.conf",
            'backend: apt\noperations:\n - remove:\n   - live-config\n   - live-tools\n'
            "   - 'calamares-settings-debian'\n",
        )
        problems = check_root(root)
        if not any("must remove the live-only" in problem for problem in problems):
            raise AssertionError("missing live-boot removal was not detected")

        write_fixture_file(
            root, "/etc/calamares/modules/packages.conf",
            'backend: apt\noperations:\n - remove:\n'
            "   - 'live-boot'\n   - 'live-config'\n   - 'live-tools'\n"
            "   - 'calamares-settings-debian'\n",
        )
        write_fixture_file(
            root, "/etc/calamares/modules/users.conf",
            'defaultGroups:\n - cdrom\n - sudo\nsudoersGroup: wheel\n',
        )
        problems = check_root(root)
        if not any("administrative access through sudo" in problem for problem in problems):
            raise AssertionError("missing sudo account configuration was not detected")

    print("Rivet installer pipeline tests passed: install order, squashfs extraction, live-package cleanup, admin account, GRUB/UEFI, and required helpers are checked.")


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

    print("Rivet installer pipeline verified: disk setup, live image extraction, user privileges, GRUB/UEFI, target package cleanup, repositories, and completion stages are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
