# ADR 0007: Chip Fixs System Diagnostics and Hardware Inventory

- **Status:** Accepted
- **Date:** 2026-10-18

## Context

Rivet already has a working base on Debian, an XFCE desktop, Calamares branding, Rivet Atmosphere, and the Chip welcome application. The remaining original desktop utility should solve a practical problem rather than add another decorative setting.

Users often need to understand what hardware their computer has or identify common system problems without opening several tools or interpreting unrelated command output.

## Decision

Create **Chip Fixs**, a Rivet-owned GTK 3 application written in Python and integrated with the existing desktop.

The main window presents two actions:

- **Fix System:** run a local diagnostic pass and explain confirmed results.
- **System Info:** display a categorized inventory of the system and hardware detectable through the kernel, sysfs, and established Debian utilities.

System information covers the operating system, kernel, architecture, firmware and motherboard where exposed, CPU, memory and swap, graphics and display resolutions, disks and filesystems, interfaces and network state, audio devices, PCI and USB devices, batteries, sensors, failed system services, package state, and clock status. Advanced RAM inventory and SMART health queries require an explicit action and administrative authorization.

## Repair boundaries

Chip Fixs must not claim it can fix every possible bug. It reports what it can check and distinguishes confirmed results from unavailable data.

Diagnostics are read-only. The first implementation may offer only specific, allow-listed repairs:
- Restart the current user's PipeWire/WirePlumber services after confirmation.
- Restart NetworkManager only after confirmation and a separate administrative authorization prompt.

It must not delete user files, kill arbitrary applications, rewrite package sources, automatically install or remove packages, run arbitrary shell commands, disable security tools, or send reports to a remote service. Package problems receive a diagnostic explanation and guidance rather than an automatic package transaction.

## Implementation

- Keep the GTK interface separate from a Python core module so the core can be tested without a desktop session.
- Reuse Debian utilities such as `lscpu`, `lspci`, `lsusb`, `lsblk`, `dmidecode`, `smartctl`, `sensors`, NetworkManager, and systemd instead of reimplementing hardware drivers.
- All subprocesses use argument arrays and bounded timeouts, never a shell command assembled from user input.
- Reports stay local. Saving or copying a report requires an explicit user action, and the interface warns that hardware/network data should be reviewed before sharing.
- Install the application through a desktop entry, the Plank dock, and the Chip welcome window.
- Add tests to repository validation and the Debian Trixie package-selection check.

## Acceptance criteria

1. Core parser and safety tests pass without GTK, root access, or real hardware changes.
2. The app launches in an XFCE session and its two main actions work.
3. Hardware fields show useful information or explain when the system cannot expose it; missing sensors are not treated as proof of hardware failure.
4. Diagnostics finish without freezing the interface and show their results clearly.
5. Repair actions are narrow, explained, confirmed, and never run from arbitrary report text.
6. No report is uploaded automatically.
7. The packaged app is tested in a freshly built Rivet ISO before this feature is considered complete.

## Consequences

Chip Fixs becomes Rivet's primary original system utility. It adds a few small, established diagnostic packages to the image, but does not introduce a daemon, a background service, a custom package manager, or a separate hardware-detection framework.
