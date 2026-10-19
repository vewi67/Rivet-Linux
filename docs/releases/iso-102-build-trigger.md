# Rivet Linux ISO #102 build trigger

This marker file exists only on the one-time branch `rivet-iso102-authorized-once-20261019` to trigger the explicitly authorized Rivet Linux build #102 workflow.

- Requested on: 2026-10-19
- Release tag: `rivet-build-102`
- ISO filename: `Rivet-Linux.amd64.iso`
- Required gates: repository validation, Debian Trixie installer integration, and live-build configuration preflight

This file is a release-trigger record, not a runtime component. The build workflow verifies that the release tag is unused before building or publishing.