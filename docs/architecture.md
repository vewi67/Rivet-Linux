# Rivet Architecture

## Status

The initial architecture is defined. The immediate focus is a reproducible first ISO, not a large feature set.

## Foundation

### System base

**Debian 13 Trixie** is the base of Rivet.

Rivet follows the selected Debian stable suite by name and uses its official updates.

## Initial profile

- Architecture: amd64
- Desktop: XFCE 4.20
- Display server: Xorg
- Display manager: LightDM
- File manager: Thunar
- Terminal: xfce4-terminal
- Network: NetworkManager
- Audio: PipeWire + WirePlumber
- Init: systemd
- Initramfs: initramfs-tools
- Bootloader: GRUB
- Default filesystem: ext4

## Build and installation

The system is built with **Debian live-build** and installed with **Calamares**.

The first image targets amd64 and should support UEFI. BIOS/legacy support is retained where the live-build flow supports it.

## Debian repositories

The build uses the following suites:

- trixie
- trixie-updates
- trixie-security

The enabled archive areas are:

- main
- contrib
- non-free
- non-free-firmware

Non-free firmware may be included when required for supported hardware.

## Initial software

The goal is a usable desktop without turning the ISO into an application warehouse.

Initial software includes:

- Firefox ESR
- LibreOffice Writer and Calc
- GParted
- Synaptic
- core XFCE utilities
- basic diagnostic and network tools

Steam, Wine, and large development toolchains are not installed by default.

## Architectural principles

### 1. Reuse before replacing

Keep a Debian component when it already solves the problem.

### 2. Clear layers

```text
Debian
  ↓
Configuration and component selection
  ↓
Rivet integration
  ↓
User experience
```

### 3. Fail visibly

Build tools and Rivet tooling must not hide failures.

### 4. Reproducibility

Build behavior must be versioned and reproducible.

### 5. Simplicity first

When a simple, proven solution solves the problem, it is the default.

## Explicitly out of scope for now

Do not implement:

- a custom package manager;
- a custom installer;
- a custom init system;
- a custom kernel;
- a custom desktop environment;
- unowned collections of scripts;
- aggressive optimizations before measuring.

## Next step

Turn the current architecture into a **validated live-build configuration**, then build and test it in a VM.

The ISO is a test artifact, not a final release.
