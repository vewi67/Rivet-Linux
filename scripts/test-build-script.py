#!/usr/bin/env python3
"""Verify configure-only preflight never deletes outputs or invokes the ISO build."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
SOURCE_BUILD_SCRIPT = REPOSITORY / "build/build.sh"


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="rivet-build-preflight-") as temporary:
        root = Path(temporary)
        build_dir = root / "build"
        config_dir = build_dir / "config"
        fake_bin = root / "bin"
        fake_bin.mkdir()
        (build_dir / "build.sh").parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_BUILD_SCRIPT, build_dir / "build.sh")

        package_list = config_dir / "package-lists/rivet.list.chroot"
        package_list.parent.mkdir(parents=True)
        package_list.write_text("xfce4\n", encoding="utf-8")
        hook = config_dir / "hooks/normal/0100-configure-rivet-branding.hook.chroot"
        hook.parent.mkdir(parents=True)
        hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")

        existing_iso = build_dir / "Rivet-Linux.amd64.iso"
        existing_checksum = build_dir / "Rivet-Linux.amd64.iso.sha256"
        existing_iso.write_bytes(b"preserve existing ISO")
        existing_checksum.write_text("preserve existing checksum\n", encoding="utf-8")

        log_file = root / "lb-calls.log"
        write_executable(
            fake_bin / "lb",
            "#!/bin/sh\n"
            'printf "%s\\n" "$*" >> "$RIVET_LB_LOG"\n'
            'case "$1" in\n'
            "  config) exit 0 ;;\n"
            "  clean|build) echo \"unexpected lb $1 call\" >&2; exit 91 ;;\n"
            "  *) echo \"unexpected lb command: $1\" >&2; exit 92 ;;\n"
            "esac\n",
        )
        for command in ("xorriso", "file", "sha256sum"):
            write_executable(fake_bin / command, "#!/bin/sh\nexit 0\n")

        environment = os.environ.copy()
        environment["PATH"] = str(fake_bin) + os.pathsep + environment.get("PATH", "")
        environment["RIVET_LB_LOG"] = str(log_file)

        result = subprocess.run(
            ["bash", str(build_dir / "build.sh"), "--configure-only"],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "configure-only preflight failed unexpectedly:\n"
                + result.stdout
                + result.stderr
            )

        calls = log_file.read_text(encoding="utf-8").splitlines()
        if not calls or not calls[0].startswith("config "):
            raise AssertionError(f"expected lb config as the first live-build call, got {calls!r}")
        if any(call == "clean" or call == "build" or call.startswith("build ") for call in calls):
            raise AssertionError(f"configure-only called a destructive/build command: {calls!r}")
        if not existing_iso.is_file() or existing_iso.read_bytes() != b"preserve existing ISO":
            raise AssertionError("configure-only preflight deleted or changed the previous ISO.")
        if not existing_checksum.is_file() or existing_checksum.read_text(encoding="utf-8") != "preserve existing checksum\n":
            raise AssertionError("configure-only preflight deleted or changed the previous checksum.")
        if "configuration preflight completed; ISO build skipped" not in result.stdout:
            raise AssertionError("configure-only success message is missing.")

    print("Rivet build-script tests passed: configure-only calls lb config, skips clean/build, and preserves existing ISO/checksum.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
