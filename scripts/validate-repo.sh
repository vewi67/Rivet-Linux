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
WELCOME_CENTER_APP="build/config/includes.chroot/usr/bin/rivet-welcome-center"
WELCOME_MODE_TEST="scripts/test-welcome-mode.py"
WELCOME_CENTER_TEST="scripts/test-welcome-center.py"
WELCOME_CENTER_GTK_TEST="scripts/test-welcome-center-gtk.py"
DOCK_HELPER="build/config/includes.chroot/usr/bin/rivet-start-plank"
DOCK_TEST="scripts/test-rivet-dock-mode.py"
PASSWORD_POLICY_HELPER="build/config/includes.chroot/usr/lib/rivet/configure-calamares-password-policy.py"
PASSWORD_POLICY_TEST="scripts/test-calamares-password-policy.py"
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
CHIP_FIXS_LOGO_SOURCE="assets/chip-fixs/logo.png"
CHIP_FIXS_LOGO_INCLUDE="build/config/includes.chroot/usr/share/rivet/chip-fixs/logo.png"
BOOT_HOOK="build/config/hooks/normal/0200-configure-rivet-boot-and-locale.hook.chroot"
PLYMOUTH_THEME="build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.plymouth"
PLYMOUTH_SCRIPT="build/config/includes.chroot/usr/share/plymouth/themes/rivet/rivet.script"

required_files=(
  README.md AGENTS.md CONTRIBUTING.md
  scripts/test-wallpaper-defaults.py scripts/test-atmosphere.py scripts/test-chip-fixs.py "$WELCOME_MODE_TEST" "$WELCOME_CENTER_TEST" "$WELCOME_CENTER_GTK_TEST" "$DOCK_TEST" "$PASSWORD_POLICY_TEST"
  build/README.md build/build.sh
  "$BRANDING_HOOK" "$SLIDESHOW_HOOK" "$BRANDING_DESC" "$BRANDING_SLIDESHOW" "$PACKAGE_LIST" "$WELCOME_APP" "$WELCOME_CENTER_APP" "$DOCK_HELPER" "$INSTALLER_HELPER"
  "$WELCOME_AUTOSTART" "$WELCOME_LAUNCHER" "$RIVET_INSTALLER_LAUNCHER" "$PLANK_AUTOSTART"
  "$ATMOSPHERE_APP" "$ATMOSPHERE_GUARD" "$ATMOSPHERE_DESKTOP" "$INSTALLER_PIPELINE_CHECKER"
  "$CHIP_FIXS_APP" "$CHIP_FIXS_CORE" "$CHIP_FIXS_DESKTOP"
  "$CHIP_FIXS_LOGO_SOURCE" "$CHIP_FIXS_LOGO_INCLUDE" assets/chip-fixs/README.md
  "$PASSWORD_POLICY_HELPER"
  "$BOOT_HOOK" "$PLYMOUTH_THEME" "$PLYMOUTH_SCRIPT"
  "$CHIP_DIR/README.md"
  .github/workflows/build-iso.yml .github/workflows/validate.yml
  config/README.md scripts/README.md
  docs/philosophy.md docs/architecture.md docs/roadmap.md docs/visual-assets.md docs/decisions/0006-software-management.md docs/decisions/0007-chip-fixs.md docs/decisions/0008-boot-theme-and-english-first.md
)

echo "==> Checking required files..."
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || {
    echo "ERROR: missing required file: $file" >&2
    exit 1
  }
done

echo "==> Checking tracked executable modes for live-build hooks..."
hook_index="$(git ls-files --stage -- 'build/config/hooks/normal/*.hook.chroot')"
if [[ -z "$hook_index" ]]; then
  echo "ERROR: no tracked live-build hooks were found." >&2
  exit 1
fi
if printf '%s\n' "$hook_index" | grep -qv '^100755 '; then
  echo "ERROR: every live-build hook must be tracked with Git mode 100755." >&2
  printf '%s\n' "$hook_index" >&2
  exit 1
fi

echo "==> Checking executable modes for installed Rivet commands..."
bin_index="$(git ls-files --stage -- 'build/config/includes.chroot/usr/bin/*')"
if [[ -z "$bin_index" ]]; then
  echo "ERROR: no installed Rivet commands are tracked under usr/bin." >&2
  exit 1
