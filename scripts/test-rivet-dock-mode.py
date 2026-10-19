#!/usr/bin/env python3
"""Regression tests for the conditional Rivet Plank installer item."""

import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile


REPOSITORY = Path(__file__).resolve().parents[1]
APP_PATH = REPOSITORY / "build/config/includes.chroot/usr/bin/rivet-start-plank"
INSTALLER_ITEM = "Install-Rivet.dockitem"
WELCOME_ITEM = "Welcome.dockitem"


def load_app():
    loader = importlib.machinery.SourceFileLoader("rivet_start_plank", str(APP_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError(f"Could not load Rivet dock helper from {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def read_items(settings: Path):
    for line in settings.read_text(encoding="utf-8").splitlines():
        if line.startswith("DockItems="):
            return [item for item in line.split("=", 1)[1].split(";") if item]
    raise AssertionError("DockItems entry not found")


def main():
    module = load_app()
    with tempfile.TemporaryDirectory(prefix="rivet-dock-mode-") as temporary:
        settings = Path(temporary) / "settings"
        settings.write_text(
            "[PlankDockPreferences]\n"
            "DockItems=Firefox.dockitem;Files.dockitem;Welcome.dockitem;Software.dockitem;"
            "Install-Rivet.dockitem;Chip-Fixs.dockitem;Settings.dockitem;\n"
            "IconSize=48\n"
            "\n[AnotherSection]\nKeepThis=unchanged\n",
            encoding="utf-8",
        )

        assert module.update_dock_items(settings, False), (
            "Installed mode should remove the installer item from the dock."
        )
        installed_items = read_items(settings)
        assert INSTALLER_ITEM not in installed_items
        assert WELCOME_ITEM not in installed_items
        assert installed_items == [
            "Firefox.dockitem", "Files.dockitem", "Software.dockitem",
            "Chip-Fixs.dockitem", "Settings.dockitem",
        ]
        installed_snapshot = settings.read_text(encoding="utf-8")
        assert "KeepThis=unchanged" in installed_snapshot
        assert not module.update_dock_items(settings, False), (
            "Repeating installed-mode configuration should be idempotent."
        )

        assert module.update_dock_items(settings, True), (
            "Live mode should restore both live-only dock items."
        )
        live_items = read_items(settings)
        assert live_items.count(INSTALLER_ITEM) == 1
        assert live_items.count(WELCOME_ITEM) == 1
        assert live_items.index(INSTALLER_ITEM) == live_items.index(WELCOME_ITEM) + 1
        assert live_items.index(WELCOME_ITEM) == live_items.index("Files.dockitem") + 1
        assert not module.update_dock_items(settings, True), (
            "Repeating live-mode configuration should be idempotent."
        )

        # Old profiles can already contain duplicate installer entries.
        settings.write_text(
            settings.read_text(encoding="utf-8").replace(
                "Install-Rivet.dockitem;", "Install-Rivet.dockitem;Install-Rivet.dockitem;"
            ),
            encoding="utf-8",
        )
        module.update_dock_items(settings, True)
        assert read_items(settings).count(INSTALLER_ITEM) == 1

        malformed = Path(temporary) / "malformed"
        malformed.write_text("[NotPlank]\nSomeOption=true\n", encoding="utf-8")
        before = malformed.read_text(encoding="utf-8")
        try:
            module.update_dock_items(malformed, True)
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed Plank settings should fail visibly.")
        assert malformed.read_text(encoding="utf-8") == before

        applications = Path(temporary) / "applications"
        assert module.update_menu_entries(applications, False), (
            "Installed mode should hide live-only launchers and expose the control center."
        )
        for desktop_id in ("rivet-installer.desktop", "rivet-welcome.desktop"):
            content = (applications / desktop_id).read_text(encoding="utf-8")
            assert "Hidden=true" in content
            assert "X-Rivet-Managed=true" in content
        assert not (applications / "rivet-control-center.desktop").exists()
        assert not module.update_menu_entries(applications, False), (
            "Installed launcher visibility should be idempotent."
        )

        assert module.update_menu_entries(applications, True), (
            "Live mode should show Welcome and hide the installed control center."
        )
        assert not (applications / "rivet-installer.desktop").exists()
        assert not (applications / "rivet-welcome.desktop").exists()
        control_override = (applications / "rivet-control-center.desktop").read_text(encoding="utf-8")
        assert "Hidden=true" in control_override
        assert "X-Rivet-Managed=true" in control_override
        assert not module.update_menu_entries(applications, True)

        assert module.update_menu_entries(applications, False)
        assert not (applications / "rivet-installer.desktop").exists()
        assert not (applications / "rivet-welcome.desktop").exists()
        assert not (applications / "rivet-control-center.desktop").exists()

    print("Rivet dock/menu tests passed: live-only entries, installed control center, idempotence, duplicate cleanup, and malformed-settings safety.")


if __name__ == "__main__":
    main()
