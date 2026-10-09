# Visual Assets

This document records the exact image locations for the planned Rivet visual identity integration.

## Wallpaper files

Upload these four wallpaper files to:

`build/config/includes.chroot/usr/share/backgrounds/rivet/`

Exact filenames (including extensions):

- `rivet-waves.jpeg` — waves wallpaper.
- `rivet-factory.jpeg` — factory wallpaper.
- `rivet-chip.jpeg` — chip wallpaper.
- `rivet-prism.jpeg` — prism wallpaper, intended for the LightDM login background.

Recommended wallpaper size: at least 1920 × 1080.

## Installer logo

Upload the logo to this directory:

`build/config/includes.chroot/etc/calamares/branding/rivet/`

Exact filename:

- `rivet.logo.png`

Recommended logo size: at least 256 × 256, with transparency if appropriate.

## Uploading through GitHub

1. Open the wallpaper directory: https://github.com/vewi67/Tip-Linux/tree/main/build/config/includes.chroot/usr/share/backgrounds/rivet
2. Click **Add file → Upload files**, select the four wallpaper files, and commit the changes.
3. Open the branding directory: https://github.com/vewi67/Tip-Linux/tree/main/build/config/includes.chroot/etc/calamares/branding/rivet
4. Click **Add file → Upload files**, select `rivet.logo.png`, and commit the changes.

Upload the original image files, not screenshots. Keep the names and extensions exactly as listed.

These directories are inside live-build's `includes.chroot/` tree, so their contents are copied into the built system image.

## Integration status and naming

- The directories are prepared, but XFCE's default wallpaper, LightDM's login background, and Calamares branding have **not** been configured yet.
- The repository and ISO metadata still use **Tip Linux**. The image filenames and the Rivet branding directory do not, by themselves, change the operating system's official name.