fi
if printf '%s\n' "$bin_index" | grep -qv '^100755 '; then
  echo "ERROR: every script installed under usr/bin must be tracked with Git mode 100755." >&2
  printf '%s\n' "$bin_index" >&2
  exit 1
fi

echo "==> Checking shell syntax..."
bash -n build/build.sh
bash -n "$BRANDING_HOOK"
sh -n "$BRANDING_HOOK"
bash -n "$SLIDESHOW_HOOK"
echo "==> Checking branding-hook structure..."
if [[ "$(grep -Fc 'CALAMARES_SETTINGS="/etc/calamares/settings.conf"' "$BRANDING_HOOK")" -ne 1 ]]; then
  echo "ERROR: the branding hook must configure Calamares settings exactly once." >&2
  exit 1
fi
if [[ "$(grep -Fc 'echo "Rivet desktop, Atmosphere, dock, installer authentication, branding, and welcome experience configured."' "$BRANDING_HOOK")" -ne 1 ]]; then
  echo "ERROR: the branding hook must have exactly one final success message." >&2
  exit 1
fi
grep -Fq "grep -Eq '^Url=https://dl\\.flathub\\.org/repo/?$'" "$BRANDING_HOOK" || {
  echo "ERROR: Flathub URL validation is missing or incomplete." >&2
  exit 1
}
grep -Fq "grep -Eq '^GPGKey=.+$'" "$BRANDING_HOOK" || {
  echo "ERROR: Flathub signing-key validation is missing or incomplete." >&2
  exit 1
}
if [[ "$(grep -Fc "grep -Eq '^GPGKey=.+$' /etc/flatpak/remotes.d/flathub.flatpakrepo" "$BRANDING_HOOK")" -ne 1 ]]; then
  echo "ERROR: expected exactly one complete Flathub signing-key validation." >&2
  exit 1
fi
sh -n "$ATMOSPHERE_GUARD"
sh -n "$BOOT_HOOK"
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
PYTHONPYCACHEPREFIX=/tmp/rivet-pycache python3 -m py_compile "$WELCOME_APP" "$WELCOME_CENTER_APP" "$DOCK_HELPER" "$INSTALLER_HELPER" "$ATMOSPHERE_APP" "$INSTALLER_PIPELINE_CHECKER" "$PASSWORD_POLICY_HELPER" "$CHIP_FIXS_APP" "$CHIP_FIXS_CORE" "$WELCOME_MODE_TEST" "$WELCOME_CENTER_TEST" "$WELCOME_CENTER_GTK_TEST" "$DOCK_TEST" "$PASSWORD_POLICY_TEST" scripts/test-wallpaper-defaults.py scripts/test-atmosphere.py scripts/test-chip-fixs.py
python3 "$WELCOME_MODE_TEST"
python3 "$WELCOME_CENTER_TEST"
python3 "$DOCK_TEST"
python3 "$PASSWORD_POLICY_TEST"
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
  xfce4 xfce4-panel xfce4-terminal xfce4-notifyd xfce4-power-manager thunar plank lightdm lightdm-gtk-greeter xserver-xorg \
  network-manager network-manager-gnome blueman pipewire pipewire-pulse pavucontrol wireplumber \
  mate-polkit polkitd pkexec x11-xserver-utils x11-utils firefox-esr \
  gnome-software gnome-software-plugin-deb gnome-software-plugin-flatpak flatpak calamares \
  calamares-settings-debian rsync squashfs-tools sudo python3-gi gir1.2-gtk-3.0 dmidecode smartmontools lm-sensors mesa-utils locales plymouth plymouth-themes; do
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
grep -Fq 'quiet splash locales=en_US.UTF-8' build/build.sh
grep -Fq 'LANG=en_US.UTF-8' "$BOOT_HOOK"
grep -Fq 'LC_MESSAGES=en_US.UTF-8' "$BOOT_HOOK"
grep -Fq 'plymouth-set-default-theme -R rivet' "$BOOT_HOOK"
grep -Fxq 'Name=Rivet Linux' "$PLYMOUTH_THEME"
grep -Fxq 'ModuleName=script' "$PLYMOUTH_THEME"
grep -Fq 'ScriptFile=/usr/share/plymouth/themes/rivet/rivet.script' "$PLYMOUTH_THEME"
grep -Fq 'logo.base_image.Rotate((2 * Math.Pi * index) / logo.frame_count)' "$PLYMOUTH_SCRIPT"
grep -Fq 'Plymouth.SetRefreshFunction(refresh_callback)' "$PLYMOUTH_SCRIPT"
grep -Fq 'Plymouth.SetBootProgressFunction(progress_callback)' "$PLYMOUTH_SCRIPT"
grep -Fq 'Let us Do the Magic' "$PLYMOUTH_SCRIPT"
grep -Fq 'Welcome to Rivet Linux' "$PLYMOUTH_SCRIPT"
for legacy_ui_text in 'ATENÇÃO' 'NÃO CONFIRMADO' 'Voltar ao início' 'Verificar agora' 'Opa! Eu sou o Chip.' 'Não disponível' 'Instalando o Rivet Linux' 'VOCÊ VENCEU!'; do
  if grep -Fq "$legacy_ui_text" "$CHIP_FIXS_APP" "$CHIP_FIXS_CORE" "$BRANDING_SLIDESHOW"; then
    echo "ERROR: Portuguese UI string remains in the English-first interface: $legacy_ui_text" >&2
    exit 1
  fi
