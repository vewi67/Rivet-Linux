#!/usr/bin/env python3
"""Test BIOS/UEFI ISO validation using controlled xorriso reports."""

import os
from pathlib import Path
import subprocess
import tempfile


REPOSITORY = Path(__file__).resolve().parents[1]
VALIDATOR = REPOSITORY / "scripts/validate-iso-boot.sh"

REPORTS = {
    "good": (
        "El Torito boot img :   1  BIOS  y   none  0x0000  0x00      4  1799\n"
        "El Torito boot img :   2  UEFI  y   none  0x0000  0x00   6656   135\n"
    ),
    "no-bios": "El Torito boot img :   1  UEFI  y   none  0x0000  0x00   6656   135\n",
    "no-uefi": "El Torito boot img :   1  BIOS  y   none  0x0000  0x00      4  1799\n",
}


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def run_validator(iso: Path, fake_bin: Path, scenario: str):
    env = os.environ.copy()
    env["PATH"] = str(fake_bin) + os.pathsep + env.get("PATH", "")
    env["RIVET_XORRISO_SCENARIO"] = scenario
    return subprocess.run(
        ["bash", str(VALIDATOR), str(iso)],
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rivet-iso-boot-validation-") as temporary:
        root = Path(temporary)
        fake_bin = root / "bin"
        fake_bin.mkdir()
        iso = root / "sample.iso"
        iso.write_bytes(b"fake but non-empty ISO fixture")

        write_executable(
            fake_bin / "file",
            "#!/bin/sh\nprintf 'ISO 9660 fixture: %s\\n' \"$1\"\n",
        )
        xorriso = [
            "#!/bin/sh",
            'case "$RIVET_XORRISO_SCENARIO" in',
            "  good) printf '%s' '" + REPORTS["good"].replace("'", "'\\''") + "' ;;",
            "  no-bios) printf '%s' '" + REPORTS["no-bios"].replace("'", "'\\''") + "' ;;",
            "  no-uefi) printf '%s' '" + REPORTS["no-uefi"].replace("'", "'\\''") + "' ;;",
            '  error) echo "simulated xorriso failure" >&2; exit 9 ;;',
            '  *) echo "unknown test scenario" >&2; exit 10 ;;',
            "esac",
            "",
        ]
        write_executable(fake_bin / "xorriso", "\n".join(xorriso))

        good = run_validator(iso, fake_bin, "good")
        assert good.returncode == 0, good.stdout + good.stderr
        assert "BIOS" in good.stdout and "UEFI" in good.stdout

        no_bios = run_validator(iso, fake_bin, "no-bios")
        assert no_bios.returncode != 0
        assert "bootable El Torito entry for BIOS" in no_bios.stderr

        no_uefi = run_validator(iso, fake_bin, "no-uefi")
        assert no_uefi.returncode != 0
        assert "bootable El Torito entry for UEFI" in no_uefi.stderr

        failed_xorriso = run_validator(iso, fake_bin, "error")
        assert failed_xorriso.returncode != 0
        assert "could not inspect the ISO boot catalog" in failed_xorriso.stderr

        empty_iso = root / "empty.iso"
        empty_iso.touch()
        empty_result = run_validator(empty_iso, fake_bin, "good")
        assert empty_result.returncode != 0
        assert "ISO is missing or empty" in empty_result.stderr

    print("Rivet ISO boot-validation tests passed: BIOS, UEFI, missing catalog entries, xorriso failure, and empty ISO.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
