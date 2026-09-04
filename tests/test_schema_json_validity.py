"""
Every committed ``schema/schemas/*-schema.json`` file MUST be loadable JSON.

Regression test for fix-01: ``ModelContextProtocolTypes-schema.json`` carried a
trailing comma that made it fail ``json.load``, silently breaking any tooling
(codegen, editors, CI) that parses schemas strictly. This walks every committed
schema file, using only the stdlib ``json`` module, and reports the offending
path(s) on failure so a future regression is caught immediately rather than
discovered downstream in codegen output.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_ROOT = REPO_ROOT / "schema" / "schemas"


def _all_schema_files() -> list[Path]:
    return sorted(SCHEMA_ROOT.rglob("*-schema.json"))


def test_schema_root_exists() -> None:
    assert SCHEMA_ROOT.is_dir(), f"expected schema directory at {SCHEMA_ROOT}"


def test_all_schema_files_are_valid_json() -> None:
    schema_files = _all_schema_files()
    assert schema_files, f"no *-schema.json files found under {SCHEMA_ROOT}"

    failures: list[str] = []
    for schema_file in schema_files:
        try:
            with schema_file.open(encoding="utf-8") as handle:
                json.load(handle)
        except json.JSONDecodeError as exc:
            failures.append(f"{schema_file.relative_to(REPO_ROOT)}: {exc}")

    assert not failures, "invalid JSON in schema file(s):\n" + "\n".join(failures)