done
grep -Fxq '    productName: Rivet Linux' "$BRANDING_DESC"
grep -Fxq '    shortProductName: Rivet' "$BRANDING_DESC"
grep -Fxq '    bootloaderEntryName: Rivet Linux' "$BRANDING_DESC"
grep -Fxq '    productLogo: "rivet.logo.png"' "$BRANDING_DESC"
grep -Fxq '    productIcon: "rivet.icon.png"' "$BRANDING_DESC"
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
grep -Fq 'name: Debian Trixie installer integration' .github/workflows/build-iso.yml
grep -Fq 'needs: [validate, installer-package-validation]' .github/workflows/build-iso.yml
grep -Fq 'xvfb-run -a python3 scripts/test-welcome-center-gtk.py' .github/workflows/build-iso.yml
grep -Fq 'container: debian:trixie' .github/workflows/validate.yml
grep -Fq 'calamares-settings-debian' .github/workflows/validate.yml
grep -Fq 'check-installer-pipeline.py --root /' .github/workflows/validate.yml
grep -Fq 'check-installer-pipeline.py --root /' .github/workflows/build-iso.yml
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

echo "==> Checking Chip Fixs logo files..."
for asset in "$CHIP_FIXS_LOGO_SOURCE" "$CHIP_FIXS_LOGO_INCLUDE"; do
  [[ -s "$asset" ]] || {
    echo "ERROR: missing or empty Chip Fixs logo: $asset" >&2
    exit 1
  }
done
if ! cmp -s "$CHIP_FIXS_LOGO_SOURCE" "$CHIP_FIXS_LOGO_INCLUDE"; then
  echo "ERROR: source and live-build copies of the Chip Fixs logo differ." >&2
  exit 1
fi
python3 - "$CHIP_FIXS_LOGO_SOURCE" <<'PY'
import struct
import sys
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
    raise SystemExit("ERROR: Chip Fixs logo is not a valid PNG with an IHDR header.")
width, height = struct.unpack(">II", data[16:24])
if width != height or width < 256 or height < 256:
    raise SystemExit(f"ERROR: Chip Fixs logo must be square and at least 256x256; found {width}x{height}.")
print(f"Chip Fixs logo PNG validated: {width}x{height}.")
PY

echo "==> Checking Chip and desktop integration..."
chip_count="$(find "$CHIP_DIR" -maxdepth 1 -type f -name '*.png' | wc -l)"
if [[ "$chip_count" -lt 5 ]]; then
  echo "ERROR: expected at least five Chip PNG poses, found $chip_count." >&2
  exit 1
fi

