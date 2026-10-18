#!/usr/bin/env python3
"""Static and behavioral tests for the installed Rivet welcome center."""

import ast
import os
from pathlib import Path
import tempfile


REPOSITORY = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY / "build/config/includes.chroot/usr/bin/rivet-welcome-center"


def load_function(tree, name):
    function = next(
        (
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == name
        ),
        None,
    )
    if function is None:
        raise AssertionError(f"{APP_PATH} must define {name}().")
    module = ast.Module(body=[function], type_ignores=[])
    namespace = {"Path": Path, "os": os}
    exec(compile(module, str(APP_PATH), "exec"), namespace)
    return namespace[name]


def load_settings(tree):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SETTINGS_GROUPS"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("The welcome center must define a static SETTINGS_GROUPS catalog.")


def main():
    source = APP_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(APP_PATH))
    detect = load_function(tree, "is_live_session")
    groups = load_settings(tree)

    titles = []
    categories = set()
    for category, entries in groups:
        categories.add(category)
        assert entries, f"Settings category {category!r} must not be empty."
        for entry in entries:
            assert len(entry) == 4, f"Invalid settings entry: {entry!r}"
            title, description, icon, command = entry
            assert title and description and icon and command, f"Incomplete settings entry: {entry!r}"
            assert isinstance(command, tuple) and command[0], f"Invalid command for {title!r}"
            titles.append(title.casefold())

    assert len(titles) == len(set(titles)), "Settings card titles must be unique."
    assert {"Personalization", "Devices & Input", "Connectivity", "Apps & System", "Rivet"} <= categories
    expected = {
        "appearance & themes", "desktop & wallpaper", "display & monitors",
        "window manager tweaks", "keyboard", "mouse & touchpad", "power & battery",
        "accessibility", "file associations", "advanced settings", "sound", "network",
        "bluetooth", "notifications", "software & updates", "rivet atmosphere",
        "chip fixs",
    }
    assert expected <= set(titles), f"Missing settings cards: {sorted(expected - set(titles))}"
    assert "if is_live_session():" in source, "The installed-only app must refuse to open in a live session."
    assert 'APP_NAME = "Welcome to Rivet"' in source
    assert "Gtk.SearchEntry()" in source, "The settings page should have searchable settings."
    assert "Gtk.StackSidebar()" in source, "The app should provide its category navigation."
    assert "mark_welcome_seen()" in source, "Dismissing the app should persist the first-run choice."

    with tempfile.TemporaryDirectory(prefix="rivet-welcome-center-") as temporary:
        root = Path(temporary)
        cmdline = root / "cmdline"
        run_live = root / "run/live/medium"
        lib_live = root / "lib/live/mount/medium"

        cmdline.write_text("BOOT_IMAGE=/vmlinuz boot=live quiet splash\n", encoding="utf-8")
        assert detect(str(cmdline), str(run_live), str(lib_live)), "boot=live must be detected."

        cmdline.write_text("BOOT_IMAGE=/vmlinuz quiet splash\n", encoding="utf-8")
        run_live.mkdir(parents=True)
        assert detect(str(cmdline), str(run_live), str(lib_live)), "/run/live/medium must be detected."

        run_live.rmdir()
        lib_live.mkdir(parents=True)
        assert detect(str(cmdline), str(run_live), str(lib_live)), "/lib/live/mount/medium must be detected."

        lib_live.rmdir()
        assert not detect(str(cmdline), str(run_live), str(lib_live)), (
            "An installed system without live markers must be classified as non-live."
        )
        assert not detect(str(root / "missing-cmdline"), str(run_live), str(lib_live)), (
            "Missing optional markers must not falsely classify the system as live."
        )

    print(
        "Rivet welcome center tests passed: installed-only guard, live detection, "
        f"{len(titles)} unique settings cards across {len(categories)} categories, search and navigation."
    )


if __name__ == "__main__":
    main()
