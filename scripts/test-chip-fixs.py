#!/usr/bin/env python3
"""Testes unitários sem GTK, privilégios administrativos ou alterações no sistema."""

import importlib.util
import os
import subprocess
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
CORE_PATH = ROOT / "build/config/includes.chroot/usr/lib/chip-fixs/core.py"
SPEC = importlib.util.spec_from_file_location("chip_fixs_core", CORE_PATH)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


class ParsingTests(unittest.TestCase):
    def test_parse_os_release_with_quotes_and_comments(self):
        values = core.parse_os_release(
            '# comentário\nNAME="Rivet Linux"\nID=rivet\nVERSION_ID=1\nEMPTY=\n'
        )
        self.assertEqual(values["NAME"], "Rivet Linux")
        self.assertEqual(values["ID"], "rivet")
        self.assertEqual(values["VERSION_ID"], "1")
        self.assertEqual(values["EMPTY"], "")

    def test_parse_meminfo_converts_kibibytes_to_bytes(self):
        values = core.parse_meminfo("MemTotal:       8192 kB\nMemFree:          25 kB\nBad line\n")
        self.assertEqual(values["MemTotal"], 8192 * 1024)
        self.assertEqual(values["MemFree"], 25 * 1024)
        self.assertNotIn("Bad line", values)

    def test_format_bytes_has_human_readable_units(self):
        self.assertEqual(core.format_bytes(0), "0 B")
        self.assertEqual(core.format_bytes(1024), "1.00 KiB")
        self.assertEqual(core.format_bytes(1024**3), "1.00 GiB")
        self.assertEqual(core.format_bytes(None), "Não disponível")

    def test_parse_lscpu(self):
        parsed = core.parse_lscpu("Architecture: x86_64\nCPU(s): 8\nModel name: Test CPU\n")
        self.assertEqual(parsed["Architecture"], "x86_64")
        self.assertEqual(parsed["CPU(s)"], "8")
        self.assertEqual(parsed["Model name"], "Test CPU")

    def test_parse_lsblk_json(self):
        parsed = core.parse_lsblk_json(
            '{"blockdevices":[{"name":"/dev/sda","type":"disk"},{"name":"/dev/sda1","type":"part"}]}'
        )
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["name"], "/dev/sda")
        self.assertEqual(core.parse_lsblk_json("not json"), [])

    def test_physical_disk_names_support_spaces_in_model(self):
        response = subprocess.CompletedProcess(
            ["lsblk"], 0,
            '{"blockdevices":[{"name":"/dev/nvme0n1","model":"Example Fast Drive","size":"1T","type":"disk"},'
            '{"name":"/dev/nvme0n1p1","model":null,"size":"500G","type":"part"}]}',
            "",
        )
        with mock.patch.object(core, "run_command", return_value=response):
            disks = core.list_physical_disks()
        self.assertEqual(len(disks), 1)
        self.assertEqual(disks[0][0], "/dev/nvme0n1")
        self.assertIn("Example Fast Drive", disks[0][1])
        self.assertIn("1T", disks[0][1])


class SafetyTests(unittest.TestCase):
    def test_unknown_repair_is_refused_without_running_commands(self):
        with mock.patch.object(core, "run_command") as command:
            success, message = core.repair_action("format-disk")
        self.assertFalse(success)
        self.assertIn("Nenhuma alteração", message)
        command.assert_not_called()

    def test_smart_check_refuses_a_device_outside_the_discovered_list(self):
        with mock.patch.object(core, "list_physical_disks", return_value=[("/dev/sda", "/dev/sda Disk 1T")]):
            with mock.patch.object(core, "run_command") as command:
                success, message = core.read_smart_health("/dev/sdb")
        self.assertFalse(success)
        self.assertIn("não reconhecido", message.lower())
        command.assert_not_called()

    def test_run_command_never_runs_a_shell(self):
        with mock.patch("subprocess.run", return_value=subprocess.CompletedProcess(["true"], 0, "", "")) as mocked:
            core.run_command(["/bin/true"])
        self.assertIsNot(mocked.call_args.kwargs.get("shell", False), True)

    def test_diagnostics_report_package_status_and_do_not_run_repair_commands(self):
        calls = []

        def fake_run(args, timeout=5):
            calls.append(list(args))
            if args == ["dpkg", "--audit"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            if args == ["apt-get", "check"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            if args == ["systemctl", "is-active", "NetworkManager.service"]:
                return subprocess.CompletedProcess(args, 0, "active\n", "")
            if args == ["systemctl", "--failed", "--no-legend", "--plain"]:
                return subprocess.CompletedProcess(args, 0, "", "")
            return subprocess.CompletedProcess(args, 127, "", "not available")

        fake_disk_usage = type("DiskUsage", (), {"total": 1000, "used": 300, "free": 700})()
        with mock.patch.object(core, "run_command", side_effect=fake_run):
            with mock.patch.object(core.shutil, "disk_usage", return_value=fake_disk_usage):
                with mock.patch.object(core, "read_text", return_value="MemTotal: 1000000 kB\nMemAvailable: 800000 kB"):
                    with mock.patch.dict(os.environ, {}, clear=True):
                        results = core.run_diagnostics()

        check_ids = {item["id"] for item in results}
        self.assertIn("dpkg", check_ids)
        self.assertIn("apt", check_ids)
        self.assertIn("disk-space", check_ids)
        self.assertIn("memory", check_ids)
        self.assertNotIn("apt-get install", " ".join(" ".join(c) for c in calls))
        self.assertNotIn("rm", [c[0] for c in calls if c])


if __name__ == "__main__":
    unittest.main(verbosity=2)
