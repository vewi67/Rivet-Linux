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

## Verification

Repository validation checks the required assets, package dependencies, launchers, and Python syntax. The ISO still needs boot and first-login testing in a virtual machine before these features can be considered verified.
