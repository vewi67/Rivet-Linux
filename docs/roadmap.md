# Rivet Roadmap

The roadmap prioritizes a usable ISO quickly. Complexity comes only after the basic path works.

## Phase 0: Foundation

**Status: complete**

- [x] Create repository and define the Rivet name
- [x] Define Debian 13 Trixie as the base
- [x] Record project philosophy and contribution rules
- [x] Record the initial architecture
- [x] Define amd64 and XFCE + Xorg
- [x] Define LightDM, NetworkManager, and PipeWire
- [x] Define live-build and Calamares
- [x] Define the initial application profile
- [x] Define first-ISO acceptance criteria

## Phase 1: First functional ISO

**Status: in progress**

Goal: produce a reproducible ISO that boots, starts XFCE, and can be installed in a VM.

- [x] Create the minimum live-build configuration
- [x] Define the initial package selection
- [x] Add Debian Calamares settings
- [x] Add repository validation
- [x] Add ISO format and boot-metadata checks
- [x] Generate a SHA-256 checksum during builds
- [x] Build and publish #101, then publish #102 with ISO/checksum and BIOS/UEFI boot-catalog checks ([#102 release](https://github.com/vewi67/Rivet-Linux/releases/tag/rivet-build-102)).
- [x] Manually boot and install #100 in a VirtualBox VM; basic desktop/installer path succeeded.
- [x] Manually test #101; desktop and installer experience was much closer to the target.
- [x] Report the #102 runtime regression: the custom startup splash failed before the desktop handoff.
- [ ] Build and runtime-test a new, explicitly authorized image with the plain-text boot path.
- [ ] Test boot in a VM using UEFI
- [ ] Test legacy BIOS boot
- [ ] Test XFCE and default wallpaper
- [ ] Test networking
- [ ] Test audio
- [ ] Test Rivet branding in Calamares
- [ ] Test installation to a virtual disk
- [ ] Test first boot after installation
- [ ] Test package updates
- [x] Integrate GNOME Software with Debian package and Flatpak plugins
- [x] Configure Flathub for system-wide Flatpak app discovery
- [x] Add Rivet Software to the application menu, dock, and welcome settings hub
- [x] Add Whisker Menu with application search and session power actions to the top panel in source
- [x] Make the installer and live welcome dock/menu entries conditional on live-session detection in source
- [ ] Verify menu search/power actions, the minimal live dock, and live-only launcher cleanup in the next generated ISO.
- [ ] Verify the two-column Calamares wiki remains readable at common VM resolutions.
- [ ] Test application search, installation, removal, and updates in a built ISO

## Phase 2: First Rivet experience

- [x] Add the Rivet visual identity
- [x] Add Chip mascot assets
- [x] Implement the first-login welcome window
- [x] Add a way to reopen the welcome window
- [x] Add Rivet-branded application launchers
- [x] Add the installed-system Welcome to Rivet settings center with Chip
- [x] Separate the live installer welcome from the installed settings hub
- [x] Add automated checks for the welcome UI, launch mode and live-only installer dock item
- [x] Define the English-first default locale.
- [x] Remove the experimental graphical splash, its package/theme helpers and the installer stage after the #102 runtime regression.
- [x] Restore visible kernel/systemd startup messages in live and installed boot defaults.
- [ ] Verify plain-text boot, display-manager handoff, and first desktop login on BIOS and UEFI in the next authorized ISO.
- [x] Implement the Chip Fixs interface and diagnostic core prototype
- [x] Add local hardware inventory and explicitly authorized advanced reads
- [x] Add confirmation-gated recovery actions for selected network/audio service issues
- [ ] Test Chip Fixs and the welcome window in a built ISO
- [ ] Refine XFCE defaults after VM testing
- [ ] Improve user documentation
- [ ] Test on real hardware

## Phase 3: Custom tools

Create only tools that solve problems found during real use.

- [x] Identify a real need: system diagnosis and hardware inventory
- [x] Define and document the Chip Fixs scope and repair boundaries
- [x] Implement the first GTK interface and read-only diagnostic core
- [x] Add unit and safety-boundary tests
- [x] Add package selection, desktop menu, dock, and welcome-app integration
- [ ] Verify diagnostics and repairs in a generated ISO
- [ ] Exercise each available repair path in a disposable VM

## Phase 4: Public pre-alpha

- [ ] Verify reproducibility
- [ ] Document manual testing
- [ ] Validate installation and upgrades
- [ ] Document recovery paths
- [ ] Publish accurate release notes

## Scope rule

A stage is not complete just because it works on the creator's machine. It needs a reproducible path and a reasonable way to verify the result.
