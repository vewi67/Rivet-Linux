#!/usr/bin/env python3
"""Smoke-test the Welcome to Rivet GTK interface under a virtual X display."""

import importlib.util
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


REPOSITORY = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY / "build/config/includes.chroot/usr/bin/rivet-welcome-center"


def drain_events():
    while Gtk.events_pending():
        Gtk.main_iteration_do(False)


def main():
    spec = importlib.util.spec_from_file_location("rivet_welcome_center", APP_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load Welcome to Rivet from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    app = module.RivetWelcomeCenter()
    expected_pages = {"home", "settings", "tools", "about"}
    for page in expected_pages:
        assert app.stack.get_child_by_name(page) is not None, f"Missing page: {page}"

    app.show()
    drain_events()
    assert app.window.get_visible(), "Welcome to Rivet window did not become visible."
    assert app.stack.get_visible_child_name() == "home", "The home page should be the initial page."
    assert app.settings_count.get_text() == "24 settings and tools", (
        f"Unexpected initial settings count: {app.settings_count.get_text()!r}"
    )

    app.search.set_text("Bluetooth")
    drain_events()
    assert app.settings_count.get_text() == "1 result", (
        f"Search for Bluetooth should find one card, got {app.settings_count.get_text()!r}"
    )

    app.search.set_text("no-such-setting-name")
    drain_events()
    assert app.settings_count.get_text() == "0 results", (
        "An unmatched search should show zero results."
    )

    app.search.set_text("")
    drain_events()
    assert app.settings_count.get_text() == "24 settings and tools", (
        "Clearing search should restore the full settings catalog."
    )

    app.stack.set_visible_child_name("settings")
    drain_events()
    assert app.stack.get_visible_child_name() == "settings", (
        "System settings page could not be selected."
    )

    app.window.destroy()
    drain_events()
    print("Welcome to Rivet GTK smoke test passed: window, four pages, search filtering and navigation.")


if __name__ == "__main__":
    main()
