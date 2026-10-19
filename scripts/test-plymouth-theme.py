#!/usr/bin/env python3
"""Regression checks for Rivet's two-stage Plymouth startup animation."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.script"
THEME_CONFIG = ROOT / "build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.plymouth"
BOOT_HOOK = ROOT / "build/config/hooks/normal/0200-configure-rivet-boot-and-locale.hook.chroot"
GENERATOR = ROOT / "build/config/includes.chroot/usr/lib/rivet/generate-plymouth-smoke.py"
BOOT_STATUS_CONFIGURATOR = ROOT / "build/config/includes.chroot/usr/lib/rivet/configure-plymouth-boot-status.py"
BUILD = ROOT / "build/build.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"ERROR: {message}")


def main() -> int:
    theme = THEME.read_text(encoding="utf-8")
    theme_config = THEME_CONFIG.read_text(encoding="utf-8")
    boot_hook = BOOT_HOOK.read_text(encoding="utf-8")
    build_script = BUILD.read_text(encoding="utf-8")

    required_theme_fragments = (
        'phase = "logs";',
        'Image.Text("RIVET LINUX  /  BOOT SEQUENCE"',
        'Image.Text("› " + log.lines[index],',
        'log.opacity[index] += 0.12;',
        'log.offset[index] -= 2.0;',
        'Plymouth.SetUpdateStatusFunction(update_status_callback);',
        'Plymouth.SetDisplayMessageFunction(message_callback);',
        'Plymouth.SetBootProgressFunction(progress_callback);',
        'Plymouth.SetQuitFunction(quit_callback);',
        'Image("smoke-0.png")',
        'Image("smoke-7.png")',
        'Welcome to Rivet Linux',
        'boot_progress >= 0.90',
    )
    for fragment in required_theme_fragments:
        require(fragment in theme, f"Plymouth theme is missing required behavior: {fragment}")

    require("ModuleName=script" in theme_config, "Rivet must continue using Plymouth's script plugin.")
    require("SetUpdateStatusFunction" not in theme_config, "Plymouth callbacks belong in the script, not .plymouth metadata.")
    require("systemd.show_status=1" in build_script, "The live kernel command line must enable systemd startup statuses.")
    require("systemd.show_status=1" in boot_hook, "Installed GRUB defaults must enable systemd startup statuses.")
    require("generate-plymouth-smoke.py" in boot_hook, "Image configuration must generate smoke frames.")
    require("configure-plymouth-boot-status.py" in boot_hook, "Image configuration must bridge initramfs log messages into Plymouth.")
    require(BOOT_STATUS_CONFIGURATOR.is_file(), "Plymouth boot-status configurator is missing.")
    require(
        boot_hook.index('python3 "$SMOKE_GENERATOR" "$THEME_DIR"')
        < boot_hook.index("plymouth-set-default-theme -R rivet"),
        "Smoke frames must be generated before the initramfs is rebuilt.",
    )
    require("Let us Do the Magic" not in theme, "The legacy tagline animation must be removed.")
    require("logo.base_image.Rotate" not in theme, "The legacy spinning logo must be removed.")
    require("quiet splash systemd.show_status=1 locales=en_US.UTF-8" in build_script, "Live boot arguments are inconsistent.")

    # Exercise the initramfs log bridge against a minimal Debian-style function
    # file. This checks safe insertion and that reruns do not duplicate it.
    with tempfile.TemporaryDirectory(prefix="rivet-plymouth-status-") as temporary:
        functions_file = Path(temporary) / "functions"
        original_functions = (
            "# -*- shell-script -*-\n"
            "_log_msg()\n"
            "{\n"
            '\tif [ "${quiet?}" = "y" ]; then return; fi\n'
            '\tprintf "$@"\n'
            "}\n"
        )
        functions_file.write_text(original_functions, encoding="utf-8")
        for _ in range(2):
            subprocess.run(
                [sys.executable, str(BOOT_STATUS_CONFIGURATOR), str(functions_file)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        patched_functions = functions_file.read_text(encoding="utf-8")
        require(
            patched_functions.count("# RIVET_PLYMOUTH_STATUS_BRIDGE_BEGIN") == 1
            and patched_functions.count("# RIVET_PLYMOUTH_STATUS_BRIDGE_END") == 1,
            "The initramfs status bridge must be inserted exactly once.",
        )
        require(
            'plymouth update --status="$_rivet_status"' in patched_functions,
            "Initramfs status messages must be forwarded through plymouth update --status.",
        )
        require(
            patched_functions.index("# RIVET_PLYMOUTH_STATUS_BRIDGE_BEGIN")
            < patched_functions.index('if [ "${quiet?}" = "y" ]; then return; fi'),
            "Quiet boot must not suppress status forwarding before it reaches Plymouth.",
        )

        malformed_file = Path(temporary) / "malformed-functions"
        malformed_file.write_text("# no compatible _log_msg function\n", encoding="utf-8")
        failed_patch = subprocess.run(
            [sys.executable, str(BOOT_STATUS_CONFIGURATOR), str(malformed_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        require(failed_patch.returncode != 0, "The status bridge must reject unknown initramfs-tools layouts.")
        require(
            malformed_file.read_text(encoding="utf-8") == "# no compatible _log_msg function\n",
            "A failed status bridge must leave the target file unchanged.",
        )

    with tempfile.TemporaryDirectory(prefix="rivet-plymouth-smoke-") as temporary:
        subprocess.run(
            [sys.executable, str(GENERATOR), temporary],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        paths = [Path(temporary) / f"smoke-{frame}.png" for frame in range(8)]
        frames = []
        for path in paths:
            require(path.is_file() and path.stat().st_size > 0, f"Generated frame is missing: {path.name}")
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                require(image.mode == "RGBA", f"{path.name} must keep a transparent background.")
                require(image.size == (720, 300), f"{path.name} has unexpected dimensions: {image.size}.")
                frames.append(image.convert("RGBA").tobytes())

        require(len(set(frames)) > 1, "Smoke frames must differ to provide actual animation.")

    print("Plymouth tests passed: live boot-status callbacks, legacy-animation removal, smoke-frame generation and branding handoff.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
