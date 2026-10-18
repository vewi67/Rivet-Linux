#!/usr/bin/env python3
"""Behavioral tests for Rivet Welcome's live-versus-installed detection."""

import ast
import os
from pathlib import Path
import tempfile


REPOSITORY = Path(__file__).resolve().parents[1]
WELCOME_SOURCE = REPOSITORY / "build/config/includes.chroot/usr/bin/rivet-welcome"


def load_detector():
    tree = ast.parse(WELCOME_SOURCE.read_text(encoding="utf-8"), filename=str(WELCOME_SOURCE))
    function = next(
        (node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "is_live_session"),
        None,
    )
    if function is None:
        raise AssertionError("rivet-welcome must define is_live_session().")
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"Path": Path, "os": os}
    exec(compile(module, str(WELCOME_SOURCE), "exec"), namespace)
    return namespace["is_live_session"]


def main():
    detect = load_detector()
    with tempfile.TemporaryDirectory(prefix="rivet-welcome-mode-") as temporary:
        root = Path(temporary)
        cmdline = root / "cmdline"
        run_live = root / "run/live/medium"
        lib_live = root / "lib/live/mount/medium"

        cmdline.write_text("BOOT_IMAGE=/vmlinuz boot=live quiet splash\n", encoding="utf-8")
        assert detect(str(cmdline), str(run_live), str(lib_live)), (
            "boot=live in the kernel command line must identify the live session"
        )

        cmdline.write_text("BOOT_IMAGE=/vmlinuz quiet splash\n", encoding="utf-8")
        run_live.mkdir(parents=True)
        lib_live.mkdir(parents=True)

        # Leftover mount-point directories alone must not imply a live boot.
        assert not detect(str(cmdline), str(run_live), str(lib_live), lambda _path: False), (
            "empty live mount-point directories must not classify an installed system as live"
        )
        assert detect(str(cmdline), str(run_live), str(lib_live), lambda path: path == str(run_live)), (
            "an active /run live-medium mount should identify a live session"
        )
        assert detect(str(cmdline), str(run_live), str(lib_live), lambda path: path == str(lib_live)), (
            "an active /lib live-medium mount should identify a live session"
        )

        assert not detect(str(root / "missing-cmdline"), str(run_live), str(lib_live), lambda _path: False), (
            "missing optional live markers must fail closed to installed mode"
        )

    print("Rivet Welcome mode tests passed: live boot flag, both live mount markers, and installed mode.")


if __name__ == "__main__":
    main()
