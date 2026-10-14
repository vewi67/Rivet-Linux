# Visual Assets

## Wallpapers

The four wallpaper files live in build/config/includes.chroot/usr/share/backgrounds/rivet/:

- rivet-waves.jpeg — waves wallpaper and default XFCE desktop background.
- rivet-factory.jpeg — factory wallpaper.
- rivet-chip.jpeg — Chip wallpaper.
- rivet-prism.jpeg — LightDM login background.

## Installer identity

The Calamares logo and branding descriptor live in build/config/includes.chroot/etc/calamares/branding/rivet/. The image-time hook switches /etc/calamares/settings.conf from Debian branding to Rivet while preserving Debian's module sequence.

The image-time hook changes the visible name, comment, and icon while keeping `/usr/bin/calamares-install-debian` as both `Exec` and `TryExec`. This preserves Debian's launcher logic for X11 access, `pkexec`, and the temporary `/etc/fstab` safeguard. Do not route the desktop entry through a second custom `pkexec` wrapper: `pkexec` normally sanitizes `DISPLAY` and `XAUTHORITY`, which can prevent a privileged Qt GUI from opening.

## Chip mascot and welcome app

Five Chip PNG poses live in build/config/includes.chroot/usr/share/rivet/chip/. Live-build copies them to /usr/share/rivet/chip/.

The welcome app is installed at /usr/bin/rivet-welcome. It opens automatically in XFCE for a new user, introduces Rivet, and offers shortcuts to Thunar and XFCE settings. Choosing “Let's go” records a marker in the user's home directory, so it does not appear on every login. The “Welcome to Rivet Linux” application-menu entry can reopen it with --show-again.

The Rivet logo is also installed into the hicolor icon theme for the welcome and installer launchers.

## Verification

Repository validation checks the required assets, package dependencies, launchers, and Python syntax. The ISO still needs boot and first-login testing in a virtual machine before these features can be considered verified.
