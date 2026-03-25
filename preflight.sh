#!/usr/bin/env bash
# preflight.sh — локальный CI: lint + typecheck (soft) + tests
# Использование: bash preflight.sh
# Возвращает: 0 если всё ок, 1 если lint или tests упали.
# mypy — мягкий: выводит ошибки, но не блокирует.

set -eo pipefail
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

FAILED=0
MYPY_FAILED=0

# ── цвета ─────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; RESET='\033[0m'; BOLD='\033[1m'

pass() { echo -e "${GREEN}✓ $1${RESET}"; }
fail() { echo -e "${RED}✗ $1${RESET}"; }
soft() { echo -e "${YELLOW}⚠ $1 (soft — не блокирует)${RESET}"; }
section() { echo -e "\n${BLUE}${BOLD}── $1 ──${RESET}"; }

# ── 1. lint (ruff) ─────────────────────────────────────────────────────────────
section "lint  ruff"
if python3 -m ruff check src/ tests/; then
    pass "ruff: нарушений нет"
else
    fail "ruff: есть нарушения"
    FAILED=1
fi

# ── 2. typecheck (mypy) — МЯГКИЙ ──────────────────────────────────────────────
section "typecheck  mypy  (soft)"
if python3 -m mypy src/ 2>&1; then
    pass "mypy: ошибок нет"
else
    soft "mypy: есть ошибки типов (не блокирует)"
    MYPY_FAILED=1
fi

# ── 3. tests (pytest) ──────────────────────────────────────────────────────────
section "tests  pytest"
if python3 -m pytest -q; then
    pass "pytest: все тесты зелёные"
else
    fail "pytest: есть упавшие тесты"
    FAILED=1
fi

# ── итог ───────────────────────────────────────────────────────────────────────
echo ""
if [ $FAILED -eq 0 ] && [ $MYPY_FAILED -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ Preflight passed${RESET}"
elif [ $FAILED -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠ Preflight passed (mypy warnings)${RESET}"
else
    echo -e "${RED}${BOLD}✗ Preflight FAILED${RESET}"
fi

exit $FAILED
