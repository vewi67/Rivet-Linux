#!/usr/bin/python3
"""Apply Rivet's permissive, non-empty Calamares password policy."""

import re
import sys
from pathlib import Path


PASSWORD_REQUIREMENTS = """passwordRequirements:
    minLength: 1
    maxLength: -1
    libpwquality:
        - minlen=0
        - minclass=0

"""


def configure(path: Path) -> None:
    """Allow any non-empty password and preserve surrounding comments and settings."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    active_blocks = [
        index
        for index, line in enumerate(lines)
        if re.fullmatch(r"passwordRequirements:[ \t]*(?:#.*)?(?:\r?\n)?", line)
    ]
    if len(active_blocks) != 1:
        raise ValueError(
            f"expected exactly one active passwordRequirements block in {path}; "
            f"found {len(active_blocks)}"
        )

    start = active_blocks[0]
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if not line.strip() or line[0].isspace():
            end += 1
            continue
        break

    updated = "".join(lines[:start]) + PASSWORD_REQUIREMENTS + "".join(lines[end:])

    for key in ("allowWeakPasswords", "allowWeakPasswordsDefault"):
        pattern = re.compile(
            rf"(?m)^{re.escape(key)}:[ \\t]*(?:true|false)[ \\t]*(?:#.*)?$"
        )
        matches = list(pattern.finditer(updated))
        if len(matches) > 1:
            raise ValueError(
                f"expected at most one active {key} boolean setting in {path}; "
                f"found {len(matches)}"
            )
        if matches:
            updated = pattern.sub(f"{key}: true", updated, count=1)
        else:
            # Debian's packaged users.conf may omit these optional keys.
            # Set them explicitly so the installer does not apply stricter defaults.
            updated = updated.rstrip() + f"\\n{key}: true\\n"

    path.write_text(updated, encoding="utf-8")
    print(f"Calamares password policy configured for {path}: any non-empty password is allowed.")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} /path/to/users.conf", file=sys.stderr)
        return 2
    try:
        configure(Path(sys.argv[1]))
    except (OSError, ValueError) as error:
        print(f"ERROR: could not configure Calamares password policy: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
