"""Noxfile - Unified development interface.

Usage:
    nox                    # Run all sessions
    nox -l                # List all sessions
    nox -s test           # Run specific session
    nox -s lint           # Lint only
    nox -s test -- tests/integrations/test_google_sheets.py  # Specific test

Sessions:
    test        - Run all tests with pytest
    test-fast   - Run tests without coverage (faster)
    lint        - Run ruff check
    format      - Format code with ruff
    typecheck   - Run mypy type checking
    docs        - Build documentation with mkdocs
    docs-serve  - Serve documentation locally
    security    - Run gitleaks secret scanning
    spell       - Run codespell spell checking
    all         - Run all quality checks (lint, typecheck, test, spell)
"""

import os
import shutil
from pathlib import Path

import nox

PYTHON_VERSIONS = ["3.11", "3.12"]
DEFAULT_PYTHON = "3.12"

nox.options.sessions = ["all"]


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run pytest with coverage."""
    session.install(".[dev]")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "--cov-fail-under=70",
        *session.posargs,
    )


@nox.session(python=PYTHON_VERSIONS)
def test_fast(session: nox.Session) -> None:
    """Run pytest without coverage (faster)."""
    session.install(".[dev]")
    session.run("pytest", "-v", "--tb=short", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Run ruff check for linting."""
    session.install("ruff")
    session.run("ruff", "check", "src/", "tests/", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def format_code(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "format", "src/", "tests/", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run mypy type checking."""
    session.install(".[dev]")
    session.run("mypy", "src/", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """Build documentation with mkdocs."""
    session.install("mkdocs-material[imaging]")
    session.run("mkdocs", "build", "--strict", "--site-dir", "site", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def docs_serve(session: nox.Session) -> None:
    """Serve documentation locally."""
    session.install("mkdocs-material[imaging]")
    session.run("mkdocs", "serve", "--dev-addr", "localhost:8000", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def security(session: nox.Session) -> None:
    """Run gitleaks for secret scanning."""
    session.install("gitleaks")
    session.run("gitleaks", "detect", "--source", ".", "--config", ".gitleaks.toml", "-v")


@nox.session(python=DEFAULT_PYTHON)
def spell(session: nox.Session) -> None:
    """Run codespell spell checking."""
    session.install("codespell")
    session.run(
        "codespell",
        "--ignore-words-list=crate,nd,te,als,ot,ro,hist,ser",
        "--skip=*.pyc,*.svg,*.lock,.venv,venv,dist,build,htmlcov,.mypy_cache",
        "src/",
        "tests/",
        "docs/",
        "examples/",
        *session.posargs,
    )


@nox.session(python=DEFAULT_PYTHON)
def all_checks(session: nox.Session) -> None:
    """Run all quality checks: lint, typecheck, test, spell."""
    session.install(".[dev]", "ruff", "codespell", "gitleaks")

    print("\n" + "=" * 60)
    print("Running all quality checks...")
    print("=" * 60)

    # 1. Spell check
    print("\n[1/5] Running codespell...")
    session.run(
        "codespell",
        "--ignore-words-list=crate,nd,te,als,ot,ro,hist,ser",
        "--skip=*.pyc,*.svg,*.lock,.venv,venv,dist,build,htmlcov,.mypy_cache",
        "src/",
        "tests/",
        "docs/",
        "examples/",
    )

    # 2. Lint
    print("\n[2/5] Running ruff check...")
    session.run("ruff", "check", "src/", "tests/")

    # 3. Format check
    print("\n[3/5] Checking code format...")
    session.run("ruff", "format", "--check", "src/", "tests/")

    # 4. Type check
    print("\n[4/5] Running mypy type check...")
    session.run("mypy", "src/")

    # 5. Test
    print("\n[5/5] Running pytest...")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-fail-under=70",
        "tests/",
    )

    print("\n" + "=" * 60)
    print("All checks passed!")
    print("=" * 60)


@nox.session(python=DEFAULT_PYTHON)
def clean(session: nox.Session) -> None:
    """Clean up build artifacts."""
    dirs_to_remove = [
        "build",
        "dist",
        "*.egg-info",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "site",
        ".nox",
    ]

    for pattern in dirs_to_remove:
        if "*" in pattern:
            for path in Path(".").glob(pattern):
                if path.is_dir():
                    print(f"Removing {path}/")
                    shutil.rmtree(path)
                elif path.is_file():
                    print(f"Removing {path}")
                    path.unlink()
        else:
            path = Path(pattern)
            if path.exists():
                if path.is_dir():
                    print(f"Removing {path}/")
                    shutil.rmtree(path)
                else:
                    print(f"Removing {path}")
                    path.unlink()

    print("Cleanup complete!")


@nox.session(python=DEFAULT_PYTHON)
def pre_commit(session: nox.Session) -> None:
    """Run pre-commit hooks on all files."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session(python=DEFAULT_PYTHON)
def install_hooks(session: nox.Session) -> None:
    """Install pre-commit hooks."""
    session.install("pre-commit")
    session.run("pre-commit", "install")
    print("Pre-commit hooks installed!")


@nox.session(python=DEFAULT_PYTHON)
def ci(session: nox.Session) -> None:
    """Run CI pipeline (same as GitHub Actions)."""
    session.install(".[dev]", "ruff", "codespell")

    print("\n" + "=" * 60)
    print("Running CI pipeline...")
    print("=" * 60)

    # Lint
    print("\n[1/4] Linting...")
    session.run("ruff", "check", "src/", "tests/")

    # Format
    print("\n[2/4] Checking format...")
    session.run("ruff", "format", "--check", "src/", "tests/")

    # Type check
    print("\n[3/4] Type checking...")
    session.run("mypy", "src/")

    # Test
    print("\n[4/4] Testing...")
    session.run("pytest", "--cov=src", "tests/")

    print("\n" + "=" * 60)
    print("CI pipeline passed!")
    print("=" * 60)
