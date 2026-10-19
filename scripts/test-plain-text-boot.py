#!/usr/bin/env python3
"""Regression checks for Rivet's plain-text boot, small dock and installer wiki."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_LIST = ROOT / "build/config/package-lists/rivet.list.chroot"
BUILD = ROOT / "build/build.sh"
BOOT_HOOK = ROOT / "build/config/hooks/normal/0200-configure-rivet-boot-and-locale.hook.chroot"
SLIDESHOW = ROOT / "build/config/includes.chroot/etc/calamares/branding/rivet/show.qml"
SLIDESHOW_HOOK = ROOT / "build/config/hooks/normal/0900-configure-rivet-calamares-slideshow.hook.chroot"
INSTALLER_CHECKER = ROOT / "build/config/includes.chroot/usr/lib/rivet/check-installer-pipeline.py"


def require(condition, message):
    if not condition:
        raise SystemExit(f"ERROR: {message}")


def main():
    package_names = [line.strip() for line in PACKAGE_LIST.read_text(encoding="utf-8").splitlines()]
    require("plymouth" not in package_names, "the Plymouth package must not be installed.")
    require("plymouth-themes" not in package_names, "the Plymouth themes package must not be installed.")

    build_script = BUILD.read_text(encoding="utf-8")
    boot_hook = BOOT_HOOK.read_text(encoding="utf-8")
    live_args = re.search(r'--bootappend-live "([^"]+)"', build_script)
    require(live_args is not None, "live boot arguments must be defined.")
    require("systemd.show_status=1" in live_args.group(1), "live boot must show systemd startup messages.")
    require("locales=en_US.UTF-8" in live_args.group(1), "live boot must keep the English-first locale.")
    require("quiet" not in live_args.group(1).split(), "quiet must not hide useful boot diagnostics.")
    require("splash" not in live_args.group(1).split(), "the graphical splash must not be requested.")
    require("plymouth-set-default-theme" not in boot_hook, "the locale hook must not configure a splash theme.")
    require("configure-plymouth" not in boot_hook and "generate-plymouth" not in boot_hook,
            "the locale hook must not call splash-specific helpers.")
    require('GRUB_CMDLINE_LINUX_DEFAULT=' in boot_hook and 'systemd.show_status=1' in boot_hook,
            "installed GRUB defaults must retain systemd status messages.")

    obsolete_files = (
        ROOT / "build/config/includes.chroot/usr/lib/rivet/generate-plymouth-smoke.py",
        ROOT / "build/config/includes.chroot/usr/lib/rivet/configure-plymouth-boot-status.py",
        ROOT / "build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.plymouth",
        ROOT / "build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.script",
        ROOT / "scripts/test-plymouth-theme.py",
    )
    require(not any(path.exists() for path in obsolete_files), "obsolete custom splash source files remain in the repository.")

    checker = INSTALLER_CHECKER.read_text(encoding="utf-8")
    sequence = checker.split("REQUIRED_EXEC_ORDER = (", 1)[1].split(")", 1)[0]
    require('"plymouthcfg"' not in sequence, "the installer check must not require the old splash stage.")
    require("must not run plymouthcfg" in checker, "the installer check must reject the old splash stage.")

    qml = SLIDESHOW.read_text(encoding="utf-8")
    for fragment in (
        'title: qsTr("Rivet Wiki")',
        'text: "RIVET WIKI"',
        "WHERE IT STARTED",
        "BUILDING THE SYSTEM",
        "WHAT WE LEARNED",
        "RELIABILITY FIRST",
        "WHAT COMES NEXT",
        "font.pixelSize: 15",
        "Flickable",
        "height: Math.max(120, parent.height - 124)",
    ):
        require(fragment in qml, f"the installer wiki is missing a readable section or layout: {fragment}")
    require("RIVET PONG" not in qml and "rivetPongField" not in qml and "gameTimer" not in qml,
            "the old installer minigame remains in the slideshow.")

    hook = SLIDESHOW_HOOK.read_text(encoding="utf-8")
    require("plymouthcfg" in hook and "sed -i -E" in hook,
            "the installer hook must remove the obsolete target configuration stage.")
    print("Plain-text boot and installer wiki checks passed.")


if __name__ == "__main__":
    main()
