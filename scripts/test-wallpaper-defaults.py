#!/usr/bin/env python3
"""Behavioral tests for Rivet's XFCE wallpaper startup script.

These tests use mocked xfconf-query/XRandR/xfdesktop commands. They validate
property handling without building or booting an ISO; they cannot prove the
desktop renders the wallpaper correctly on physical hardware.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot"
WALLPAPER_LITERAL = 'WALLPAPER="/usr/share/backgrounds/rivet/rivet-waves.jpeg"'
START = "cat > /usr/local/bin/rivet-set-wallpaper <<'EOF'\n"
END = "\nEOF\nchmod 0755 /usr/local/bin/rivet-set-wallpaper"

MOCK_XFCONF = r"""#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
state_path = Path(os.environ["RIVET_MOCK_XFCONF_STATE"])
state = json.loads(state_path.read_text(encoding="utf-8"))
channel = args[args.index("-c") + 1] if "-c" in args else ""

if "-lv" in args or ("-l" in args and "-v" in args) or "--list" in args:
    for prop, value in sorted(state.items()):
        if prop.startswith("/backdrop/"):
            print(f"{prop}\t{value}")
    raise SystemExit(0)

if "-p" not in args:
    raise SystemExit("mock xfconf-query: missing property argument")
prop = args[args.index("-p") + 1]

if channel == "xfwm4" and prop == "/general/workspace_count":
    print("2")
    raise SystemExit(0)

set_index = None
if "--set" in args:
    set_index = args.index("--set") + 1
elif "-s" in args:
    set_index = args.index("-s") + 1

if set_index is not None:
    if set_index >= len(args):
        raise SystemExit("mock xfconf-query: missing set value")
    state[prop] = args[set_index]
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    raise SystemExit(0)

if prop not in state:
    raise SystemExit(1)
print(state[prop])
"""

def write_command(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def extract_runtime_script() -> str:
    hook = HOOK.read_text(encoding="utf-8")
    start = hook.find(START)
    if start < 0:
        raise AssertionError("Wallpaper runtime-script heredoc is missing.")
    start += len(START)
    end = hook.find(END, start)
    if end < 0:
        raise AssertionError("Wallpaper runtime-script heredoc is not terminated.")
    script = hook[start:end]
    if script.count(WALLPAPER_LITERAL) != 1:
        raise AssertionError("Expected one fixed wallpaper path in the runtime script.")
    return script


def run_case(initial: dict[str, str], *, expect_waves: bool) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="rivet-wallpaper-test-") as raw_tmp:
        tmp = Path(raw_tmp)
        home = tmp / "home"
        bin_dir = tmp / "bin"
        home.mkdir()
        bin_dir.mkdir()
        wallpaper = tmp / "rivet-waves.jpeg"
        wallpaper.write_bytes(b"mock image bytes, presence only")
        custom = tmp / "user-wallpaper.jpg"
        custom.write_bytes(b"mock custom image bytes, presence only")

        state_path = tmp / "xfconf-state.json"
        state_path.write_text(json.dumps(initial), encoding="utf-8")
        runtime = tmp / "rivet-set-wallpaper"
        runtime.write_text(
            extract_runtime_script().replace(WALLPAPER_LITERAL, f'WALLPAPER="{wallpaper}"'),
            encoding="utf-8",
        )
        runtime.chmod(0o755)

        write_command(bin_dir / "xfconf-query", MOCK_XFCONF)
        write_command(
            bin_dir / "pgrep",
            '#!/bin/sh\n[ "$1" = "-x" ] && [ "$2" = "xfdesktop" ]\n',
        )
        write_command(
            bin_dir / "xrandr",
            '#!/bin/sh\nprintf "Screen 0: minimum 320 x 200, current 1280 x 720\\nVirtual-1 connected primary 1280x720+0+0 (normal left inverted right x axis y axis) 300mm x 170mm\\n"\n',
        )
        write_command(bin_dir / "xfdesktop", "#!/bin/sh\nexit 0\n")
        write_command(bin_dir / "sleep", "#!/bin/sh\nexit 0\n")

        marker = home / ".config/rivet/wallpaper-default-applied"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("stale marker from an older build\n", encoding="utf-8")

        env = os.environ.copy()
        env["HOME"] = str(home)
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        env["RIVET_MOCK_XFCONF_STATE"] = str(state_path)

        proc = subprocess.run(
            ["/bin/sh", str(runtime)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            check=False,
        )
        log_path = home / ".cache/rivet/wallpaper-default.log"
        log = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
        if proc.returncode != 0:
            raise AssertionError(
                f"Wallpaper startup script exited {proc.returncode}.\n"
                f"stdout: {proc.stdout}\nlog: {log}"
            )
        if marker.exists():
            raise AssertionError("Legacy one-time marker was not removed.")

        final_state = json.loads(state_path.read_text(encoding="utf-8"))
        wave = str(wallpaper)
        root = "/backdrop/screen0/monitorVirtual-1"
        if expect_waves:
            for key in (
                f"{root}/image-path",
                f"{root}/last-image",
                f"{root}/workspace0/last-image",
                f"{root}/workspace1/last-image",
            ):
                if final_state.get(key) != wave:
                    raise AssertionError(f"Expected {key} to be Rivet Waves, got {final_state.get(key)!r}.")
            if final_state.get(f"{root}/workspace0/image-style") != "5":
                raise AssertionError("Wallpaper fit mode was not set to zoomed (5).")
            if "Rivet Waves wallpaper properties verified" not in log:
                raise AssertionError("The default-wallpaper verification message is missing.")
        else:
            for key, value in initial.items():
                if final_state.get(key) != value:
                    raise AssertionError(f"User wallpaper property was overwritten: {key}")
            if f"{root}/workspace1/last-image" in final_state:
                raise AssertionError("A missing workspace property overrode an existing custom monitor wallpaper.")
            if "existing user-selected wallpapers were preserved" not in log:
                raise AssertionError("The custom-wallpaper preservation message is missing.")
        return final_state


def main() -> None:
    script = extract_runtime_script()
    if "workspace[0-9]+/(last-image|last-single-image)" in script:
        raise AssertionError("Wallpaper detection still incorrectly requires a workspace property.")
    stock = "/usr/share/images/desktop-base/default"
    monitor = "/backdrop/screen0/monitorVirtual-1"
    run_case(
        {
            f"{monitor}/image-path": stock,
            f"{monitor}/last-image": stock,
        },
        expect_waves=True,
    )

    with tempfile.TemporaryDirectory(prefix="rivet-wallpaper-custom-") as raw_tmp:
        custom_wallpaper = Path(raw_tmp) / "custom-wallpaper.jpg"
        custom_wallpaper.write_bytes(b"mock user wallpaper")
        run_case(
            {
                f"{monitor}/image-path": str(custom_wallpaper),
                f"{monitor}/workspace0/last-image": str(custom_wallpaper),
            },
            expect_waves=False,
        )
    print("Wallpaper behavior tests passed: legacy Debian defaults are repaired and custom wallpapers are preserved.")


if __name__ == "__main__":
    main()
