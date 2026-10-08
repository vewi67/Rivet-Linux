# ISO Build

The `build/` directory contains the reproducible Tip ISO build.

## Current builder

Tip uses **Debian live-build** inside a Debian Trixie container in GitHub Actions.

The build configuration is versioned under:

```text
build/
├── build.sh
└── config/
    ├── package-lists/
    └── includes.chroot/
```

## Local build

Install `live-build` on a Debian-based environment, then run:

```bash
bash build/build.sh
```

The script intentionally does not delete the tracked configuration directory. Build state should be cleaned using live-build's own cleanup workflow when necessary.

## CI build

GitHub Actions builds the ISO inside `debian:trixie` and publishes the resulting hybrid ISO as an artifact.

A failed build is not considered a successful Tip build.

## Scope

This build produces a development/test image. It is not a release pipeline yet.
