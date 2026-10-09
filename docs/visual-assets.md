# Visual Assets

## Wallpapers

The four wallpaper files live in `build/config/includes.chroot/usr/share/backgrounds/rivet/`:

- `rivet-waves.jpeg` — waves wallpaper and default XFCE desktop background.
- `rivet-factory.jpeg` — factory wallpaper.
- `rivet-chip.jpeg` — Chip wallpaper.
- `rivet-prism.jpeg` — login background for LightDM.

## Installer logo

The Calamares logo is stored at `build/config/includes.chroot/etc/calamares/branding/rivet/rivet.logo.png`.

## Chip mascot

Five Chip PNG poses live in `build/config/includes.chroot/usr/share/rivet/chip/`. Live-build copies them to `/usr/share/rivet/chip/`.

The first-login welcome application is installed at `/usr/bin/rivet-welcome` and autostarts in XFCE through `/etc/xdg/autostart/rivet-welcome.desktop`. It displays a randomly selected Chip pose, introduces Rivet, and offers shortcuts to Thunar and XFCE settings. Dismissing the window records a marker in the user's home directory, so it does not appear on every login.

## Verification

The repository validation script checks the mascot files, welcome application, autostart entry, and required runtime packages. The ISO still needs boot and first-login testing in a virtual machine before this feature can be considered verified.
