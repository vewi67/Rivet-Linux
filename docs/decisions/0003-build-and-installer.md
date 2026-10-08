# ADR 0003: live-build and Calamares

- **Status:** Accepted
- **Date:** 2026-10-07

## Context

The immediate goal is to reach a bootable and installable system quickly, without creating a custom build chain before the first ISO exists.

## Decision

### Build

Use Debian **live-build** to build the image.

### Installation

Use **Calamares** as the graphical installer.

### Boot

The first image targets amd64 and supports UEFI, while retaining BIOS/legacy boot where the live-build flow supports it.

### Repositories

The image uses Debian suites explicitly by name:

- trixie
- trixie-updates
- trixie-security

The enabled archive areas are main, contrib, non-free, and non-free-firmware.

## Why not write our own installer?

Calamares already provides a graphical installation framework suitable for Debian-based systems. Tip should customize the experience and configuration instead of rebuilding partitioning, user creation, and system installation from scratch.

## Why not create our own build system?

live-build already solves the problem of building Debian-based Live systems. Starting with it reduces custom code and accelerates the first ISO.

## Rule

Replacing live-build or Calamares later requires a concrete problem that cannot reasonably be solved through the existing configuration.
