#!/usr/bin/env python3
"""Regression tests for Rivet Atmosphere app state rollback and unique-area counts."""

import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "build/config/includes.chroot/usr/bin/rivet-atmosphere"

# Stub GTK at import time; tests exercise the non-visual state logic only.
gi_module = types.ModuleType("gi")
gi_module.require_version = lambda *_args: None
repository_module = types.ModuleType("gi.repository")
repository_module.Gtk = types.SimpleNamespace(Window=object)
gi_module.repository = repository_module
with mock.patch.dict(sys.modules, {"gi": gi_module, "gi.repository": repository_module}):
    loader = importlib.machinery.SourceFileLoader("rivet_atmosphere_app", str(APP_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError(f"Could not load {APP_PATH}")
    app = importlib.util.module_from_spec(spec)
    loader.exec_module(app)


class AtmosphereStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="rivet-atmosphere-ui-")
        self.addCleanup(self.temp.cleanup)
        self.mode_file = Path(self.temp.name) / "config/rivet/atmosphere-mode"
        self.mode_file.parent.mkdir(parents=True)
        app.MODE_FILE = self.mode_file
        self.prefix = "/backdrop/screen0/monitorVirtual-1/workspace-1"
        self.aliases = [
            (f"{self.prefix}/last-image", self.prefix, "RIVET:waves"),
            (f"{self.prefix}/last-single-image", self.prefix, "RIVET:waves"),
        ]
        self.is_rivet = mock.patch.object(
            app, "is_rivet_art", side_effect=lambda image: image.startswith("RIVET:")
        )
        self.is_rivet.start()
        self.addCleanup(self.is_rivet.stop)

    def test_failed_guard_restores_previous_mode(self):
        self.mode_file.write_text("static\n", encoding="utf-8")
        with mock.patch.object(app, "image_properties", return_value=self.aliases):
            with mock.patch.object(
                app.subprocess, "run",
                return_value=subprocess.CompletedProcess(["guard"], 1, "", "simulated failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated failure"):
                    app.apply_mode("ambient")
        self.assertEqual(self.mode_file.read_text(encoding="utf-8"), "static\n")

    def test_timeout_restores_previous_mode_and_becomes_readable_error(self):
        self.mode_file.write_text("static\n", encoding="utf-8")
        with mock.patch.object(app, "image_properties", return_value=self.aliases):
            with mock.patch.object(
                app.subprocess, "run", side_effect=subprocess.TimeoutExpired(["guard"], 10)
            ):
                with self.assertRaisesRegex(RuntimeError, "timed out"):
                    app.apply_mode("ambient")
        self.assertEqual(self.mode_file.read_text(encoding="utf-8"), "static\n")

    def test_failed_first_apply_removes_new_mode_file(self):
        with mock.patch.object(app, "image_properties", return_value=self.aliases):
            with mock.patch.object(
                app.subprocess, "run",
                return_value=subprocess.CompletedProcess(["guard"], 1, "", "failure"),
            ):
                with self.assertRaises(RuntimeError):
                    app.apply_mode("ambient")
        self.assertFalse(self.mode_file.exists())

    def test_area_count_deduplicates_last_image_aliases(self):
        with mock.patch.object(app, "image_properties", return_value=self.aliases):
            with mock.patch.object(
                app.subprocess, "run",
                return_value=subprocess.CompletedProcess(["guard"], 0, "", ""),
            ):
                with mock.patch.object(app, "cycle_enabled", return_value=True):
                    active, eligible = app.apply_mode("ambient")
        self.assertEqual(active, 1)
        self.assertEqual(eligible, 1)

    def test_mixed_personal_aliases_refuse_ambient_mode_without_writing_preference(self):
        mixed = [
            self.aliases[0],
            (f"{self.prefix}/last-single-image", self.prefix, "PERSONAL:photo"),
        ]
        with mock.patch.object(app, "image_properties", return_value=mixed):
            with mock.patch.object(app.subprocess, "run") as command:
                with self.assertRaisesRegex(ValueError, "Choose one of the Rivet wallpapers"):
                    app.apply_mode("ambient")
        command.assert_not_called()
        self.assertFalse(self.mode_file.exists())

    def test_post_apply_read_failure_restores_previous_mode(self):
        self.mode_file.write_text("static\\n", encoding="utf-8")
        with mock.patch.object(
            app, "image_properties", side_effect=[self.aliases, RuntimeError("read failed")]
        ):
            with mock.patch.object(
                app.subprocess, "run",
                return_value=subprocess.CompletedProcess(["guard"], 0, "", ""),
            ):
                with self.assertRaisesRegex(RuntimeError, "read failed"):
                    app.apply_mode("ambient")
        self.assertEqual(self.mode_file.read_text(encoding="utf-8"), "static\\n")

    def test_query_timeout_is_reported_as_runtime_error(self):
        with mock.patch.object(
            app.subprocess, "run", side_effect=subprocess.TimeoutExpired(["xfconf-query"], 5)
        ):
            with self.assertRaisesRegex(RuntimeError, "did not respond"):
                app.run_query("-lv")


if __name__ == "__main__":
    unittest.main(verbosity=2)
