# Rivet Linux

> **Your computer. Your rules.**

Rivet is a Debian-based Linux distribution built around one simple idea:

**YOUR COMPUTER IS YOURS. CHANGE WHAT YOU WANT.**

Rivet aims to be simple without being limiting. Everyday tasks should be easy to understand, while the user keeps real control over the system.

## Principles

- **Control:** important system decisions should not be hidden.
- **Simplicity:** common tasks should have obvious paths.
- **Freedom:** the system should not artificially lock down configuration.
- **Lightweight:** avoid unnecessary software, services, and layers.
- **Compatibility:** stay close to the Debian ecosystem and widely supported solutions.
- **Clarity:** prefer predictable behavior over unexplained automation.

## Project status

**Pre-alpha.**

The foundation and initial architecture are in place. The current work is focused on making the build reproducible, validating the configuration, and producing the first usable ISO.

## Current architecture

| Component | Choice |
|---|---|
| Base | Debian 13 Trixie |
| Architecture | amd64 |
| Desktop | XFCE 4.20 |
| Display server | Xorg |
| Display manager | LightDM |
| File manager | Thunar |
| Terminal | xfce4-terminal |
| Network | NetworkManager |
| Audio | PipeWire + WirePlumber |
| Init | systemd |
| Initramfs | initramfs-tools |
| Bootloader | GRUB |
| Default filesystem | ext4 |
| ISO builder | Debian live-build |
| Installer | Calamares |
| Package management | APT + dpkg |

## Repository layout

```text
.
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       └── build-iso.yml
├── build/
│   ├── README.md
│   ├── build.sh
│   └── config/
├── config/
├── docs/
│   ├── philosophy.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── decisions/
└── scripts/
    ├── README.md
    └── validate-repo.sh
```

## Development rule

> **Define before implementing. Keep stable components when they work. Do not add complexity just because it is possible.**

The project is built in small, verifiable steps. A working foundation comes before visual polish and custom tooling.

## First milestone

The first milestone is a bootable, usable, installable ISO that can:

1. boot in a virtual machine;
2. start XFCE;
3. provide working networking;
4. provide audio when the VM exposes it;
5. launch the basic applications;
6. start Calamares;
7. install to a virtual disk;
8. boot the installed system;
9. create a normal user;
10. update the installed packages.

This is a test image, not a final release.

## Why Rivet?

Rivet combines proven Debian components with a distinct identity and a straightforward, lightweight experience. The project focuses on making the system understandable and customizable without rebuilding reliable components unnecessarily.

---

See [docs/architecture.md](docs/architecture.md) for the technical design and [docs/roadmap.md](docs/roadmap.md) for the development plan.
