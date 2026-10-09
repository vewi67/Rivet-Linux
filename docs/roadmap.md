# Rivet Roadmap

The roadmap prioritizes a usable ISO quickly. Complexity comes only after the basic path works.

## Phase 0: Foundation

**Status: complete**

- [x] Create repository
- [x] Define name: Rivet
- [x] Define Debian 13 Trixie as the base
- [x] Record project philosophy
- [x] Record agent and contribution rules
- [x] Record initial architecture
- [x] Define amd64
- [x] Define XFCE + Xorg
- [x] Define LightDM, NetworkManager, and PipeWire
- [x] Define live-build
- [x] Define Calamares
- [x] Define initial application profile
- [x] Define first-ISO acceptance criteria

## Phase 1: First functional ISO

**Status: in progress**

Goal: produce a reproducible ISO that boots, starts XFCE, and can be installed in a VM.

- [x] Create the minimum live-build configuration
- [x] Define the initial package selection
- [x] Add Debian Calamares settings
- [x] Add repository validation
- [ ] Validate Debian repository configuration
- [ ] Build the first ISO
- [ ] Test boot in a VM
- [ ] Test XFCE
- [ ] Test networking
- [ ] Test audio
- [ ] Test Calamares
- [ ] Test installation
- [ ] Test first boot after installation
- [ ] Test package updates

## Phase 2: First Rivet experience

- [ ] Refine XFCE defaults
- [x] Add the Rivet visual identity
- [x] Add Chip mascot assets
- [x] Implement the first-login welcome window
- [ ] Test the welcome window in a built ISO
- [ ] Add small Rivet tools where real problems exist
- [ ] Improve user documentation
- [ ] Test on real hardware

## Phase 3: Custom tools

Create only tools that solve problems found during real use.

- [ ] Identify real problems
- [ ] Design small solutions
- [ ] Implement them
- [ ] Add tests
- [ ] Integrate them into the image

## Phase 4: Public pre-alpha

- [ ] Verify reproducibility
- [ ] Add minimum automated tests
- [ ] Document manual testing
- [ ] Validate installation
- [ ] Validate upgrades
- [ ] Document recovery paths
- [ ] Publish release notes

## Scope rule

A stage is not complete just because it works on the creator's machine.

It needs a reproducible path and a reasonable way to verify the result.
