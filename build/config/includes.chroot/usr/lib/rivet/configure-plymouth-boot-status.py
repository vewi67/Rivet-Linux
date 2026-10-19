#!/usr/bin/env python3
"""Forward genuine initramfs-tools log messages to Rivet's Plymouth theme.

The patch is deliberately small and idempotent: it instruments initramfs-tools'
existing _log_msg() helper instead of replacing the packaged file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

BEGIN = "# RIVET_PLYMOUTH_STATUS_BRIDGE_BEGIN"
END = "# RIVET_PLYMOUTH_STATUS_BRIDGE_END"
BRIDGE = """    # RIVET_PLYMOUTH_STATUS_BRIDGE_BEGIN
    # Mirror the same formatted message to the active splash, even when quiet
    # suppresses the normal console output. A missing daemon is non-fatal.
    if [ -x /bin/plymouth ]; then
        _rivet_status="$(printf "$@" 2>/dev/null | tr '\\n' ' ' | sed 's/[[:space:]]*$//')"
        if [ -n "$_rivet_status" ]; then
            /bin/plymouth update --status="$_rivet_status" >/dev/null 2>&1 || true
        fi
    fi
    # RIVET_PLYMOUTH_STATUS_BRIDGE_END
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} /path/to/initramfs-tools/scripts/functions", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: initramfs-tools functions file not found: {path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8")
    if BEGIN in content or END in content:
        if BEGIN in content and END in content and content.index(BEGIN) < content.index(END):
            print("Rivet Plymouth status bridge already configured.")
            return 0
        print("ERROR: incomplete existing Rivet Plymouth status bridge markers.", file=sys.stderr)
        return 1

    match = re.search(r"(?m)^_log_msg\(\)[ \t]*\r?\n\{\r?\n", content)
    if match is None:
        print("ERROR: could not locate the initramfs-tools _log_msg() function safely.", file=sys.stderr)
        return 1

    updated = content[:match.end()] + BRIDGE + content[match.end():]
    path.write_text(updated, encoding="utf-8")
    print("Configured initramfs-tools to forward genuine boot log messages to Plymouth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
