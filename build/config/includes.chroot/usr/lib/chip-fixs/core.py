#!/usr/bin/python3
"""Diagnósticos somente de leitura e coleta local de informações do Chip Fixs."""

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
    """Execute uma lista fixa de argumentos, sem shell e sem esconder erros."""
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
        return subprocess.CompletedProcess(args, 127, "", f"Comando não encontrado: {args[0]}")
    except subprocess.TimeoutExpired as error:
        output = error.stdout or ""
        if isinstance(output, bytes):
            output = output.decode("utf-8", "replace")
        return subprocess.CompletedProcess(args, 124, output, f"Tempo limite excedido: {args[0]}")
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
        return "Não disponível"
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
        "Fabricante do computador": "sys_vendor",
        "Modelo do computador": "product_name",
        "Versão do computador": "product_version",
        "Fabricante da placa-mãe": "board_vendor",
        "Modelo da placa-mãe": "board_name",
        "Versão da placa-mãe": "board_version",
        "Fabricante do firmware/BIOS": "bios_vendor",
        "Versão do firmware/BIOS": "bios_version",
        "Data do firmware/BIOS": "bios_date",
        "Fabricante do chassi": "chassis_vendor",
    }
    result = {
        "Sistema operacional": os_data.get("PRETTY_NAME", "Desconhecido"),
        "ID da distribuição": os_data.get("ID", "Desconhecido"),
        "Versão da distribuição": os_data.get("VERSION_ID", "Desconhecida"),
        "Kernel": platform.release(),
        "Arquitetura": platform.machine(),
        "Nome do computador": platform.node() or "Desconhecido",
        "Versão do Chip Fixs": APP_VERSION,
    }
    uptime_raw = read_text("/proc/uptime")
    if uptime_raw:
        try:
            seconds = int(float(uptime_raw.split()[0]))
            days, remainder = divmod(seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes = remainder // 60
            result["Tempo ligado"] = f"{days} dia(s), {hours} h, {minutes} min"
        except (ValueError, IndexError):
            result["Tempo ligado"] = "Não disponível"
    else:
        result["Tempo ligado"] = "Não disponível"

    result["Tipo de sessão gráfica"] = os.environ.get("XDG_SESSION_TYPE", "Não informado")
    result["Ambiente gráfico"] = os.environ.get("XDG_CURRENT_DESKTOP", "Não informado")
    result["Inicialização UEFI"] = "Sim" if Path("/sys/firmware/efi").exists() else "Não / BIOS legado"
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
                f"Memória RAM instalada: {format_bytes(total)}",
                f"Memória em uso (estimativa): {format_bytes(used)}",
                f"Memória disponível: {format_bytes(available)}",
                f"Uso de RAM: {((used / total) * 100):.1f}%" if total else "Uso de RAM: não disponível",
            ]
        )
    else:
        values.append("Não foi possível ler /proc/meminfo.")
    values.append(f"Swap total: {format_bytes(swap_total)}")
    values.append(f"Swap em uso: {format_bytes(max(0, swap_total - swap_free))}")
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
    """Coleta informações locais. Não envia dados nem modifica a configuração."""
    info: OrderedDict[str, str] = OrderedDict()

    overview = read_os_and_board()
    info["Resumo e placa-mãe"] = "\n".join(f"{key}: {value}" for key, value in overview.items())

    cpu = run_command(["lscpu"], timeout=5)
    if cpu.returncode == 0 and cpu.stdout.strip():
        cpu_text = cpu.stdout.strip()
    else:
        model = "Não identificado"
        for line in read_text("/proc/cpuinfo").splitlines():
            if line.lower().startswith("model name") and ":" in line:
                model = line.split(":", 1)[1].strip()
                break
        cpu_text = f"Modelo: {model}\nProcessadores lógicos: {os.cpu_count() or 'Não disponível'}"
    info["Processador"] = cpu_text

    memory_lines, _mem = memory_summary()
    memory_lines.append("")
    memory_lines.append("Detalhes por pente de RAM")
    dmidecode = find_command("dmidecode")
    if dmidecode:
        dmi_memory = run_command([dmidecode, "--type", "memory"], timeout=6)
        if dmi_memory.returncode == 0 and dmi_memory.stdout.strip():
            memory_lines.append(dmi_memory.stdout.strip())
        else:
            memory_lines.append(
                "O firmware pode fornecer fabricante, velocidade e capacidade de cada pente. "
                "Use “Detalhes avançados da RAM” para solicitar autorização administrativa."
            )
    else:
        memory_lines.append("O dmidecode não está instalado nesta imagem.")
    info["Memória RAM e swap"] = "\n".join(memory_lines)

    gpu = run_command(["lspci", "-nnk"], timeout=6)
    if gpu.returncode == 0:
        blocks = re.split(r"(?=^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F])", gpu.stdout, flags=re.M)
        display_blocks = [
            block.strip() for block in blocks
            if re.search(r"VGA compatible controller|3D controller|Display controller", block, re.I)
        ]
        gpu_text = "\n\n".join(display_blocks) if display_blocks else "Nenhum controlador gráfico identificado por lspci."
    else:
        gpu_text = gpu.stderr.strip() or "O lspci não está disponível."
    glx = run_command(["glxinfo", "-B"], timeout=6)
    if glx.returncode == 0 and glx.stdout.strip():
        gpu_text += "\n\nOpenGL e renderizador ativo\n" + glx.stdout.strip()
    else:
        gpu_text += "\n\nOpenGL: glxinfo não disponível ou a sessão gráfica não expõe esse recurso."
    xrandr = run_command(["xrandr", "--query"], timeout=4)
    gpu_text += "\n\nMonitores e resoluções\n" + (
        xrandr.stdout.strip() if xrandr.returncode == 0 and xrandr.stdout.strip()
        else "Não foi possível consultar o XRandR nesta sessão."
    )
    info["Placa de vídeo e monitores"] = gpu_text

    lsblk = run_command(
        ["lsblk", "-e", "7", "-o", "NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS,ROTA,TRAN"],
        timeout=6,
    )
    df = run_command(["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"], timeout=5)
    storage = lsblk.stdout.strip() if lsblk.returncode == 0 else (lsblk.stderr.strip() or "lsblk não disponível.")
    storage += "\n\nUso dos sistemas de arquivos\n"
    storage += df.stdout.strip() if df.returncode == 0 else (df.stderr.strip() or "df não disponível.")
    storage += (
        "\n\nSaúde SMART: selecione um disco e use o botão de verificação. "
        "O teste solicita autorização administrativa e apenas lê dados de saúde do disco."
    )
    info["Discos, partições e espaço"] = storage

    network = run_command(
        ["nmcli", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"],
        timeout=6,
    )
    ip = run_command(["ip", "-brief", "address"], timeout=4)
    info["Rede e interfaces"] = (
        "NetworkManager\n"
        + (network.stdout.strip() if network.returncode == 0 else (network.stderr.strip() or "nmcli não disponível."))
        + "\n\nEndereços e interfaces\n"
        + (ip.stdout.strip() if ip.returncode == 0 else (ip.stderr.strip() or "ip não disponível."))
    )

    pactl = run_command(["pactl", "info"], timeout=4)
    sinks = run_command(["pactl", "list", "short", "sinks"], timeout=4)
    sources = run_command(["pactl", "list", "short", "sources"], timeout=4)
    audio = pactl.stdout.strip() if pactl.returncode == 0 else (pactl.stderr.strip() or "pactl não disponível.")
    audio += "\n\nSaídas de áudio\n" + (
        sinks.stdout.strip() if sinks.returncode == 0 else (sinks.stderr.strip() or "Não disponível.")
    )
    audio += "\n\nEntradas de áudio\n" + (
        sources.stdout.strip() if sources.returncode == 0 else (sources.stderr.strip() or "Não disponível.")
    )
    for service in ("pipewire.service", "pipewire-pulse.service", "wireplumber.service"):
        state = run_command(["systemctl", "--user", "is-active", service], timeout=3)
        if state.returncode in (0, 3, 4):
            audio += f"\n{service}: {(state.stdout or state.stderr).strip() or 'desconhecido'}"
    info["Áudio"] = audio

    pci = run_command(["lspci", "-nnk"], timeout=6)
    usb = run_command(["lsusb"], timeout=5)
    info["Dispositivos PCI e USB"] = (
        "Dispositivos PCI\n"
        + (pci.stdout.strip() if pci.returncode == 0 else (pci.stderr.strip() or "lspci não disponível."))
        + "\n\nDispositivos USB\n"
        + (usb.stdout.strip() if usb.returncode == 0 else (usb.stderr.strip() or "lsusb não disponível."))
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
                ("Fabricante", "manufacturer"),
                ("Modelo", "model_name"),
                ("Estado", "status"),
                ("Carga", "capacity"),
                ("Tecnologia", "technology"),
                ("Tensão (µV)", "voltage_now"),
                ("Corrente (µA)", "current_now"),
            ):
                value = read_text(supply / filename)
                if value:
                    power_lines.append(f"  {key}: {value}")
    if not power_lines:
        power_lines.append("Nenhuma bateria ou fonte de energia identificada em /sys/class/power_supply.")
    sensors = run_command(["sensors"], timeout=5)
    if sensors.returncode == 0 and sensors.stdout.strip():
        power_lines.extend(["", "Sensores de temperatura e tensão", sensors.stdout.strip()])
    else:
        power_lines.extend(["", "Sensores", "O comando sensors não encontrou dados disponíveis. Alguns dispositivos não expõem temperaturas."])
    thermal: list[str] = []
    for zone in sorted(Path("/sys/class/thermal").glob("thermal_zone*")):
        temp = read_text(zone / "temp")
        zone_type = read_text(zone / "type", zone.name)
        if temp.isdigit():
            thermal.append(f"{zone_type}: {int(temp) / 1000:.1f} °C")
    if thermal:
        power_lines.extend(["", "Zonas térmicas do kernel", *thermal])
    info["Bateria, energia e sensores"] = "\n".join(power_lines)

    failed = run_command(["systemctl", "--failed", "--no-legend", "--plain"], timeout=6)
    audit = run_command(["dpkg", "--audit"], timeout=10)
    updates = run_command(["apt", "list", "--upgradable"], timeout=12)
    timedate = run_command(["timedatectl", "status"], timeout=4)
    maintenance = [
        "Serviços do sistema com falha",
        failed.stdout.strip() if failed.returncode == 0 and failed.stdout.strip() else (
            "Nenhum serviço com falha informado pelo systemd." if failed.returncode == 0
            else (failed.stderr.strip() or "Não disponível.")
        ),
        "",
        "Auditoria do banco de pacotes dpkg",
        audit.stdout.strip() if audit.returncode == 0 and audit.stdout.strip() else (
            "Nenhum problema informado pelo dpkg." if audit.returncode == 0
            else (audit.stderr.strip() or "Não disponível.")
        ),
        "",
        "Pacotes com atualização disponível (cache local; pode estar desatualizado)",
        updates.stdout.strip() if updates.returncode == 0 else (updates.stderr.strip() or "Não disponível."),
        "",
        "Data e sincronização do relógio",
        timedate.stdout.strip() if timedate.returncode == 0 else (timedate.stderr.strip() or "Não disponível."),
    ]
    info["Serviços, pacotes e relógio"] = "\n".join(maintenance)

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
    """Executa verificações de leitura; reparos ficam sempre atrás de confirmação."""
    results: list[dict[str, str | None]] = []

    audit = run_command(["dpkg", "--audit"], timeout=12)
    if audit.returncode == 127:
        results.append(_check("dpkg", "Pacotes", "unknown", "Auditoria de pacotes indisponível", audit.stderr))
    elif audit.returncode != 0 or audit.stdout.strip():
        details = audit.stdout.strip() or audit.stderr.strip() or "O dpkg retornou um erro sem detalhes."
        results.append(_check(
            "dpkg", "Pacotes", "error", "O banco de pacotes precisa de atenção", details,
            suggestion="Revise os detalhes antes de alterar pacotes. Comandos comuns de diagnóstico: dpkg --audit e apt-get -s check.",
        ))
    else:
        results.append(_check("dpkg", "Pacotes", "ok", "Banco de pacotes dpkg", "Nenhuma configuração pendente foi informada pelo dpkg."))

    apt_check = run_command(["apt-get", "-s", "check"], timeout=25)
    if apt_check.returncode == 127:
        results.append(_check("apt", "Pacotes", "unknown", "Verificação de dependências indisponível", apt_check.stderr))
    elif apt_check.returncode != 0:
        results.append(_check(
            "apt", "Pacotes", "error", "A verificação de dependências encontrou um problema",
            (apt_check.stdout + "\n" + apt_check.stderr).strip() or f"apt-get -s check retornou código {apt_check.returncode}.",
            suggestion="Não foram instalados, removidos ou atualizados pacotes. Revise as mensagens e faça uma simulação do reparo antes de autorizar mudanças.",
        ))
    else:
        results.append(_check("apt", "Pacotes", "ok", "Dependências do APT", "apt-get -s check terminou sem relatar dependências quebradas."))

    try:
        usage = shutil.disk_usage("/")
        percent = usage.used / usage.total * 100 if usage.total else 0
        detail = f"Raiz (/): {format_bytes(usage.used)} usados de {format_bytes(usage.total)} ({percent:.1f}%)."
        if percent >= 97:
            results.append(_check("disk-space", "Armazenamento", "critical", "O sistema de arquivos raiz está quase cheio", detail + " O Chip não apagará arquivos pessoais automaticamente."))
        elif percent >= 90:
            results.append(_check("disk-space", "Armazenamento", "warning", "Pouco espaço livre na raiz", detail + " Revise os arquivos antes de liberar espaço."))
        else:
            results.append(_check("disk-space", "Armazenamento", "ok", "Espaço livre na raiz", detail))
    except OSError as error:
        results.append(_check("disk-space", "Armazenamento", "unknown", "Não foi possível medir o espaço livre", str(error)))

    mem = parse_meminfo(read_text("/proc/meminfo"))
    total = mem.get("MemTotal", 0)
    available = mem.get("MemAvailable", mem.get("MemFree", 0))
    if total <= 0:
        results.append(_check("memory", "Memória", "unknown", "Estado da RAM indisponível", "O kernel não forneceu MemTotal em /proc/meminfo."))
    else:
        percent = available / total * 100
        detail = f"{format_bytes(available)} de {format_bytes(total)} estão disponíveis ({percent:.1f}%)."
        if percent < 5:
            results.append(_check("memory", "Memória", "warning", "Pouca memória disponível", detail + " O Chip não encerrará programas automaticamente."))
        else:
            results.append(_check("memory", "Memória", "ok", "Memória disponível", detail))

    nm = run_command(["systemctl", "is-active", "NetworkManager.service"], timeout=4)
    network_state = (nm.stdout or nm.stderr).strip().lower()
    if nm.returncode == 127:
        results.append(_check("network-manager", "Rede", "unknown", "Não foi possível consultar o NetworkManager", nm.stderr))
    elif network_state != "active":
        results.append(_check(
            "network-manager", "Rede", "warning", "O serviço NetworkManager não está ativo",
            f"Estado informado: {network_state or 'desconhecido'}. Reiniciar o serviço pode interromper temporariamente a rede.",
            repair="network" if network_state in {"inactive", "failed"} else None,
        ))
    else:
        results.append(_check("network-manager", "Rede", "ok", "Serviço de rede", "NetworkManager está ativo."))

    if os.environ.get("DBUS_SESSION_BUS_ADDRESS") or os.environ.get("XDG_RUNTIME_DIR"):
        audio_states: list[tuple[str, str]] = []
        for service in ("pipewire.service", "pipewire-pulse.service", "wireplumber.service"):
            state_result = run_command(["systemctl", "--user", "is-active", service], timeout=3)
            state = (state_result.stdout or state_result.stderr).strip().lower()
            if state_result.returncode in (0, 3, 4):
                audio_states.append((service, state or "desconhecido"))
        inactive = [(name, state) for name, state in audio_states if state != "active"]
        if inactive:
            details = "\n".join(f"{name}: {state}" for name, state in inactive)
            results.append(_check(
                "audio", "Áudio", "warning", "Um ou mais serviços de áudio não estão ativos", details + "\nReiniciar o áudio pode interromper sons que estejam tocando.",
                repair="audio",
            ))
        elif audio_states:
            results.append(_check("audio", "Áudio", "ok", "Serviços de áudio", "PipeWire, PipeWire Pulse e WirePlumber estão ativos."))
        else:
            results.append(_check("audio", "Áudio", "unknown", "Estado do áudio não confirmado", "Não foi possível consultar os serviços de áudio da sessão atual."))
    else:
        results.append(_check("audio", "Áudio", "unknown", "Áudio da sessão não consultado", "Não foi detectado um barramento de sessão de usuário. Abra o Chip Fixs dentro da sessão gráfica do usuário para verificar o áudio."))

    failed = run_command(["systemctl", "--failed", "--no-legend", "--plain"], timeout=6)
    failed_lines = [line.strip() for line in failed.stdout.splitlines() if line.strip()]
    if failed.returncode != 0:
        results.append(_check("failed-units", "Serviços", "unknown", "Não foi possível consultar serviços com falha", failed.stderr.strip() or "systemctl --failed retornou erro."))
    elif failed_lines:
        results.append(_check(
            "failed-units", "Serviços", "warning", f"{len(failed_lines)} unidade(s) do sistema com falha",
            "\n".join(failed_lines[:12]) + ("\n… outros resultados omitidos." if len(failed_lines) > 12 else "") +
            "\nUma unidade com falha pode ser opcional. O Chip não reiniciará serviços desconhecidos automaticamente.",
        ))
    else:
        results.append(_check("failed-units", "Serviços", "ok", "Serviços do systemd", "Nenhuma unidade com falha foi informada pelo systemd."))

    if Path("/usr/share/backgrounds/rivet").is_dir():
        missing = [path for path in RIVET_WALLPAPERS if not Path(path).is_file() or Path(path).stat().st_size == 0]
        if missing:
            results.append(_check("rivet-files", "Rivet", "warning", "Um ou mais arquivos visuais do Rivet estão ausentes", "\n".join(missing)))
        else:
            results.append(_check("rivet-files", "Rivet", "ok", "Arquivos visuais do Rivet", "Os quatro wallpapers esperados estão presentes."))
    else:
        results.append(_check("rivet-files", "Rivet", "unknown", "Arquivos do Rivet não encontrados", "Esta instalação não expõe /usr/share/backgrounds/rivet; talvez o programa esteja sendo executado fora do Rivet."))

    # Check whether a graphics controller is visible to PCI enumeration.
    graphics = run_command(["lspci", "-nnk"], timeout=6)
    if graphics.returncode == 127:
        results.append(_check("graphics", "Gráficos", "unknown", "Verificação gráfica indisponível", graphics.stderr))
    elif graphics.returncode != 0:
        results.append(_check("graphics", "Gráficos", "warning", "A consulta aos controladores gráficos falhou", graphics.stderr.strip() or f"lspci retornou código {graphics.returncode}."))
    elif re.search(r"VGA compatible controller|3D controller|Display controller", graphics.stdout, re.I):
        results.append(_check("graphics", "Gráficos", "ok", "Controlador gráfico detectado", "O barramento PCI informa pelo menos um controlador gráfico. Isso não substitui o teste do driver e da aceleração 3D."))
    else:
        results.append(_check("graphics", "Gráficos", "unknown", "Controlador gráfico não confirmado", "Nenhum controlador gráfico foi identificado na saída do lspci. Isso pode ser normal em máquinas sem vídeo PCI ou ambientes virtuais."))

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
            results.append(_check("temperature", "Temperatura", "critical", "Foi detectada uma temperatura muito alta", summary + ". Reduza a carga de trabalho e verifique a ventilação; Chip Fixs não altera as ventoinhas nem desliga o computador."))
        elif hottest_temp >= 85:
            results.append(_check("temperature", "Temperatura", "warning", "Foi detectada uma temperatura elevada", summary + ". A interpretação depende do componente e do sensor."))
        else:
            results.append(_check("temperature", "Temperatura", "ok", "Sensores térmicos do kernel", summary))
    else:
        results.append(_check("temperature", "Temperatura", "unknown", "Temperaturas não disponíveis", "O kernel não expôs zonas térmicas legíveis. Isso não prova que exista um problema de resfriamento."))

    updates = run_command(["apt", "list", "--upgradable"], timeout=12)
    if updates.returncode == 0:
        candidates = [
            line.strip() for line in updates.stdout.splitlines()
            if line.strip() and not line.startswith("Listing...") and "/" in line and not line.startswith("WARNING:")
        ]
        if candidates:
            results.append(_check("updates", "Pacotes", "warning", f"{len(candidates)} pacote(s) podem ter atualização disponível", "A lista usa o cache local e pode estar desatualizada. O Chip não instala atualizações automaticamente."))
        else:
            results.append(_check("updates", "Pacotes", "ok", "Cache local de atualizações", "Nenhum pacote atualizável foi informado pelo cache local. O resultado não verifica se as listas de pacotes estão atualizadas."))
    else:
        results.append(_check("updates", "Pacotes", "unknown", "Estado das atualizações não confirmado", updates.stderr.strip() or "O APT não conseguiu consultar seu cache local."))

    journal = run_command(["journalctl", "-b", "-p", "err", "--no-pager", "-n", "50", "-q"], timeout=8)
    if journal.returncode == 0:
        error_lines = [line for line in journal.stdout.splitlines() if line.strip()]
        if error_lines:
            results.append(_check("journal-errors", "Registros do sistema", "warning", f"{len(error_lines)} registro(s) de nível erro no log recente", "O log pode conter mensagens antigas, transitórias ou específicas do hardware. O Chip não modifica o journal nem tenta reparar causas desconhecidas automaticamente."))
        else:
            results.append(_check("journal-errors", "Registros do sistema", "ok", "Erros recentes no journal", "Não foram retornadas mensagens de nível erro no trecho recente do boot atual."))
    else:
        results.append(_check("journal-errors", "Registros do sistema", "unknown", "Leitura do journal indisponível", "Não foi possível ler o journal do boot atual; isso pode depender das permissões da conta."))

    return results


def repair_action(action: str) -> tuple[bool, str]:
    """Executa apenas ações de reparo de uma lista fechada."""
    if action == "audio":
        command = ["systemctl", "--user", "restart", "pipewire.service", "pipewire-pulse.service", "wireplumber.service"]
        result = run_command(command, timeout=20)
        if result.returncode == 0:
            return True, "Os serviços de áudio receberam o comando de reinicialização."
        detail = (result.stdout + "\n" + result.stderr).strip()
        return False, detail or f"systemctl retornou código {result.returncode}."

    if action == "network":
        pkexec = find_command("pkexec")
        systemctl = find_command("systemctl")
        if not pkexec or not systemctl:
            return False, "Não foi encontrado pkexec ou systemctl. Nenhuma alteração foi feita."
        # Ação fixa e visível. Nenhum comando vem de entrada do usuário.
        result = run_command([pkexec, systemctl, "restart", "NetworkManager.service"], timeout=30)
        if result.returncode == 0:
            return True, "O NetworkManager foi reiniciado. A conexão pode levar alguns segundos para voltar."
        detail = (result.stdout + "\n" + result.stderr).strip()
        return False, detail or f"A reinicialização foi cancelada ou falhou (código {result.returncode})."

    return False, "Essa ação não faz parte da lista de reparos permitidos. Nenhuma alteração foi feita."


def read_advanced_memory() -> tuple[bool, str]:
    """Lê o inventário SMBIOS da RAM apenas após a autorização do usuário."""
    pkexec = find_command("pkexec")
    dmidecode = find_command("dmidecode")
    if not pkexec or not dmidecode:
        return False, "É necessário ter pkexec e dmidecode instalados. Nenhuma alteração foi feita."
    result = run_command([pkexec, dmidecode, "--type", "memory"], timeout=15)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output or f"dmidecode retornou código {result.returncode} sem detalhes."


def read_smart_health(device: str) -> tuple[bool, str]:
    """Consulta a saúde SMART de um dispositivo escolhido pelo usuário."""
    allowed_devices = {path for path, _label in list_physical_disks()}
    if device not in allowed_devices:
        return False, "Dispositivo não reconhecido pela lista atual de discos físicos. Nenhuma ação foi executada."
    pkexec = find_command("pkexec")
    smartctl = find_command("smartctl")
    if not pkexec or not smartctl:
        return False, "É necessário ter pkexec e smartmontools instalados. Nenhuma alteração foi feita."
    result = run_command([pkexec, smartctl, "-H", device], timeout=20)
    output = (result.stdout + "\n" + result.stderr).strip()
    # O smartctl usa códigos diferentes para advertências SMART. O texto continua sendo exibido.
    return result.returncode == 0, output or f"smartctl retornou código {result.returncode}."
