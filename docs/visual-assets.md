# Visual Assets

This document records the exact image locations for the planned visual identity integration.

## Wallpaper files

Upload these PNG files to:

`build/config/includes.chroot/usr/share/backgrounds/rivet/`

Required filenames:

- `rivet-ocean.png` — intended default XFCE wallpaper.
- `rivet-factory.png` — alternate wallpaper.
- `rivet-chip.png` — alternate wallpaper.
- `rivet-prism.png` — intended LightDM login background.

Recommended wallpaper size: at least 1920 × 1080.

## Installer logo

Upload the logo PNG to:

`build/config/includes.chroot/etc/calamares/branding/rivet/logo.png`

Recommended logo size: at least 256 × 256, with transparency if appropriate.

## Important

- Preserve the exact filenames above. The planned configuration will refer to these paths.
- Upload the original image files, not screenshots of them.
- These directories are inside live-build's `includes.chroot/` tree, so their contents are copied into the built system image.
- This commit only prepares the directories and documents the destinations. It does not yet configure XFCE, LightDM, or Calamares.
- The repository is currently named **Tip Linux**. Do not change ISO metadata or the distribution's system identity until the project name is explicitly confirmed.
