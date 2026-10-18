#!/usr/bin/env python3
"""Regression tests for Rivet's Calamares password-policy helper."""

from pathlib import Path
import re
import subprocess
import sys
import tempfile


REPOSITORY = Path(__file__).resolve().parents[1]
HELPER = REPOSITORY / (
    "build/config/includes.chroot/usr/lib/rivet/configure-calamares-password-policy.py"
)


def run_helper(path: Path):
    return subprocess.run(
        [sys.executable, str(HELPER), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )


def main():
    assert HELPER.is_file(), f"Missing password-policy helper: {HELPER}"

    source = """---
defaultGroups:
  - sudo
sudoersGroup: sudo
passwordRequirements:
    minLength: 8
    maxLength: 64
    libpwquality:
        - minlen=8
        - minclass=3

# This explanatory documentation must survive configuration.
# passwordRequirements:
#     minLength: 12

allowWeakPasswords: false
allowWeakPasswordsDefault: false
user:
  shell: /bin/bash
"""
    with tempfile.TemporaryDirectory(prefix="rivet-password-policy-") as temporary:
        root = Path(temporary)
        users = root / "users.conf"
        users.write_text(source, encoding="utf-8")

        result = run_helper(users)
        assert result.returncode == 0, result.stderr
        configured = users.read_text(encoding="utf-8")

        requirements = re.search(
            r"(?ms)^passwordRequirements:\n(.*?)(?=^\n*#|^allowWeakPasswords:)",
            configured,
        )
        assert requirements is not None, "passwordRequirements block must remain present."
        block = requirements.group(1)
        assert re.search(r"(?m)^    minLength: 1$", block), "Any non-empty password must be allowed."
        assert re.search(r"(?m)^    maxLength: -1$", block), "No maximum password length should be imposed."
        assert "- minlen=0" in block and "- minclass=0" in block, (
            "libpwquality must not impose class or minimum-length requirements."
        )
        assert re.search(r"(?m)^allowWeakPasswords: true$", configured)
        assert re.search(r"(?m)^allowWeakPasswordsDefault: true$", configured)
        assert "# This explanatory documentation must survive configuration." in configured
        assert "#     minLength: 12" in configured

        result_again = run_helper(users)
        assert result_again.returncode == 0, result_again.stderr
        assert users.read_text(encoding="utf-8") == configured, (
            "Reapplying the helper should be idempotent."
        )

        missing_key = root / "missing-key.conf"
        invalid = source.replace("allowWeakPasswordsDefault: false\n", "")
        missing_key.write_text(invalid, encoding="utf-8")
        before = missing_key.read_text(encoding="utf-8")
        result = run_helper(missing_key)
        assert result.returncode != 0, "A missing required setting must fail visibly."
        assert missing_key.read_text(encoding="utf-8") == before, (
            "A failed configuration must not partially rewrite users.conf."
        )

    print("Calamares password-policy tests passed: permissive non-empty passwords, comment preservation, idempotence and safe failure.")


if __name__ == "__main__":
    main()
