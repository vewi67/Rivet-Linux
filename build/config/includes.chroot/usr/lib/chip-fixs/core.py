#!/usr/bin/python3
"""Read-only diagnostics and local collection of Chip Fixs system information."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

APP_VERSION = "1.0.0"
RIVET_WALLPAPERS = (
    "/usr/share/backgrounds/rivet/rivet-waves.jpeg",
    "/usr/share/backgrounds/rivet/rivet-factory.jpeg",
    "/usr/share/backgrounds/rivet/rivet-chip.jpeg",
    "/usr/share/backgrounds/rivet/rivet-prism.jpeg",
)


def run_command(args: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str]:
    """Execute a fixed argument list without a shell or hidden errors."""
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    env["LANG"] = "C"
    try:
        return subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=timeout,
            env=env,
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(args, 127, "", f"Command not found: {args[0]}")
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", "replace")
        return subprocess.CompletedProcess(args, 124, output, f"Timed out: {args[0]}")
    except OSError as error:
        return subprocess.CompletedProcess(args, 126, "", str(error))


def find_command(name: str) -> str | None:
    """Find trusted system utilities in fixed directories, never through user PATH."""
    for directory in ("/usr/bin", "/usr/sbin", "/bin", "/sbin"):
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def read_text(path: str | Path, default: str = "") -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except (OSError, ValueError):
        return default


def parse_os_release(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        values[key.strip()] = value
    return values


def parse_meminfo(text: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for line in text.splitlines():
        match = re.match(r"^([^:]+):\s+(\d+)(?:\s+(kB))?", line)
        if match:
            amount = int(match.group(2))
            result[match.group(1)] = amount * 1024 if match.group(3) else amount
    return result


def format_bytes(value: int | float | None) -> str:
    if value is None:
        return "Not available"
    amount = max(0.0, float(value))
    for unit in ("B", "KiB", "MiB", "GiB", "TiB", "PiB"):
        if amount < 1024 or unit == "PiB":
            if unit == "B":
                return f"{int(amount)} {unit}"
            return f"{amount:.2f} {unit}"
        amount /= 1024
    return f"{amount:.2f} PiB"


def parse_lsblk_json(text: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        return []
    devices = payload.get("blockdevices", [])
    return devices if isinstance(devices, list) else []


def parse_lscpu(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def read_os_and_board() -> dict[str, str]:
    os_data = parse_os_release(read_text("/etc/os-release"))
    dmi_root = Path("/sys/devices/virtual/dmi/id")
    dmi_fields = {
        "System manufacturer": "sys_vendor",
        "System model": "product_name",
        "System version": "product_version",
        "Motherboard manufacturer": "board_vendor",
        "Motherboard model": "board_name",
        "Motherboard version": "board_version",
        "Firmware/BIOS manufacturer": "bios_vendor",
        "Firmware/BIOS version": "bios_version",
        "Firmware/BIOS date": "bios_date",
        "Chassis manufacturer": "chassis_vendor",
    }
    result = {
        "Operating system": os_data.get("PRETTY_NAME", "Unknown"),
        "Distribution ID": os_data.get("ID", "Unknown"),
        "Distribution version": os_data.get("VERSION_ID", "Unknown"),
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
        "Computer name": platform.node() or "Unknown",
        "Chip Fixs version": APP_VERSION,
    }
    uptime_raw = read_text("/proc/uptime")
    if uptime_raw:
        try:
            seconds = int(float(uptime_raw.split()[0]))
            days, remainder = divmod(seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes = remainder // 60
            day_label = "day" if days == 1 else "days"
            result["Uptime"] = f"{days} {day_label}, {hours} h, {minutes} min"
        except (ValueError, IndexError):
            result["Uptime"] = "Not available"
    else:
        result["Uptime"] = "Not available"

    result["Graphical session type"] = os.environ.get("XDG_SESSION_TYPE", "Not reported")
    result["Desktop environment"] = os.environ.get("XDG_CURRENT_DESKTOP", "Not reported")
    result["UEFI boot"] = "Yes" if Path("/sys/firmware/efi").exists() else "No / Legacy BIOS"
    for label, filename in dmi_fields.items():
        value = read_text(dmi_root / filename)
        if value:
            result[label] = value
    return result


def memory_summary() -> tuple[list[str], dict[str, int]]:
    mem = parse_meminfo(read_text("/proc/meminfo"))
    total = mem.get("MemTotal")
    available = mem.get("MemAvailable", mem.get("MemFree"))
    swap_total = mem.get("SwapTotal", 0)
    swap_free = mem.get("SwapFree", 0)
    values: list[str] = []
    if total is not None:
        used = max(0, total - (available or 0))
        values.extend(
            [
                f"Installed RAM: {format_bytes(total)}",
                f"RAM in use (estimate): {format_bytes(used)}",
                f"Available memory: {format_bytes(available)}",
                f"RAM usage: {((used / total) * 100):.1f}%" if total else "RAM usage: not available",
            ]
        )
    else:
        values.append("Could not read /proc/meminfo.")
    values.append(f"Swap total: {format_bytes(swap_total)}")
    values.append(f"Swap used: {format_bytes(max(0, swap_total - swap_free))}")
    return values, mem


def list_physical_disks() -> list[tuple[str, str]]:
    lsblk = find_command("lsblk")
    if not lsblk:
        return []
    result = run_command(
        [lsblk, "-dnJpo", "NAME,MODEL,SIZE,TYPE"],
        timeout=4,
    )
    if result.returncode != 0:
        return []
    disks: list[tuple[str, str]] = []
    for item in parse_lsblk_json(result.stdout):
        device = str(item.get("name") or "")
        if item.get("type") != "disk" or not device.startswith("/dev/"):
            continue
        model = str(item.get("model") or "").strip()
        size = str(item.get("size") or "").strip()
        label = " ".join(part for part in (device, model, size) if part)
        disks.append((device, label))
    return disks


def collect_system_info() -> OrderedDict[str, str]:
    """Collects local information. It does not send data or change configuration."""
    info: OrderedDict[str, str] = OrderedDict()

    overview = read_os_and_board()
    info["Overview and motherboard"] = "\n".join(f"{key}: {value}" for key, value in overview.items())

    cpu = run_command(["lscpu"], timeout=5)
    if cpu.returncode == 0 and cpu.stdout.strip():
        cpu_text = cpu.stdout.strip()
    else:
        model = "Not identified"
        for line in read_text("/proc/cpuinfo").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                model = line.split(":", 1)[1].strip()
                break
        cpu_text = f"Model: {model}\nLogical processors: {os.cpu_count() or 'Not available'}"
    info["Processor"] = cpu_text

    memory_lines, _mem = memory_summary()
    memory_lines.append("")
    memory_lines.append("Per-module RAM details")
    dmidecode = find_command("dmidecode")
    if dmidecode:
        dmi_memory = run_command([dmidecode, "--type", "memory"], timeout=6)
        if dmi_memory.returncode == 0 and dmi_memory.stdout.strip():
            memory_lines.append(dmi_memory.stdout.strip())
        else:
            memory_lines.append(
                "Firmware may expose the manufacturer, speed, and capacity of each memory module. "
                "Use “Advanced RAM details” to request administrator authorization."
            )
    else:
        memory_lines.append("dmidecode is not installed in this image.")
    info["RAM and swap"] = "\n".join(memory_lines)

    gpu = run_command(["lspci", "-nnk"], timeout=6)
    if gpu.returncode == 0:
        blocks = re.split(r"(?=^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F])", gpu.stdout, flags=re.M)
        display_blocks = [
            block.strip() for block in blocks
            if re.search(r"VGA compatible controller|3D controller|Display controller", block, re.I)
        ]
        gpu_text = "\n\n".join(display_blocks) if display_blocks else "No graphics controller was identified by lspci."
    else:
        gpu_text = gpu.stderr.strip() or "lspci is not available."
    glx = run_command(["glxinfo", "-B"], timeout=6)
    if glx.returncode == 0 and glx.stdout.strip():
        gpu_text += "\n\nOpenGL e renderizador ativo\n" + glx.stdout.strip()
    else:
        gpu_text += "\n\nOpenGL: glxinfo is unavailable or the current graphical session does not expose this feature."
    xrandr = run_command(["xrandr", "--query"], timeout=4)
    gpu_text += "\n\nDisplays and resolutions\n" + (
        xrandr.stdout.strip() if xrandr.returncode == 0 and xrandr.stdout.strip()
        else "Could not query XRandR in this session."
    )
    info["Graphics and displays"] = gpu_text

    lsblk = run_command(
        ["lsblk", "-e", "7", "-o", "NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS,ROTA,TRAN"],
        timeout=6,
    )
    df = run_command(["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"], timeout=5)
    storage = lsblk.stdout.strip() if lsblk.returncode == 0 else (lsblk.stderr.strip() or "lsblk is not available.")
    storage += "\n\nFilesystem usage\n"
    storage += df.stdout.strip() if df.returncode == 0 else (df.stderr.strip() or "df is not available.")
    storage += (
        "\n\nSMART health: select a disk and use the check button. "
        "This test requests administrator authorization and only reads disk health data."
    )
    info["Disks, partitions, and space"] = storage

    network = run_command(
        ["nmcli", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
        timeout=6,
    )
    ip = run_command(["ip", "-brief", "address"], timeout=4)
    info["Network and interfaces"] = (
        "NetworkManager\n"
        + (network.stdout.strip() if network.returncode == 0 else (network.stderr.strip() or "nmcli is not available."))
        + "\n\nAddresses and interfaces\n"
        + (ip.stdout.strip() if ip.returncode == 0 else (ip.stderr.strip() or "ip is not available."))
    )

    pactl = run_command(["pactl", "info"], timeout=4)
    sinks = run_command(["pactl", "list", "short", "sinks"], timeout=4)
    sources = run_command(["pactl", "list", "short", "sources"], timeout=4)
    audio = pactl.stdout.strip() if pactl.returncode == 0 else (pactl.stderr.strip() or "pactl is not available.")
    audio += "\n\nAudio outputs\n" + (
        sinks.stdout.strip() if sinks.returncode == 0 else (sinks.stderr.strip() or "Not available.")
    )
    audio += "\n\nAudio inputs\n" + (
        sources.stdout.strip() if sources.returncode == 0 else (sources.stderr.strip() or "Not available.")
    )
    for service in ("pipewire.service", "pipewire-pulse.service", "wireplumber.service"):
        state = run_command(["systemctl", "--user", "is-active", service], timeout=3)
        if state.returncode in (0, 3, 4):
            audio += f"\n{service}: {(state.stdout or state.stderr).strip() or 'unknown'}"
    info["Audio"] = audio

    pci = run_command(["lspci", "-nnk"], timeout=6)
    usb = run_command(["lsusb"], timeout=5)
    info["PCI and USB devices"] = (
        "PCI devices\n"
        + (pci.stdout.strip() if pci.returncode == 0 else (pci.stderr.strip() or "lspci is not available."))
        + "\n\nUSB devices\n"
        + (usb.stdout.strip() if usb.returncode == 0 else (usb.stderr.strip() or "lsusb is not available."))
    )

    power_lines: list[str] = []
    supply_root = Path("/sys/class/power_supply")
    if supply_root.exists():
        for supply in sorted(supply_root.iterdir()):
            kind = read_text(supply / "type")
            if not kind:
                continue
            power_lines.append(f"{supply.name} ({kind})")
            for key, filename in (
                ("Manufacturer", "manufacturer"),
                ("Model", "model_name"),
                ("State", "status"),
                ("Charge", "capacity"),
                ("Technology", "technology"),
                ("Voltage (µV)", "voltage_now"),
                ("Current (µA)", "current_now"),
            ):
                value = read_text(supply / filename)
                if value:
                    power_lines.append(f"  {key}: {value}")
    if not power_lines:
        power_lines.append("No battery or power supply was identified in /sys/class/power_supply.")
    sensors = run_command(["sensors"], timeout=5)
    if sensors.returncode == 0 and sensors.stdout.strip():
        power_lines.extend(["", "Temperature and voltage sensors", sensors.stdout.strip()])
    else:
        power_lines.extend(["", "Sensors", "The sensors command returned no data. Some devices do not expose temperature readings."])
    thermal: list[str] = []
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        temp = read_text(zone / "temp")
        zone_type = read_text(zone / "type", zone.name)
        if temp.isdigit():
            thermal.append(f"{zone_type}: {int(temp) / 1000:.1f} °C")
    if thermal:
        power_lines.extend(["", "Kernel thermal zones", *thermal])
    info["Battery, power, and sensors"] = "\n".join(power_lines)

    failed = run_command(["systemctl", "--failed", "--no-legend", "--plain"], timeout=6)
    audit = run_command(["dpkg", "--audit"], timeout=10)
    updates = run_command(["apt", "list", "--upgradable"], timeout=12)
    timedate = run_command(["timedatectl", "status"], timeout=4)
    maintenance = [
        "Failed system services",
        failed.stdout.strip() if failed.returncode == 0 and failed.stdout.strip() else (
            "systemd reported no failed services." if failed.returncode == 0
            else (failed.stderr.strip() or "Not available.")
        ),
        "",
        "dpkg package database audit",
        audit.stdout.strip() if audit.returncode == 0 and audit.stdout.strip() else (
            "dpkg reported no problems." if audit.returncode == 0
            else (audit.stderr.strip() or "Not available.")
        ),
        "",
        "Packages with available updates (local cache; may be outdated)",
        updates.stdout.strip() if updates.returncode == 0 else (updates.stderr.strip() or "Not available."),
        "",
        "Date and clock synchronization",
        timedate.stdout.strip() if timedate.returncode == 0 else (timedate.stderr.strip() or "Not available."),
    ]
    info["Services, packages, and clock"] = "\n".join(maintenance)

    return info


def list_physical_disks_for_test() -> list[tuple[str, str]]:
    return list_physical_disks()


def _check(
    check_id: str,
    category: str,
    status: str,
    title: str,
    details: str,
    repair: str | None = None,
    suggestion: str | None = None,
) -> dict[str, str | None]:
    return {
        "id": check_id,
        "category": category,
        "status": status,
        "title": title,
        "details": details,
        "repair": repair,
        "suggestion": suggestion,
    }


def run_diagnostics() -> list[dict[str, str | None]]:
    """Runs read-only checks; repairs always require confirmation."""
    results: list[dict[str, str | None]] = []

    audit = run_command(["dpkg", "--audit"], timeout=12)
    if audit.returncode == 127:
        results.append(_check("dpkg", "Packages", "unknown", "Package audit unavailable", audit.stderr))
    elif audit.returncode != 0 or audit.stdout.strip():
        details = audit.stdout.strip() or audit.stderr.strip() or "dpkg returned an error without details."
        results.append(_check(
            "dpkg", "Packages", "error", "The package database needs attention", details,
            suggestion="Review the details before changing packages. Common diagnostic commands: dpkg --audit and apt-get -s check.",
        ))
    else:
        results.append(_check("dpkg", "Packages", "ok", "dpkg package database", "dpkg reported no pending configuration."))

    apt_check = run_command(["apt-get", "-s", "check"], timeout=25)
    if apt_check.returncode == 127:
        results.append(_check("apt", "Packages", "unknown", "Dependency check unavailable", apt_check.stderr))
    elif apt_check.returncode != 0:
        results.append(_check(
            "apt", "Packages", "error", "The dependency check found a problem",
            (apt_check.stdout + "\n" + apt_check.stderr).strip() or f"apt-get -s check returned code {apt_check.returncode}.",
            suggestion="No packages were installed, removed, or updated. Review the messages and simulate a repair before authorizing changes.",
        ))
    else:
        results.append(_check("apt", "Packages", "ok", "APT dependencies", "apt-get -s check finished without reporting broken dependencies."))

    try:
        usage = shutil.disk_usage("/")
        percent = usage.used / usage.total * 100 if usage.total else 0
        detail = f"Root filesystem: {format_bytes(usage.used)} used of {format_bytes(usage.total)} ({percent:.1f}%)."
        if percent >= 97:
            results.append(_check("disk-space", "Storage", "critical", "The root filesystem is almost full", detail + " Chip will not delete personal files automatically."))
        elif percent >= 90:
            results.append(_check("disk-space", "Storage", "warning", "Low free space on root filesystem", detail + " Review files before freeing space."))
        else:
            results.append(_check("disk-space", "Storage", "ok", "Free space on root filesystem", detail))
    except OSError as error:
        results.append(_check("disk-space", "Storage", "unknown", "Could not measure free space", str(error)))

    mem = parse_meminfo(read_text("/proc/meminfo"))
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", mem.get("MemFree", 0))
    if total <= 0:
        results.append(_check("memory", "Memory", "unknown", "RAM status unavailable", "The kernel did not provide MemTotal in /proc/meminfo."))
    else:
        percent = available / total * 100
        detail = f"{format_bytes(available)} of {format_bytes(total)} are available ({percent:.1f}%)."
        if percent < 5:
            results.append(_check("memory", "Memory", "warning", "Low available memory", detail + " Chip will not terminate programs automatically."))
        else:
            results.append(_check("memory", "Memory", "ok", "Available memory", detail))

    nm = run_command(["systemctl", "is-active", "NetworkManager.service"], timeout=4)
    network_state = (nm.stdout or nm.stderr).strip().lower()
    if nm.returncode == 127:
        results.append(_check("network-manager", "Network", "unknown", "Could not query NetworkManager", nm.stderr))
    elif network_state != "active":
        results.append(_check(
            "network-manager", "Network", "warning", "The NetworkManager service is not active",
            f"Reported state: {network_state or 'unknown'}. Restarting the service may temporarily interrupt networking.",
            repair="network" if network_state in {"inactive", "failed"} else None,
        ))
    else:
        results.append(_check("network-manager", "Network", "ok", "Network service", "NetworkManager is active."))

    if os.environ.get("DBUS_SESSION_BUS_ADDRESS") or os.environ.get("XDG_RUNTIME_DIR"):
        audio_states: list[tuple[str, str]] = []
        for service in ("pipewire.service", "pipewire-pulse.service", "wireplumber.service"):
            state_result = run_command(["systemctl", "--user", "is-active", service], timeout=3)
            state = (state_result.stdout or state_result.stderr).strip().lower()
            if state_result.returncode in (0, 3, 4):
                audio_states.append((service, state or "unknown"))
        inactive = [(name, state) for name, state in audio_states if state != "active"]
        if inactive:
            details = "\n".join(f"{name}: {state}" for name, state in inactive)
            results.append(_check(
                "audio", "Audio", "warning", "One or more audio services are inactive", details + "\nRestarting audio may interrupt currently playing sound.",
                repair="audio",
            ))
        elif audio_states:
            results.append(_check("audio", "Audio", "ok", "Audio services", "PipeWire, PipeWire Pulse, and WirePlumber are active."))
        else:
            results.append(_check("audio", "Audio", "unknown", "Audio status not confirmed", "Could not query audio services in the current session."))
    else:
        results.append(_check("audio", "Audio", "unknown", "Session audio not checked", "No user session bus was detected. Open Chip Fixs in the graphical user session to check audio."))

    failed = run_command(["systemctl", "--failed", "--no-legend", "--plain"], timeout=6)
    failed_lines = [line.strip() for line in failed.stdout.splitlines() if line.strip()]
    if failed.returncode != 0:
        results.append(_check("failed-units", "Services", "unknown", "Could not query failed services", failed.stderr.strip() or "systemctl --failed returned an error."))
    elif failed_lines:
        results.append(_check(
            "failed-units", "Services", "warning", f"{len(failed_lines)} failed system unit(s)",
            "\n".join(failed_lines[:12]) + ("\n… more results omitted." if len(failed_lines) > 12 else "") +
            "\nA failed unit may be optional. Chip will not restart unknown services automatically.",
        ))
    else:
        results.append(_check("failed-units", "Services", "ok", "systemd services", "systemd reported no failed units."))

    if Path("/usr/share/backgrounds/rivet").is_dir():
        missing = [path for path in RIVET_WALLPAPERS if not Path(path).is_file() or Path(path).stat().st_size == 0]
        if missing:
            results.append(_check("rivet-files", "Rivet", "warning", "One or more Rivet visual assets are missing", "\n".join(missing)))
        else:
            results.append(_check("rivet-files", "Rivet", "ok", "Rivet visual assets", "All four expected wallpapers are present."))
    else:
        results.append(_check("rivet-files", "Rivet", "unknown", "Rivet files not found", "This installation does not expose /usr/share/backgrounds/rivet; the app may be running outside Rivet."))

    # Check whether a graphics controller is visible to PCI enumeration.
    graphics = run_command(["lspci", "-nnk"], timeout=6)
    if graphics.returncode == 127:
        results.append(_check("graphics", "Graphics", "unknown", "Graphics check unavailable", graphics.stderr))
    elif graphics.returncode != 0:
        results.append(_check("graphics", "Graphics", "warning", "The graphics controller query failed", graphics.stderr.strip() or f"lspci returned code {graphics.returncode}."))
    elif re.search(r"VGA compatible controller|3D controller|Display controller", graphics.stdout, re.I):
        results.append(_check("graphics", "Graphics", "ok", "Graphics controller detected", "The PCI bus reports at least one graphics controller. This does not replace testing the driver and 3D acceleration."))
    else:
        results.append(_check("graphics", "Graphics", "unknown", "Graphics controller not confirmed", "No graphics controller was identified in lspci output. This can be normal on machines without PCI graphics or in virtual environments."))

    # Read kernel thermal zones when the platform exposes them. Missing sensors
    # are not treated as proof that the computer is overheating or broken.
    thermal_readings: list[tuple[str, float]] = []
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        raw_temp = read_text(zone / "temp")
        zone_name = read_text(zone / "type", zone.name)
        try:
            if raw_temp:
                thermal_readings.append((zone_name, int(raw_temp) / 1000.0))
        except ValueError:
            continue
    if thermal_readings:
        hottest_name, hottest_temp = max(thermal_readings, key=lambda pair: pair[1])
        summary = "; ".join(f"{name}: {temp:.1f} °C" for name, temp in thermal_readings[:8])
        if hottest_temp >= 95:
            results.append(_check("temperature", "Temperature", "critical", "A very high temperature was detected", summary + ". Reduce the workload and check ventilation; Chip Fixs does not control fans or shut down the computer."))
        elif hottest_temp >= 85:
            results.append(_check("temperature", "Temperature", "warning", "An elevated temperature was detected", summary + ". Interpretation depends on the component and sensor."))
        else:
            results.append(_check("temperature", "Temperature", "ok", "Kernel thermal sensors", summary))
    else:
        results.append(_check("temperature", "Temperature", "unknown", "Temperatures unavailable", "The kernel did not expose readable thermal zones. This does not prove a cooling problem exists."))

    updates = run_command(["apt", "list", "--upgradable"], timeout=12)
    if updates.returncode == 0:
        candidates = [
            line.strip() for line in updates.stdout.splitlines()
            if line.strip() and not line.startswith("Listing...") and "/" in line and not line.startswith("WARNING:")
        ]
        if candidates:
            results.append(_check("updates", "Packages", "warning", f"{len(candidates)} package(s) may have updates available", "The list uses the local cache and may be outdated. Chip does not install updates automatically."))
        else:
            results.append(_check("updates", "Packages", "ok", "Local update cache", "The local cache reported no upgradable packages. This result does not check whether package lists are current."))
    else:
        results.append(_check("updates", "Packages", "unknown", "Update status not confirmed", updates.stderr.strip() or "APT could not query its local cache."))

    journal = run_command(["journalctl", "-b", "-p", "err", "--no-pager", "-n", "50", "-q"], timeout=8)
    if journal.returncode == 0:
        error_lines = [line for line in journal.stdout.splitlines() if line.strip()]
        if error_lines:
            results.append(_check("journal-errors", "System logs", "warning", f"{len(error_lines)} error-level entry/entries in recent logs", "Logs may contain old, transient, or hardware-specific messages. Chip does not modify the journal or automatically attempt to repair unknown causes."))
        else:
            results.append(_check("journal-errors", "System logs", "ok", "Recent journal errors", "No error-level messages were returned for the recent part of the current boot."))
    else:
        results.append(_check("journal-errors", "System logs", "unknown", "Journal reading unavailable", "Could not read the current boot journal; this may depend on account permissions."))

    return results


def repair_action(action: str) -> tuple[bool, str]:
    """Only performs repair actions from a fixed allow-list."""
    if action == "audio":
        command = ["systemctl", "--user", "restart", "pipewire.service", "pipewire-pulse.service", "wireplumber.service"]
        result = run_command(command, timeout=20)
        if result.returncode == 0:
            return True, "The audio services received the restart command."
        detail = (result.stdout + "\n" + result.stderr).strip()
        return False, detail or f"systemctl returned code {result.returncode}."

    if action == "network":
        pkexec = find_command("pkexec")
        systemctl = find_command("systemctl")
        if not pkexec or not systemctl:
            return False, "pkexec or systemctl was not found. No changes were made."
        # Fixed and visible action. No command comes from user input.
        result = run_command([pkexec, systemctl, "restart", "NetworkManager.service"], timeout=30)
        if result.returncode == 0:
            return True, "NetworkManager was restarted. The connection may take a few seconds to return."
        detail = (result.stdout + "\n" + result.stderr).strip()
        return False, detail or f"The restart was cancelled or failed (code {result.returncode})."

    return False, "This action is not part of the allowed repair list. No changes were made."


def read_advanced_memory() -> tuple[bool, str]:
    """Reads the RAM SMBIOS inventory only after the user authorizes it."""
    pkexec = find_command("pkexec")
    dmidecode = find_command("dmidecode")
    if not pkexec or not dmidecode:
        return False, "pkexec and dmidecode must be installed. No changes were made."
    result = run_command([pkexec, dmidecode, "--type", "memory"], timeout=15)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output or f"dmidecode returned code {result.returncode} without details."


def read_smart_health(device: str) -> tuple[bool, str]:
    """Checks SMART health for a device selected by the user."""
    allowed_devices = {path for path, _label in list_physical_disks()}
    if device not in allowed_devices:
        return False, "Device is not recognized in the current physical disk list. No action was performed."
    pkexec = find_command("pkexec")
    smartctl = find_command("smartctl")
    if not pkexec or not smartctl:
        return False, "pkexec and smartmontools must be installed. No changes were made."
    result = run_command([pkexec, smartctl, "-H", device], timeout=20)
    output = (result.stdout + "\n" + result.stderr).strip()
    # smartctl exit statuses are a bitmask. Bits 6-7 can report error/self-test
    # log history while the overall-health result still says PASSED. Bits 0-3
    # indicate command/device/SMART-status problems and prevent a healthy confirmation.
    healthy_status_reported = bool(re.search(
        r"(?:SMART overall-health self-assessment test result:\s*PASSED|SMART Health Status:\s*OK)",
        output,
        re.IGNORECASE,
    ))
    command_or_health_error_bits = result.returncode & 0x1F
    if healthy_status_reported and command_or_health_error_bits == 0:
        if result.returncode:
            output += (
                "\n\nNote: smartctl also reported warning/history bits "
                f"(exit mask {result.returncode:#04x}). Review the output above."
            )
        return True, output
    if not output:
        output = f"smartctl returned code {result.returncode} without a health summary."
    return False, output