grep -Fq 'Exec=/usr/bin/rivet-welcome' "$WELCOME_AUTOSTART"
grep -Fq 'chmod 0755 /usr/bin/rivet-welcome-center' "$BRANDING_HOOK"
grep -Fq 'chmod 0755 /usr/bin/rivet-start-plank' "$BRANDING_HOOK"
grep -Fq 'def update_dock_items(' "$DOCK_HELPER"
grep -Fq 'INSTALLER_ITEM = "Install-Rivet.dockitem"' "$DOCK_HELPER"
grep -Fq 'Welcome.dockitem' "$BRANDING_HOOK"
grep -Fq 'Software.dockitem' "$BRANDING_HOOK"
grep -Fq 'Launcher=file:///usr/share/applications/rivet-software.desktop' "$BRANDING_HOOK"
grep -Fq 'gnome-software-plugin-deb' "$PACKAGE_LIST"
grep -Fq 'gnome-software-plugin-flatpak' "$PACKAGE_LIST"
grep -Fq 'flatpak' "$PACKAGE_LIST"
grep -Fq 'Flathub' "$BRANDING_HOOK"
grep -Fq 'flathub.flatpakrepo' "$BRANDING_HOOK"
grep -Fq 'GPGKey=' "$BRANDING_HOOK"
grep -Fq 'Name=Rivet Software' "$BRANDING_HOOK"
grep -Fq 'Exec=gnome-software --mode=overview' "$BRANDING_HOOK"
grep -Fq 'Welcome to Rivet' "$WELCOME_CENTER_APP"
grep -Fq 'def is_live_session(' "$WELCOME_CENTER_APP"
grep -Fq 'if is_live_session():' "$WELCOME_CENTER_APP"
grep -Fq 'SETTINGS_GROUPS = (' "$WELCOME_CENTER_APP"
grep -Fq 'Gtk.SearchEntry()' "$WELCOME_CENTER_APP"
grep -Fq 'Gtk.StackSidebar()' "$WELCOME_CENTER_APP"
grep -Fq 'System settings' "$WELCOME_CENTER_APP"
grep -Fq 'Rivet Atmosphere' "$WELCOME_CENTER_APP"
grep -Fq 'Chip Fixs' "$WELCOME_CENTER_APP"
grep -Fq 'rivet-welcome-center' "$WELCOME_APP"
grep -Fq 'Software Store' "$WELCOME_CENTER_APP"
grep -Fq '("Software Store", "Discover and install desktop applications"' "$WELCOME_CENTER_APP"
grep -Fq 'OnlyShowIn=XFCE;' "$WELCOME_AUTOSTART"
grep -Fq 'Exec=/usr/bin/rivet-welcome --show-again' "$WELCOME_LAUNCHER"
grep -Fq 'NoDisplay=true' "$RIVET_INSTALLER_LAUNCHER"
grep -Fq 'Name=Welcome to Rivet' "$WELCOME_LAUNCHER"
grep -Fq 'Icon=rivet' "$WELCOME_LAUNCHER"
grep -Fq 'Welcome to Rivet Linux' "$WELCOME_APP"
grep -Fq 'def is_live_session(' "$WELCOME_APP"
grep -Fq 'if self.live_session:' "$WELCOME_APP"
grep -Fq 'Rivet is installed and ready.' "$WELCOME_APP"
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
grep -Fq 'PASSWORD_POLICY_HELPER="/usr/lib/rivet/configure-calamares-password-policy.py"' "$BRANDING_HOOK"
grep -Fq 'python3 "$PASSWORD_POLICY_HELPER" "$USERS_CONFIG"' "$BRANDING_HOOK"
grep -Fq 'PASSWORD_REQUIREMENTS = """passwordRequirements:' "$PASSWORD_POLICY_HELPER"
grep -Fq 'minLength: 1' "$PASSWORD_POLICY_HELPER"
grep -Fq 'maxLength: -1' "$PASSWORD_POLICY_HELPER"
grep -Fq 'allowWeakPasswords' "$PASSWORD_POLICY_HELPER"
grep -Fq 'configure-calamares-password-policy.py' .github/workflows/validate.yml
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
grep -Fq 'CHIP_FIXS_LOGO=' "$BRANDING_HOOK"
grep -Fq 'chmod 0755 /usr/bin/chip-fixs' "$BRANDING_HOOK"
grep -Fq 'cp "$CHIP_FIXS_LOGO" "$CHIP_FIXS_ICON"' "$BRANDING_HOOK"
grep -Fq 'Chip-Fixs.dockitem' "$BRANDING_HOOK"
grep -Fq 'Launcher=file:///usr/share/applications/chip-fixs.desktop' "$BRANDING_HOOK"
grep -Fq 'launch_app, ["chip-fixs"]' "$WELCOME_APP"
grep -Fq 'dmidecode' "$PACKAGE_LIST"
grep -Fq 'smartmontools' "$PACKAGE_LIST"
grep -Fq 'lm-sensors' "$PACKAGE_LIST"
grep -Fq 'mesa-utils' "$PACKAGE_LIST"

grep -Fq 'Exec=/usr/bin/rivet-start-plank' "$PLANK_AUTOSTART"
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
grep -Fq 'title: qsTr("Installing Rivet Linux")' "$BRANDING_SLIDESHOW"
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
