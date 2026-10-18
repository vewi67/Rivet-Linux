# Visual Assets

## Wallpapers

The four wallpaper files live in build/config/includes.chroot/usr/share/backgrounds/rivet/:

- rivet-waves.jpeg — waves wallpaper and default XFCE desktop background.
- rivet-factory.jpeg — factory wallpaper.
- rivet-chip.jpeg — Chip wallpaper.
- rivet-prism.jpeg — LightDM login background.

## Installer identity

The Calamares logo, static branding descriptor (`branding.desc`), and slideshow (`show.qml`) live in build/config/includes.chroot/etc/calamares/branding/rivet/. A small image-time hook changes only the `branding` key in `/etc/calamares/settings.conf` from Debian to Rivet, preserving Debian's complete installer module sequence and module configuration. A separate validation hook checks the branding files without generating or rewriting them.

Rivet ships its own `rivet-installer.desktop` entry with the Rivet name and icon. It launches `/usr/bin/rivet-installer`, which captures output from Debian's packaged `/usr/bin/calamares-install-debian` helper without replacing its logic. The diagnostic helper checks the mapped top-level window's `WM_CLASS` (with a title fallback), so translated window titles do not cause false failures. Process detection reads `/proc/PID/exe` and `cmdline` rather than relying on the 15-character-truncated `comm` field. If no visible window appears, it shows a diagnostic dialog and only appends `/root/.cache/calamares/session.log` if the file was created or changed during that attempt, avoiding stale logs. The system includes `x11-utils` for the X11 window check. A missing GTK diagnostic dependency no longer prevents the underlying Debian installer launcher from being called. The underlying Debian helper preserves its display authorization, `pkexec`, and temporary `/etc/fstab` handling. The unbranded Debian menu entry remains hidden to avoid duplicate shortcuts.

## Chip mascot and welcome app

Five Chip PNG poses live in build/config/includes.chroot/usr/share/rivet/chip/. Live-build copies them to /usr/share/rivet/chip/.

The welcome app is installed at /usr/bin/rivet-welcome. It opens automatically in XFCE for a new user, introduces Rivet, and offers shortcuts to Thunar and XFCE settings. Choosing “Let's go” records a marker in the user's home directory, so it does not appear on every login. The “Welcome to Rivet Linux” application-menu entry can reopen it with --show-again.

The Rivet logo is also installed into the hicolor icon theme for the welcome and installer launchers.

## Chip Fixs

Chip Fixs is installed as `/usr/bin/chip-fixs`, with its data-collection and diagnostic core at `/usr/lib/chip-fixs/core.py`. Its menu launcher is `chip-fixs.desktop`, and the hicolor icon is created from a Chip mascot PNG during image configuration. The launcher is available from the application menu, the Plank dock, and the welcome window.

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
