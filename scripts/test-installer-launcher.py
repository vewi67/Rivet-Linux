#!/usr/bin/env python3
"""Regression tests for selecting a writable installer diagnostic log."""

import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "build/config/includes.chroot/usr/bin/rivet-installer"
loader = importlib.machinery.SourceFileLoader("rivet_installer_launcher", str(APP_PATH))
spec = importlib.util.spec_from_loader(loader.name, loader)
if spec is None:
    raise AssertionError(f"Could not load {APP_PATH}")
app = importlib.util.module_from_spec(spec)
loader.exec_module(app)


class InstallerLogTests(unittest.TestCase):
    def test_falls_back_when_primary_log_cannot_be_opened(self):
        with tempfile.TemporaryDirectory(prefix="rivet-installer-log-") as temporary:
            root = Path(temporary)
            primary = root / "protected/state.log"
            fallback = root / "tmp/fallback.log"
            real_open = Path.open

            def selective_open(path, *args, **kwargs):
                if Path(path) == primary:
                    raise PermissionError("simulated permission denial")
                return real_open(path, *args, **kwargs)

            with mock.patch.object(Path, "open", new=selective_open):
                selected = app.select_writable_log_path(primary, fallback)

            self.assertEqual(selected, fallback)
            self.assertTrue(fallback.is_file())

    def test_returns_none_when_both_log_paths_fail(self):
        with tempfile.TemporaryDirectory(prefix="rivet-installer-log-") as temporary:
            root = Path(temporary)
            primary = root / "primary.log"
            fallback = root / "fallback.log"

            def denied_open(_path, *_args, **_kwargs):
                raise PermissionError("simulated permission denial")

            with mock.patch.object(Path, "open", new=denied_open):
                selected = app.select_writable_log_path(primary, fallback)

            self.assertIsNone(selected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
