#!/usr/bin/env python3
"""Behavioral tests for Rivet Atmosphere's XFCE backdrop-cycle integration."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "build/config/includes.chroot/usr/bin/rivet-wallpaper-guard"

MOCK_XFCONF = r"""#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
state_file = Path(os.environ["RIVET_XFCONF_TEST_STATE"])
state = json.loads(state_file.read_text(encoding="utf-8"))
values = state["values"]
types = state["types"]
log = state["log"]

if "-lv" in args:
    for prop, value in sorted(values.items()):
        print(f"{prop}\t{value}")
    raise SystemExit(0)

if "-p" not in args:
    raise SystemExit("mock xfconf-query: missing -p")
prop = args[args.index("-p") + 1]

set_index = None
if "--set" in args:
    set_index = args.index("--set") + 1
elif "-s" in args:
    set_index = args.index("-s") + 1

if set_index is not None:
    value = args[set_index]
    type_name = args[args.index("--type") + 1] if "--type" in args else "unknown"
    values[prop] = value
    types[prop] = type_name
    log.append({"property": prop, "type": type_name, "value": value})
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    raise SystemExit(0)

if prop not in values:
    raise SystemExit(1)
print(values[prop])
"""


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def run_case(
    *,
    image: str,
    mode: str,
    should_cycle: bool,
    expected_period_type: str = "int",
) -> dict:
    with tempfile.TemporaryDirectory(prefix="rivet-atmosphere-test-") as raw:
        tmp = Path(raw)
        home = tmp / "home"
        bin_dir = tmp / "bin"
        config_dir = home / ".config"
        wallpaper_dir = tmp / "wallpapers"
        for directory in (home, bin_dir, config_dir, wallpaper_dir):
            directory.mkdir(parents=True, exist_ok=True)

        for name in ("rivet-waves.jpeg", "rivet-factory.jpeg", "rivet-chip.jpeg", "rivet-prism.jpeg"):
            (wallpaper_dir / name).write_bytes(b"mock artwork bytes")

        current_image = Path(image)
        if image.startswith("PERSONAL:"):
            personal_image = tmp / "personal.jpg"
            personal_image.write_bytes(b"personal wallpaper bytes")
            image_value = str(personal_image)
        else:
            image_value = str(wallpaper_dir / current_image.name)

        monitor_root = "/backdrop/screen0/monitorVirtual-1/workspace-1"
        initial = {
            f"{monitor_root}/last-image": image_value,
        }
        state_file = tmp / "state.json"
        state_file.write_text(
            json.dumps({"values": initial, "types": {}, "log": []}, indent=2),
            encoding="utf-8",
        )
        mode_file = config_dir / "rivet" / "atmosphere-mode"
        mode_file.parent.mkdir(parents=True, exist_ok=True)
        mode_file.write_text(mode + "\n", encoding="utf-8")

        write_executable(bin_dir / "xfconf-query", MOCK_XFCONF)
        env = os.environ.copy()
        env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
        env["HOME"] = str(home)
        env["XDG_CONFIG_HOME"] = str(config_dir)
        env["RIVET_WALLPAPER_DIR"] = str(wallpaper_dir)
        env["RIVET_XFCONF_TEST_STATE"] = str(state_file)

        proc = subprocess.run(
            ["/bin/sh", str(GUARD), "--once"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=8,
            check=False,
        )
        if proc.returncode != 0:
            raise AssertionError(
                f"rivet-wallpaper-guard exited {proc.returncode} for mode={mode}, image={image}:\n{proc.stdout}"
            )

        state = json.loads(state_file.read_text(encoding="utf-8"))
        values = state["values"]
        types = state["types"]
        log = state["log"]
        enabled = values.get(f"{monitor_root}/backdrop-cycle-enable", "false").lower() in {"true", "1", "yes"}

        if enabled != should_cycle:
            raise AssertionError(
                f"Expected cycling={should_cycle} for mode={mode}, image={image}, got {enabled}. State: {values}"
            )
        if image.startswith("PERSONAL:") and values[f"{monitor_root}/last-image"] != image_value:
            raise AssertionError("The custom wallpaper path was changed.")
        if should_cycle:
            expected = {
                f"{monitor_root}/backdrop-cycle-period": ("1", expected_period_type),
                f"{monitor_root}/backdrop-cycle-timer": ("30", "uint"),
                f"{monitor_root}/backdrop-cycle-random-order": ("true", "bool"),
                f"{monitor_root}/backdrop-cycle-enable": ("true", "bool"),
            }
            for prop, (value, type_name) in expected.items():
                if values.get(prop) != value:
                    raise AssertionError(f"Expected {prop}={value!r}, got {values.get(prop)!r}.")
                if types.get(prop) != type_name:
                    raise AssertionError(f"Expected type {type_name} for {prop}, got {types.get(prop)!r}.")
            if not any(item["property"] == f"{monitor_root}/backdrop-cycle-period" and item["type"] == "int" for item in log):
                raise AssertionError("Cycle period was not written as an integer.")
        return state


def main() -> None:
    if not GUARD.is_file():
        raise AssertionError("Rivet Atmosphere guard script is missing.")

    # workspace-1 is XFCE's shared-workspace property form.
    run_case(image="rivet-waves.jpeg", mode="ambient", should_cycle=True)
    run_case(image="rivet-waves.jpeg", mode="static", should_cycle=False)
    run_case(image="PERSONAL:wallpaper.jpg", mode="ambient", should_cycle=False)

    print("Rivet Atmosphere tests passed: native XFCE settings are typed correctly, static mode works, and personal wallpapers are preserved.")


if __name__ == "__main__":
    main()
