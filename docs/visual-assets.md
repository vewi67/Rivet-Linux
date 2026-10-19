# Visual Assets

## Wallpapers

The four wallpaper files live in build/config/includes.chroot/usr/share/backgrounds/rivet/:

- rivet-waves.jpeg — waves wallpaper and default XFCE desktop background.
- rivet-factory.jpeg — factory wallpaper.
- rivet-chip.jpeg — Chip wallpaper.
- rivet-prism.jpeg — LightDM login background.

## Boot identity

The scripted Plymouth theme lives in `build/config/includes.chroot/usr/share/plymouth/themes/rivet/`. Its logo is staged at image-build time from the Rivet Calamares logo, preserving its original aspect ratio. The source theme starts with real status updates in a terminal-style panel; each incoming line slides in and fades up. The build configures initramfs-tools’ existing `_log_msg()` helper to forward the formatted early-boot messages through `plymouth update --status`, while Plymouth’s own status callbacks can display system status updates without inventing successful steps. As boot progresses, the log view transitions to the Rivet logo over eight build-generated blue/cyan smoke frames, then fades in **“Welcome to Rivet Linux”**. The live and installed kernel command lines use `systemd.show_status=1` alongside `quiet splash`. The status bridge is applied before `plymouth-set-default-theme -R rivet` rebuilds the initramfs; it adds no resident animation service and does not hold up startup with an artificial delay. Published ISO #101 still contains the previous splash: these changes are source-only until a new ISO is explicitly authorized and built. The line animation, smoke sequence, real status forwarding, and display-manager handoff still require runtime testing on BIOS and UEFI VMs.

## Installer identity

The Calamares logo, static branding descriptor (`branding.desc`), and slideshow (`show.qml`) live in build/config/includes.chroot/etc/calamares/branding/rivet/. A small image-time hook changes only the `branding` key in `/etc/calamares/settings.conf` from Debian to Rivet, preserving Debian's complete installer module sequence and module configuration. A separate validation hook checks the branding files without generating or rewriting them.

Rivet ships its own `rivet-installer.desktop` entry with the Rivet name and icon. It launches `/usr/bin/rivet-installer`, which captures output from Debian's packaged `/usr/bin/calamares-install-debian` helper without replacing its logic. The diagnostic helper checks the mapped top-level window's `WM_CLASS` (with a title fallback), so translated window titles do not cause false failures. Process detection reads `/proc/PID/exe` and `cmdline` rather than relying on the 15-character-truncated `comm` field. If no visible window appears, it shows a diagnostic dialog and only appends `/root/.cache/calamares/session.log` if the file was created or changed during that attempt, avoiding stale logs. The system includes `x11-utils` for the X11 window check. A missing GTK diagnostic dependency no longer prevents the underlying Debian installer launcher from being called. The underlying Debian helper preserves its display authorization, `pkexec`, and temporary `/etc/fstab` handling. The unbranded Debian menu entry remains hidden to avoid duplicate shortcuts.

## Chip mascot and welcome app

Five Chip PNG poses live in build/config/includes.chroot/usr/share/rivet/chip/. Live-build copies them to /usr/share/rivet/chip/.

The live-session welcome launcher is installed at /usr/bin/rivet-welcome. In a live session, it offers “Install Rivet”. On an installed system, the launcher hands off to the separate /usr/bin/rivet-welcome-center GTK application and does not show the live installer welcome screen. The installed center is guarded against running in a live session. It includes the Chip mascot, a welcome dashboard, a searchable System settings page, Rivet tools, and an About page. Settings cards open existing XFCE or Debian tools for themes, display, panels, window management and tweaks, workspaces, keyboard, mouse, power, accessibility, sound, network, Bluetooth, notifications, file associations, advanced XFCE properties, applications, packages and disks. Rivet Atmosphere and Chip Fixs are included as first-class tools. The current system settings page checks whether each command exists before launching it. The welcome launcher appears in the application menu as “Welcome to Rivet” and is also added to the Plank dock. Closing the installed welcome center records the existing per-user welcome marker, so it does not pop up on every login; the menu entry can reopen it with --show-again. The installer desktop entry is hidden from application menus. The Plank startup wrapper adds the installer shortcut only in live sessions and removes it from the installed-system dock while preserving other user dock items. Automated tests cover live-versus-installed detection, settings search and navigation, and live-only dock behavior; the UI smoke test opens the app under a virtual X display. The current source changes still require a fresh ISO and booted-system verification.

The Rivet logo is also installed into the hicolor icon theme for the welcome and installer launchers.

## Chip Fixs

Chip Fixs is installed as `/usr/bin/chip-fixs`, with its data-collection and diagnostic core at `/usr/lib/chip-fixs/core.py`. Its official logo is stored at `assets/chip-fixs/logo.png` and mirrored at `build/config/includes.chroot/usr/share/rivet/chip-fixs/logo.png`, which live-build copies into the system. During image configuration, the branding hook installs this image as `/usr/share/icons/hicolor/256x256/apps/chip-fixs.png` and refreshes the hicolor icon cache. The same `chip-fixs` icon name is used by the GTK window and desktop launcher, so the menu and Plank use the custom artwork too. Repository validation checks the PNG dimensions and ensures the source and staged copies are identical.

The application offers two main actions: **Fix System** runs bounded diagnostics and provides only a small allow-list of confirmed repair actions; **System Info** shows local hardware and system details by category. Advanced SMBIOS memory and SMART disk queries ask for administrator authorization. Diagnostics do not upload reports or automatically change files or packages.

## Rivet Atmosphere

Rivet Atmosphere gives the wallpaper collection a quiet, optional rhythm without adding a custom animation engine or a continuously polling process.

- New user profiles start in **ambient** mode with Rivet Waves as the default wallpaper.
- XFCE's native backdrop cycler selects among the four images in the Rivet wallpaper directory in random order, changing every 30 minutes.
- A small GTK control panel named **Rivet Atmosphere** is available from the welcome window, the Plank dock, and the application menu.
- Turning Atmosphere off stores a per-user static preference. Choosing a wallpaper outside the Rivet collection stops cycling for that desktop area without overwriting the chosen image.
- Choosing a Rivet wallpaper again resumes cycling when ambient mode is enabled.

The repository validator runs behavioral tests for the XFCE settings, static mode, and preservation of personal wallpapers. These tests do not render a real desktop; a booted ISO still needs visual verification before Atmosphere is considered fully verified.

## Verification

Repository validation checks the required assets, package dependencies, launchers, and Python syntax. The ISO still needs boot and first-login testing in a virtual machine before these features can be considered verified.
