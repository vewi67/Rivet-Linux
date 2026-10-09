# ADR 0005: First Project Milestone

- **Status:** Accepted
- **Date:** 2026-10-07

## Goal

The first major Rivet milestone is:

> Build a bootable ISO that starts XFCE, allows the desktop to be tested, and can install to a virtual machine.

The first stage does not need every future Rivet tool.

## Acceptance criteria

The first functional ISO must:

1. boot in a VM;
2. start a graphical session;
3. recognize networking;
4. provide audio when the VM exposes it;
5. launch the basic applications;
6. start Calamares;
7. install to a virtual disk;
8. boot the installed system;
9. create a normal user;
10. update packages after installation.

## Out of scope

This milestone does not include:

- final theme;
- custom settings application;
- custom software center;
- multiple architectures;
- experimental features;
- aggressive optimization;
- complete branding.

## Rule

First make the computer boot, work, and install.

Then make it beautiful, distinctive, and Rivet.
