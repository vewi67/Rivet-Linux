# Chip Fixs logo

The official artwork is stored as `assets/chip-fixs/logo.png`. The current image is a square 500 × 500 pixel PNG.

## Integration

The same image is staged at:

`build/config/includes.chroot/usr/share/rivet/chip-fixs/logo.png`

Live-build includes the staged copy in Rivet. The branding hook installs it into the hicolor icon theme at `/usr/share/icons/hicolor/256x256/apps/chip-fixs.png`. The GTK window, application menu, and Plank launcher all use the `chip-fixs` icon name.

Keep the source and staged files identical when replacing the artwork. Run `bash scripts/validate-repo.sh`; the repository validator checks that both files match and that the logo is a square PNG at least 256 × 256 pixels.

A transparent background is recommended for best appearance across dark and light themes.
