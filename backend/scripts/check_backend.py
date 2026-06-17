"""Run backend checks without requiring optional developer tooling."""

from __future__ import annotations

import compileall
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def configure_test_environment() -> None:
    os.environ.setdefault("DEBUG", "true")
    os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("SECRET_KEY", "test-secret")
    sys.path.insert(0, str(ROOT))


def run_compile_check() -> bool:
    return compileall.compile_dir(
        str(ROOT / "app"),
        quiet=1,
        force=True,
    )


def run_tests() -> unittest.result.TestResult:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    return unittest.TextTestRunner(verbosity=2).run(suite)


def main() -> int:
    configure_test_environment()

    if not run_compile_check():
        return 1

    result = run_tests()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
