# Scripts

The `scripts/` directory contains small, reproducible project automation.

Scripts should:

- have one clear responsibility;
- fail explicitly;
- avoid hidden state;
- document non-obvious behavior;
- be safe to run from any repository checkout.

Repository validation lives in `scripts/validate-repo.sh`.

The Chip Fixs core tests can be run with:

    python3 scripts/test-chip-fixs.py

They exercise parsers, disk enumeration safeguards, and the allow-list boundary without GTK, root access, or real hardware changes.

Production system tooling does not belong here unless the project explicitly decides that it does.
