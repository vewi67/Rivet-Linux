#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PACKAGE_LIST="build/config/package-lists/rivet.list.chroot"
BRANDING_HOOK="build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot"
SLIDESHOW_HOOK="build/config/hooks/normal/0900-configure-rivet-calamares-slideshow.hook.chroot"
BRANDING_DESC="build/config/includes.chroot/etc/calamares/branding/rivet/branding.desc"
BRANDING_SLIDESHOW="build/config/includes.chroot/etc/calamares/branding/rivet/show.qml"
CHIP_DIR="build/config/includes.chroot/usr/share/rivet/chip"
WELCOME_APP="build/config/includes.chroot/usr/bin/rivet-welcome"
INSTALLER_HELPER="build/config/includes.chroot/usr/bin/rivet-installer"
WELCOME_AUTOSTART="build/config/includes.chroot/etc/xdg/autostart/rivet-welcome.desktop"
WELCOME_LAUNCHER="build/config/includes.chroot/usr/share/applications/rivet-welcome.desktop"
RIVET_INSTALLER_LAUNCHER="build/config/includes.chroot/usr/share/applications/rivet-installer.desktop"
PLANK_AUTOSTART="build/config/includes.chroot/etc/xdg/autostart/rivet-plank.desktop"
ATMOSPHERE_APP="build/config/includes.chroot/usr/bin/rivet-atmosphere"
ATMOSPHERE_GUARD="build/config/includes.chroot/usr/bin/rivet-wallpaper-guard"
ATMOSPHERE_DESKTOP="build/config/includes.chroot/usr/share/applications/rivet-atmosphere.desktop"
INSTALLER_PIPELINE_CHECKER="build/config/includes.chroot/usr/lib/rivet/check-installer-pipeline.py"
CHIP_FIXS_APP="build/config/includes.chroot/usr/bin/chip-fixs"
CHIP_FIXS_CORE="build/config/includes.chroot/usr/lib/chip-fixs/core.py"
CHIP_FIXS_DESKTOP="build/config/includes.chroot/usr/share/applications/chip-fixs.desktop"

required_files=(
  README.md AGENTS.md CONTRIBUTING.md
  scripts/test-wallpaper-defaults.py scripts/test-atmosphere.py scripts/test-chip-fixs.py
  build/README.md build/build.sh
  "$BRANDING_HOOK" "$SLIDESHOW_HOOK" "$BRANDING_DESC" "$BRANDING_SLIDESHOW" "$PACKAGE_LIST" "$WELCOME_APP" "$INSTALLER_HELPER"
  "$WELCOME_AUTOSTART" "$WELCOME_LAUNCHER" "$RIVET_INSTALLER_LAUNCHER" "$PLANK_AUTOSTART"
  "$ATMOSPHERE_APP" "$ATMOSPHERE_GUARD" "$ATMOSPHERE_DESKTOP" "$INSTALLER_PIPELINE_CHECKER"
  "$CHIP_FIXS_APP" "$CHIP_FIXS_CORE" "$CHIP_FIXS_DESKTOP"
  "$CHIP_DIR/README.md"
  .github/workflows/build-iso.yml .github/workflows/validate.yml
  config/README.md scripts/README.md
  docs/philosophy.md docs/architecture.md docs/roadmap.md docs/visual-assets.md
)

echo "==> Checking required files..."
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    echo "ERROR: missing required file: $file" >&2
    exit 1
  }
done

echo "==> Checking shell syntax..."
bash -n build/build.sh
bash -n "$BRANDING_HOOK"
bash -n "$SLIDESHOW_HOOK"
sh -n "$ATMOSPHERE_GUARD"
bash -n scripts/validate-repo.sh

echo "==> Extracting and checking the generated wallpaper startup script..."
python3 - "$BRANDING_HOOK" /tmp/rivet-set-wallpaper-validation.sh <<'PY'
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8")
begin = "cat > /usr/local/bin/rivet-set-wallpaper <<'EOF'\n"
end = "\nEOF\nchmod 0755 /usr/local/bin/rivet-set-wallpaper"
start = source.find(begin)
if start < 0:
    raise SystemExit("ERROR: wallpaper startup script heredoc is missing.")
start += len(begin)
finish = source.find(end, start)
if finish < 0:
    raise SystemExit("ERROR: wallpaper startup script heredoc is unterminated.")
Path(sys.argv[2]).write_text(source[start:finish] + "\n", encoding="utf-8")
PY
sh -n /tmp/rivet-set-wallpaper-validation.sh

