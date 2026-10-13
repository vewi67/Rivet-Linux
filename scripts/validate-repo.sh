#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/rivet-validate.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

PACKAGE_LIST="build/config/package-lists/rivet.list.chroot"
BRANDING_HOOK="build/config/hooks/normal/0100-configure-rivet-branding.hook.chroot"
SLIDESHOW_HOOK="build/config/hooks/normal/0900-configure-rivet-calamares-slideshow.hook.chroot"
SECURE_LOG_HOOK="build/config/hooks/normal/0200-secure-rivet-installer-logging.hook.chroot"
CHIP_DIR="build/config/includes.chroot/usr/share/rivet/chip"
WELCOME_APP="build/config/includes.chroot/usr/bin/rivet-welcome"
WELCOME_AUTOSTART="build/config/includes.chroot/etc/xdg/autostart/rivet-welcome.desktop"
WELCOME_LAUNCHER="build/config/includes.chroot/usr/share/applications/rivet-welcome.desktop"
PLANK_AUTOSTART="build/config/includes.chroot/etc/xdg/autostart/rivet-plank.desktop"

required_files=(
  README.md AGENTS.md CONTRIBUTING.md
  build/README.md build/build.sh
  "$BRANDING_HOOK" "$SLIDESHOW_HOOK" "$SECURE_LOG_HOOK" "$PACKAGE_LIST" "$WELCOME_APP"
  "$WELCOME_AUTOSTART" "$WELCOME_LAUNCHER" "$PLANK_AUTOSTART"
  "$CHIP_DIR/README.md"
  .github/workflows/build-iso.yml .github/workflows/build-pr.yml .github/workflows/validate.yml
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
grep -Fq 'SLIDESHOW_HOOK="config/hooks/normal/0900-configure-rivet-calamares-slideshow.hook.chroot"' build/build.sh
grep -Fq 'chmod 0755 {} +' build/build.sh
grep -Fq 'SECURE_LOG_HOOK="config/hooks/normal/0200-secure-rivet-installer-logging.hook.chroot"' build/build.sh
grep -Fq '[[ -s "$SECURE_LOG_HOOK" ]]' build/build.sh

bash -n build/build.sh
sh -n "$BRANDING_HOOK"
sh -n "$SLIDESHOW_HOOK"
sh -n "$SECURE_LOG_HOOK"
bash -n scripts/validate-repo.sh

# Shell scripts embedded in the branding hook are heredoc contents, so parsing
# the hook itself does not validate their syntax. Extract and check each one.
extract_heredoc() {
  local source="$1"
  local marker="$2"
  local end_marker="$3"
  local destination="$4"

  awk -v marker="$marker" -v end_marker="$end_marker" '
    !capturing && index($0, marker) { capturing = 1; found = 1; next }
    capturing && $0 == end_marker { complete = 1; exit }
    capturing { print }
    END {
      if (!found || !complete) {
        exit 1
      }
    }
  ' "$source" > "$destination" || {
    echo "ERROR: failed to extract embedded script '$marker' from $source." >&2
    exit 1
  }

  [[ -s "$destination" ]] || {
    echo "ERROR: embedded script '$marker' is empty." >&2
    exit 1
  }
}

extract_heredoc "$BRANDING_HOOK" "cat > /usr/local/bin/rivet-set-wallpaper <<'EOF'" EOF "$TMP_DIR/wallpaper.sh"
extract_heredoc "$BRANDING_HOOK" "cat > /usr/local/bin/rivet-disable-xfce-panel <<'EOF'" EOF "$TMP_DIR/disable-panel.sh"
extract_heredoc "$BRANDING_HOOK" "cat > \"\$POLKIT_SETUP\" <<'EOF'" EOF "$TMP_DIR/polkit-setup.sh"
extract_heredoc "$BRANDING_HOOK" "cat > /usr/local/bin/rivet-installer <<'EOF'" EOF "$TMP_DIR/installer.sh"
extract_heredoc "$BRANDING_HOOK" "cat > /usr/local/libexec/rivet-installer-root <<'EOF'" EOF "$TMP_DIR/installer-root.sh"

for generated_script in "$TMP_DIR"/*.sh; do
  sh -n "$generated_script"
done

# Also parse the inline Python dialog created by the installer wrapper.
extract_heredoc "$TMP_DIR/installer.sh" "/usr/bin/python3 - <<'PY'" PY "$TMP_DIR/installer-dialog.py"
python3 -c 'import ast, pathlib, sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))' "$TMP_DIR/installer-dialog.py"

# Verify the source helper still matches the hardening hook's expected input,
# then syntax-check the resulting helper without executing privileged actions.
grep -Fq 'LOG_FILE="/tmp/rivet-installer.log"' "$TMP_DIR/installer-root.sh"
sed 's|LOG_FILE="/tmp/rivet-installer.log"|LOG_FILE="/run/rivet-installer-root.log"|' "$TMP_DIR/installer-root.sh" > "$TMP_DIR/installer-root-relocated.sh"
awk '
  { print }
  $0 == "LOG_FILE=\"/run/rivet-installer-root.log\"" {
    print "install -o root -g root -m 0644 /dev/null \"$LOG_FILE\""
  }
' "$TMP_DIR/installer-root-relocated.sh" > "$TMP_DIR/installer-root-hardened.sh"
sh -n "$TMP_DIR/installer-root-hardened.sh"
grep -Fq 'LOG_FILE="/run/rivet-installer-root.log"' "$TMP_DIR/installer-root-hardened.sh"
grep -Fq 'install -o root -g root -m 0644 /dev/null "$LOG_FILE"' "$TMP_DIR/installer-root-hardened.sh"

echo "==> Checking Python syntax..."
PYTHONPYCACHEPREFIX="$TMP_DIR/pycache" python3 -m py_compile "$WELCOME_APP"

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
  xfce4 xfce4-terminal thunar plank lightdm lightdm-gtk-greeter xserver-xorg \
  network-manager network-manager-gnome pipewire pipewire-pulse wireplumber \
  mate-polkit polkitd pkexec x11-xserver-utils firefox-esr calamares \
  calamares-settings-debian sudo python3-gi gir1.2-gtk-3.0; do
  require_package "$package"
done

echo "==> Checking build and branding identity..."
for setting in \
  '--distribution trixie' \
  '--architectures amd64' \
  '--binary-images iso-hybrid' \
  '--iso-application "Rivet Linux"' \
  '--iso-publisher "Rivet Linux Project"' \
  '--iso-volume "RIVET_LINUX"'; do
  grep -Fq -- "$setting" build/build.sh || {
    echo "ERROR: build identity setting missing: $setting" >&2
    exit 1
  }
done
grep -Fq 'productName: Rivet Linux' "$BRANDING_HOOK"
grep -Fq 'shortProductName: Rivet' "$BRANDING_HOOK"
grep -Fq 'bootloaderEntryName: Rivet Linux' "$BRANDING_HOOK"
grep -Fq 'name: Build Rivet ISO' .github/workflows/build-iso.yml
grep -Fq "if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/fix/rivet-installer-display-env'" .github/workflows/build-iso.yml
grep -Fq '      - fix/rivet-installer-display-env' .github/workflows/build-iso.yml
grep -Fq 'name: Publish development ISO' .github/workflows/build-iso.yml
grep -Fq 'tag_name: rivet-build-' .github/workflows/build-iso.yml
grep -Fq 'name: "Rivet Linux build #${{ github.run_number }}"' .github/workflows/build-iso.yml
grep -Fq 'name: Validate Rivet ISO on PR' .github/workflows/build-pr.yml
grep -Fq 'name: Build and validate ISO (no upload)' .github/workflows/build-pr.yml
grep -Fq 'permissions:' .github/workflows/build-pr.yml
grep -Fq 'contents: read' .github/workflows/build-pr.yml
if grep -Fq 'upload-artifact' .github/workflows/build-pr.yml || grep -Fq 'download-artifact' .github/workflows/build-iso.yml; then
  echo "ERROR: ISO workflow must not depend on temporary artifact storage." >&2
  exit 1
fi
grep -Fq 'name: Validate Rivet' .github/workflows/validate.yml

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
grep -Fq 'rivet-installer' "$WELCOME_APP"

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
grep -Fq 'workspace0' "$BRANDING_HOOK"
grep -Fq 'last-image' "$BRANDING_HOOK"
grep -Fq 'rivet-set-wallpaper' "$BRANDING_HOOK"
grep -Fq 'rivet-disable-xfce-panel' "$BRANDING_HOOK"
grep -Fq 'xfce4-panel.xml' "$BRANDING_HOOK"
grep -Fq 'rivet-live-polkit.service' "$BRANDING_HOOK"
grep -Fq 'polkit-1/rules.d/50-rivet-live.rules' "$BRANDING_HOOK"
grep -Fq 'install -d -m 0755 /etc/polkit-1/rules.d' "$BRANDING_HOOK"
grep -Fq 'cat > /etc/polkit-1/rules.d/50-rivet-live.rules' "$BRANDING_HOOK"
grep -Fq 'rivet-installer-root' "$BRANDING_HOOK"
grep -Fq 'rivet-installer' "$BRANDING_HOOK"
# pkexec filters GUI environment variables, so the launcher must pass the
# display/authentication details and the privileged helper must restore them.
grep -Fq 'rivet-installer-root "$DISPLAY" "${XAUTHORITY:-}"' "$BRANDING_HOOK"
grep -Fq 'export DISPLAY="$DISPLAY_VALUE"' "$BRANDING_HOOK"
grep -Fq 'export XAUTHORITY="$XAUTHORITY_VALUE"' "$BRANDING_HOOK"
grep -Fq '/run/rivet-installer-root.log' "$BRANDING_HOOK"
grep -Fq 'export QT_DEBUG_PLUGINS=1' "$BRANDING_HOOK"
grep -Fq '/usr/bin/calamares -D8' "$BRANDING_HOOK"
grep -Fq 'Calamares session log' "$BRANDING_HOOK"
grep -Fq 'Relevant Calamares diagnostics' "$BRANDING_HOOK"
grep -Fq 'last 25 lines' "$BRANDING_HOOK"
grep -Fq 'LOG_FILE="/tmp/rivet-installer.log"' "$SECURE_LOG_HOOK"
grep -Fq 'LOG_FILE="/run/rivet-installer-root.log"' "$SECURE_LOG_HOOK"
grep -Fq 'install -o root -g root -m 0644 /dev/null "$LOG_FILE"' "$SECURE_LOG_HOOK"
grep -Fq 'RIVET_WALLPAPER_DIR="/usr/share/backgrounds/rivet"' "$BRANDING_HOOK"
grep -Fq 'rivet-waves.jpeg' "$BRANDING_HOOK"
grep -Fq 'branding: rivet' "$BRANDING_HOOK"
grep -Fq 'slideshow: "show.qml"' "$SLIDESHOW_HOOK"
grep -Fq 'slideshowAPI: 2' "$SLIDESHOW_HOOK"
grep -Fq 'Presentation {' "$SLIDESHOW_HOOK"
grep -Fq 'centeredText: qsTr("Installing Rivet Linux")' "$SLIDESHOW_HOOK"
grep -Fq 'calamares-install-debian' "$BRANDING_HOOK"
grep -Fq 'Exec=/usr/local/bin/rivet-installer' "$BRANDING_HOOK"
grep -Fq 'Icon=rivet' "$BRANDING_HOOK"

echo "==> Checking documentation language..."
if grep -RniE '(^|[[:space:]])(para|uma|das|dos|não|aqui|deve|somente|pacotes|instalar|teste|experiência|configuração|usuário)([[:space:]]|$)' \
  README.md AGENTS.md CONTRIBUTING.md docs build/README.md build/config config scripts .github/pull_request_template.md \
  --include='*.md' --include='*.yml' --include='*.yaml' --include='*.sh' --exclude-dir='.git' \
  >$TMP_DIR/portuguese-check.txt 2>/dev/null; then
  echo "ERROR: possible Portuguese text found in project documentation:" >&2
  cat $TMP_DIR/portuguese-check.txt >&2
  exit 1
fi

echo "==> Repository validation passed."