echo "==> Checking Python syntax..."
PYTHONPYCACHEPREFIX=/tmp/rivet-pycache python3 -m py_compile "$WELCOME_APP" "$INSTALLER_HELPER" "$ATMOSPHERE_APP" "$INSTALLER_PIPELINE_CHECKER" "$CHIP_FIXS_APP" "$CHIP_FIXS_CORE" scripts/test-wallpaper-defaults.py scripts/test-atmosphere.py scripts/test-chip-fixs.py
python3 scripts/test-wallpaper-defaults.py
python3 scripts/test-atmosphere.py
python3 scripts/test-chip-fixs.py
python3 "$INSTALLER_PIPELINE_CHECKER" --self-test

echo "==> Checking package list..."
mapfile -t packages < <(sed '/^[[:space:]]*$/d; /^[[:space:]]*#/d' "$PACKAGE_LIST")
[[ ${#packages[@]} -gt 0 ]] || {
  echo "ERROR: package list is empty." >&2
  exit 1
}

if printf '%s\n' "${packages[@]}" | grep -qvE '^[a-z0-9][a-z0-9+.-]*$'; then
  echo "ERROR: package list contains an invalid package name." >&2
  printf '%s\n' "${packages[@]}" >&2
  exit 1
fi

duplicates="$(printf '%s\n' "${packages[@]}" | sort | uniq -d)"
if [[ -n "$duplicates" ]]; then
  echo "ERROR: duplicate package names found:" >&2
  printf '%s\n' "$duplicates" >&2
  exit 1
fi

require_package() {
  local package="$1"
  grep -Fxq "$package" "$PACKAGE_LIST" || {
    echo "ERROR: required package is missing: $package" >&2
    exit 1
  }
}

echo "==> Checking required packages..."
for package in \
  xfce4 xfce4-panel xfce4-terminal thunar plank lightdm lightdm-gtk-greeter xserver-xorg \
  network-manager network-manager-gnome pipewire pipewire-pulse wireplumber \
  mate-polkit polkitd pkexec x11-xserver-utils x11-utils firefox-esr calamares \
  calamares-settings-debian rsync squashfs-tools sudo python3-gi gir1.2-gtk-3.0 dmidecode smartmontools lm-sensors mesa-utils; do
  require_package "$package"
done

echo "==> Checking build and branding identity..."
for setting in \
  '--distribution trixie' \
  '--architectures amd64' \
  '--binary-images iso-hybrid' \
  '--iso-application "Rivet Linux"' \
  '--iso-publisher "Rivet Linux Project"' \
  '--iso-volume "RIVET_LINUX"' \
  '--archive-areas "main contrib non-free non-free-firmware"' \
  '--firmware-binary true' \
  '--firmware-chroot true'; do
  grep -Fq -- "$setting" build/build.sh || {
    echo "ERROR: build identity setting missing: $setting" >&2
    exit 1
  }
done
grep -Fxq '    productName: Rivet Linux' "$BRANDING_DESC"
grep -Fxq '    shortProductName: Rivet' "$BRANDING_DESC"
grep -Fxq '    bootloaderEntryName: Rivet Linux' "$BRANDING_DESC"
grep -Fxq '    productLogo: "rivet.logo.png"' "$BRANDING_DESC"
grep -Fxq '    productIcon: "rivet.logo.png"' "$BRANDING_DESC"
grep -Fxq '    productWelcome: "rivet.logo.png"' "$BRANDING_DESC"
grep -Fxq 'style: {}' "$BRANDING_DESC"
grep -Fxq 'uploadServer: {}' "$BRANDING_DESC"
grep -Fq 'name: Build Rivet ISO' .github/workflows/build-iso.yml
grep -Fq 'name: Publish ISO as a GitHub Release' .github/workflows/build-iso.yml
grep -Fq 'split -b 1800M' .github/workflows/build-iso.yml
grep -Fq 'reassemble-rivet-iso.sh' .github/workflows/build-iso.yml
grep -Fq 'build/release-assets/*' .github/workflows/build-iso.yml
grep -Fq 'tag_name: rivet-build-' .github/workflows/build-iso.yml
grep -Fq 'name: Validate Rivet' .github/workflows/validate.yml
grep -Fq 'name: Debian Trixie installer integration' .github/workflows/validate.yml
grep -Fq 'container: debian:trixie' .github/workflows/validate.yml
grep -Fq 'calamares-settings-debian' .github/workflows/validate.yml
grep -Fq 'check-installer-pipeline.py --root /' .github/workflows/validate.yml
# Keep the ISO build opt-in: ordinary pushes must never build or publish an ISO.
if grep -Eq '^[[:space:]]+push:' .github/workflows/build-iso.yml; then
  echo "ERROR: ISO build workflow must not have a push trigger." >&2
  exit 1
fi
grep -Fq 'default: "NO"' .github/workflows/build-iso.yml
grep -Fq "if: inputs.authorize_iso == 'YES'" .github/workflows/build-iso.yml

echo "==> Checking XFCE status-panel XML..."
python3 - "$BRANDING_HOOK" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

hook = Path(sys.argv[1]).read_text(encoding="utf-8")
match = re.search(r"""cat > "\$panel_file" <<'EOF'\n(.*?)\nEOF""", hook, re.S)
if not match:
    raise SystemExit("ERROR: could not find the generated XFCE panel XML in the branding hook.")
try:
    root = ET.fromstring(match.group(1))
except ET.ParseError as error:
    raise SystemExit(f"ERROR: generated XFCE panel XML is invalid: {error}")

if root.tag != "channel" or root.attrib.get("name") != "xfce4-panel":
    raise SystemExit("ERROR: generated XML is not an XFCE panel configuration.")
plugins = {
    item.attrib.get("name"): item.attrib.get("value")
    for item in root.findall("./property[@name='plugins']/property")
}
if plugins.get("plugin-1") != "systray":
    raise SystemExit("ERROR: XFCE status panel must provide a system tray for NetworkManager.")
if plugins.get("plugin-2") != "clock":
    raise SystemExit("ERROR: XFCE status panel clock plugin is missing.")
panels = root.find("./property[@name='panels']")
panel = panels.find("./property[@name='panel-1']") if panels is not None else None
if panel is None:
    raise SystemExit("ERROR: XFCE panel configuration does not define panel-1.")
position = panel.find("./property[@name='position']")
if position is None or not position.attrib.get("value", "").startswith("p=6;"):
    raise SystemExit("ERROR: XFCE status panel must be positioned at the top.")
print("XFCE status-panel XML is valid; system tray and clock are configured.")
PY

echo "==> Checking required visual assets..."
for asset in \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-waves.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-factory.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-chip.jpeg \
  build/config/includes.chroot/usr/share/backgrounds/rivet/rivet-prism.jpeg \
  build/config/includes.chroot/etc/calamares/branding/rivet/rivet.logo.png; do
  [[ -s "$asset" ]] || {
    echo "ERROR: missing or empty Rivet asset: $asset" >&2
    exit 1
  }
done

echo "==> Checking Chip and desktop integration..."
chip_count="$(find "$CHIP_DIR" -maxdepth 1 -type f -name '*.png' | wc -l)"
if [[ "$chip_count" -lt 5 ]]; then
  echo "ERROR: expected at least five Chip PNG poses, found $chip_count." >&2
  exit 1
fi

grep -Fq 'Exec=/usr/bin/rivet-welcome' "$WELCOME_AUTOSTART"
grep -Fq 'OnlyShowIn=XFCE;' "$WELCOME_AUTOSTART"
grep -Fq 'Exec=/usr/bin/rivet-welcome --show-again' "$WELCOME_LAUNCHER"
grep -Fq 'Icon=rivet' "$WELCOME_LAUNCHER"
grep -Fq 'Welcome to Rivet Linux' "$WELCOME_APP"
grep -Fq 'CHIP_DIR = "/usr/share/rivet/chip"' "$WELCOME_APP"
grep -Fq -- '--show-again' "$WELCOME_APP"
grep -Fq 'Install Rivet' "$WELCOME_APP"
grep -Fq 'INSTALLER = "/usr/bin/rivet-installer"' "$WELCOME_APP"
grep -Fq 'rivet-atmosphere' "$WELCOME_APP"
grep -Fq 'Gtk.Button(label="Atmosphere")' "$WELCOME_APP"
grep -Fq 'STOCK_LAUNCHER = "/usr/bin/calamares-install-debian"' "$INSTALLER_HELPER"
grep -Fq 'PIPELINE_CHECKER = "/usr/lib/rivet/check-installer-pipeline.py"' "$INSTALLER_HELPER"
grep -Fq 'Installer pipeline preflight passed:' "$INSTALLER_HELPER"
grep -Fq 'python3 "$INSTALLER_CHECKER" --root /' "$SLIDESHOW_HOOK"
grep -Fq 'prompt-install: true' "$BRANDING_HOOK"
grep -Fq 'disable-cancel-during-exec: true' "$BRANDING_HOOK"
grep -Fq 'ROOT_CALAMARES_LOG = "/root/.cache/calamares/session.log"' "$INSTALLER_HELPER"
grep -Fq 'WINDOW_CLASS = "calamares"' "$INSTALLER_HELPER"
grep -Fq 'xprop' "$INSTALLER_HELPER"
grep -Fq 'WM_CLASS' "$INSTALLER_HELPER"
grep -Fq 'def root_calamares_log_signature()' "$INSTALLER_HELPER"
grep -Fq 'Existing session.log is unchanged; omitting it to avoid stale diagnostics.' "$INSTALLER_HELPER"
grep -Fq 'cmdline' "$INSTALLER_HELPER"
grep -Fq 'GTK diagnostic UI unavailable' "$INSTALLER_HELPER"
grep -Fq 'not considered proof that the installer window opened' "$INSTALLER_HELPER"

echo "==> Checking Chip Fixs integration and safety surface..."
grep -Fq 'Name=Chip Fixs' "$CHIP_FIXS_DESKTOP"
grep -Fq 'Exec=/usr/bin/chip-fixs' "$CHIP_FIXS_DESKTOP"
grep -Fq 'Icon=chip-fixs' "$CHIP_FIXS_DESKTOP"
grep -Fq 'Fix System' "$CHIP_FIXS_APP"
grep -Fq 'System Info' "$CHIP_FIXS_APP"
grep -Fq 'run_diagnostics' "$CHIP_FIXS_CORE"
grep -Fq 'repair_action' "$CHIP_FIXS_CORE"
grep -Fq 'read_advanced_memory' "$CHIP_FIXS_CORE"
grep -Fq 'read_smart_health' "$CHIP_FIXS_CORE"
grep -Fq 'CHIP_FIXS_ICON=' "$BRANDING_HOOK"
grep -Fq 'CHIP_FIXS_MASCOT=' "$BRANDING_HOOK"
grep -Fq 'chmod 0755 /usr/bin/chip-fixs' "$BRANDING_HOOK"
grep -Fq 'cp "$CHIP_FIXS_MASCOT" "$CHIP_FIXS_ICON"' "$BRANDING_HOOK"
grep -Fq 'Chip-Fixs.dockitem' "$BRANDING_HOOK"
grep -Fq 'Launcher=file:///usr/share/applications/chip-fixs.desktop' "$BRANDING_HOOK"
grep -Fq 'launch_app, ["chip-fixs"]' "$WELCOME_APP"
grep -Fq 'dmidecode' "$PACKAGE_LIST"
grep -Fq 'smartmontools' "$PACKAGE_LIST"
grep -Fq 'lm-sensors' "$PACKAGE_LIST"
grep -Fq 'mesa-utils' "$PACKAGE_LIST"

grep -Fq 'Exec=plank' "$PLANK_AUTOSTART"
grep -Fq 'OnlyShowIn=XFCE;' "$PLANK_AUTOSTART"
grep -Fq 'plank' "$BRANDING_HOOK"
grep -Fq 'mate-polkit' "$PACKAGE_LIST"
grep -Fq 'rivet-polkit-agent.desktop' "$BRANDING_HOOK"
grep -Fq 'polkit-mate-authentication-agent-1' "$BRANDING_HOOK"
grep -Fq 'OnlyShowIn=XFCE;' "$BRANDING_HOOK"
grep -Fq 'Position=3' "$BRANDING_HOOK"
grep -Fq 'Firefox.dockitem' "$BRANDING_HOOK"
grep -Fq 'Install-Rivet.dockitem' "$BRANDING_HOOK"
grep -Fq 'rivet-settings.desktop' "$BRANDING_HOOK"
grep -Fq 'rivet-wallpaper-guard --once' "$BRANDING_HOOK"
grep -Fq 'Name=Rivet Atmosphere Service' "$BRANDING_HOOK"
grep -Fq 'Exec=/usr/bin/rivet-wallpaper-guard' "$BRANDING_HOOK"
grep -Fq 'atmosphere-mode' "$BRANDING_HOOK"
grep -Fq 'Atmosphere.dockitem' "$BRANDING_HOOK"
grep -Fq 'rivet-atmosphere.desktop' "$BRANDING_HOOK"
grep -Fq 'Exec=/usr/bin/rivet-atmosphere' "$ATMOSPHERE_DESKTOP"
grep -Fq 'Rivet Atmosphere' "$ATMOSPHERE_APP"
grep -Fq 'workspace-?' "$ATMOSPHERE_APP"
grep -Fq '/workspace-?[0-9]+' "$ATMOSPHERE_GUARD"
grep -Fq 'backdrop-cycle-period" int 1' "$ATMOSPHERE_GUARD"
grep -Fq 'backdrop-cycle-timer" uint 30' "$ATMOSPHERE_GUARD"
grep -Fq 'backdrop-cycle-random-order" bool true' "$ATMOSPHERE_GUARD"
grep -Fq 'backdrop-cycle-enable" bool true' "$ATMOSPHERE_GUARD"
grep -Fq 'workspace0' "$BRANDING_HOOK"
grep -Fq 'last-image' "$BRANDING_HOOK"
grep -Fq 'rivet-set-wallpaper' "$BRANDING_HOOK"
grep -Fq 'pgrep -x xfdesktop' "$BRANDING_HOOK"
grep -Fq 'xrandr --query' "$BRANDING_HOOK"
grep -Fq 'monitor([^/]+)' "$BRANDING_HOOK"
grep -Fq 'workspace$workspace/last-image' "$BRANDING_HOOK"
grep -Fq -- '--create --type string --set "$WALLPAPER"' "$BRANDING_HOOK"
grep -Fq 'Preserving user wallpaper' "$BRANDING_HOOK"
grep -Fq 'Rivet Waves wallpaper properties verified' "$BRANDING_HOOK"
if grep -Fq '[ -e "$MARKER" ] && exit 0' "$BRANDING_HOOK"; then
  echo "ERROR: wallpaper startup still has a permanent one-time skip marker." >&2
  exit 1
fi
# NetworkManager's graphical applet requires the status bar's system tray.
grep -Fq 'value="systray"' "$BRANDING_HOOK"
grep -Fq 'value="clock"' "$BRANDING_HOOK"
if grep -Fq 'xfce4-panel --quit' "$BRANDING_HOOK"; then
  echo "ERROR: XFCE panel is being shut down; NetworkManager's applet would have no system tray." >&2
  exit 1
fi
grep -Fq 'xfce4-panel.xml' "$BRANDING_HOOK"
grep -Fq 'RIVET_WALLPAPER_DIR="/usr/share/backgrounds/rivet"' "$BRANDING_HOOK"
grep -Fq 'rivet-waves.jpeg' "$BRANDING_HOOK"
grep -Fq 'branding: rivet' "$BRANDING_HOOK"
grep -Fq 'slideshow: "show.qml"' "$BRANDING_DESC"
grep -Fq 'slideshowAPI: 2' "$BRANDING_DESC"
grep -Fq 'Presentation {' "$BRANDING_SLIDESHOW"
grep -Fq 'title: qsTr("Instalando o Rivet Linux")' "$BRANDING_SLIDESHOW"
grep -Fq 'RIVET PONG' "$BRANDING_SLIDESHOW"
grep -Fq 'mouseNavigation: false' "$BRANDING_SLIDESHOW"
grep -Fq 'property int targetScore: 5' "$BRANDING_SLIDESHOW"
grep -Fq 'function advanceGame()' "$BRANDING_SLIDESHOW"
grep -Fq 'function awardPlayerPoint()' "$BRANDING_SLIDESHOW"
grep -Fq 'function awardComputerPoint()' "$BRANDING_SLIDESHOW"
grep -Fq 'onPositionChanged:' "$BRANDING_SLIDESHOW"
grep -Fq 'id: gameTimer' "$BRANDING_SLIDESHOW"
grep -Fq 'calamares-install-debian' "$BRANDING_HOOK"
grep -Fq 'NoDisplay=true' "$BRANDING_HOOK"
grep -Fq 'rivet-installer.desktop' "$BRANDING_HOOK"
grep -Fq 'rm -f /etc/xdg/autostart/calamares-desktop-icon.desktop' "$BRANDING_HOOK"
grep -Fq 'Exec=/usr/bin/rivet-installer' "$RIVET_INSTALLER_LAUNCHER"
grep -Fq 'TryExec=/usr/bin/rivet-installer' "$RIVET_INSTALLER_LAUNCHER"
grep -Fq 'Icon=rivet' "$RIVET_INSTALLER_LAUNCHER"
grep -Fq 'Name=Install Rivet Linux' "$RIVET_INSTALLER_LAUNCHER"

echo "==> Checking documentation language..."
if grep -RniE '(^|[[:space:]])(para|uma|das|dos|não|aqui|deve|somente|pacotes|instalar|teste|experiência|configuração|usuário)([[:space:]]|$)' \
  README.md AGENTS.md CONTRIBUTING.md docs build/README.md build/config config scripts .github/pull_request_template.md \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.sh' --exclude-dir='.git' \
  >/tmp/rivet-portuguese-check.txt 2>/dev/null; then
  echo "ERROR: possible Portuguese text found in project documentation:" >&2
  cat /tmp/rivet-portuguese-check.txt >&2
  exit 1
fi

echo "==> Repository validation passed."
